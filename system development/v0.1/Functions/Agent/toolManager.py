import importlib
import inspect
import pkgutil
import time
from Functions.tool import Tool
import Functions.Tools
import json

BLUE_GREY = "\033[38;2;120;140;170m"
RESET = "\033[0m"

class ToolManager:

    def __init__(self):
        self.tools = {}
        self.load_tools()

    def __iter__(self):
        return iter(self.tools.values())

    def register(self, tool):
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered.")

        self.tools[tool.name] = tool

    def load_tools(self):
        for _, module_name, _ in pkgutil.iter_modules(
            Functions.Tools.__path__
        ):

            module = importlib.import_module(
                f"Functions.Tools.{module_name}"
            )

            for _, obj in inspect.getmembers(module):

                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Tool)
                    and not inspect.isabstract(obj)
                ):
                    signature = inspect.signature(obj.__init__)

                    required_parameters = []
                    for parameter in signature.parameters.values():
                        if parameter.name == "self":
                            continue

                        if parameter.default == inspect.Parameter.empty:
                            required_parameters.append(parameter)
                            
                    if required_parameters:
                        continue
                                            
                    self.register(obj())

    def schema(self):
        return [tool.schema() for tool in self.tools.values()]

    async def execute(
        self,
        stats,
        name,
        on_event=None,
        **kwargs
    ):
        async def emit(event_type, data):
            if on_event:
                await on_event({
                    "type": event_type,
                    "data": data
                })

        await emit(
            "tool_started",
            {
                "name": name,
                "arguments": kwargs
            }
        )

        start = time.perf_counter()

        result = await self.tools[name].execute(**kwargs)

        elapsed = time.perf_counter() - start

        stats.add_tool(name, elapsed)

        await emit(
            "tool_finished",
            {
                "name": name,
                "elapsed": elapsed
            }
        )

        return result

    async def execute_calls(
        self,
        stats,
        tool_calls,
        on_event=None
    ):
        messages = []

        for call in tool_calls:
            name = call.function.name
            args = call.function.arguments

            result = await self.execute(
                stats,
                name,
                on_event=on_event,
                **args
            )

            messages.append({
                "role": "tool",
                "name": name,
                "content": json.dumps(result)
            })

        return messages