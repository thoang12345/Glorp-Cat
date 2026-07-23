import importlib
import inspect
import pkgutil

from Functions.tool import Tool
import Functions.Tools
import json

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
                    self.register(obj())

    def schema(self):
        return [tool.schema() for tool in self.tools.values()]

    def execute(self, name, **kwargs):
        return self.tools[name].execute(**kwargs)

    def execute_calls(self, tool_calls):

        messages = []

        for call in tool_calls:

            name = call.function.name
            args = call.function.arguments

            result = self.execute(name, **args)

            messages.append({
                "role": "tool",
                "name": name,
                "content": json.dumps(result)
            })

        return messages