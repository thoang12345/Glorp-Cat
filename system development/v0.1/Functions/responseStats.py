import time

TAB = "  "
TOOL_WIDTH = 30
GREY = "\033[38;2;170;170;170m"
RESET = "\033[0m"


class ResponseStats:

    def __init__(self):
        self.start_time = time.perf_counter()
        self.total_time = 0.0
        self.tool_times = []

    def add_tool(self, name, elapsed):
        self.tool_times.append({
            "name": name,
            "elapsed": elapsed
        })

    def set_llm(
        self,
        prompt_tokens,
        generated_tokens,
        prompt_duration,
        generation_duration,
        load_duration,
        total_duration,
    ):

        self.prompt_tokens = prompt_tokens
        self.generated_tokens = generated_tokens

        self.load_time = load_duration / 1_000_000_000
        self.model_time = total_duration / 1_000_000_000

        self.prompt_speed = (
            prompt_tokens /
            (prompt_duration / 1_000_000_000)
        )

        self.generation_speed = (
            generated_tokens /
            (generation_duration / 1_000_000_000)
        )

    def finish(self):
        self.total_time = time.perf_counter() - self.start_time

    def set_model(self, model_info):
        self.model = model_info

    def stat(self, label, value):
        print(f"{TAB}{label:<{TOOL_WIDTH}}{value}")

    def print_stats(self):
        context_usage = (
                    self.prompt_tokens /
                    self.model.context_length
                ) * 100
        
        print(f"{GREY}\n\n" + "=" * 50)
        print("📊 Response Statistics:")

        print("\n🧠 Model:")
        self.stat(
            "Context",
            f"{self.prompt_tokens:,} / "
            f"{self.model.context_length:,} "
            f"({context_usage:.1f}%)"
        )
        self.stat("Prompt Tokens", f"{self.prompt_tokens:,}")
        self.stat("Generated Tokens", f"{self.generated_tokens:,}")
        self.stat("Prompt Speed", f"{self.prompt_speed:.2f} tok/s")
        self.stat("Generation Speed", f"{self.generation_speed:.2f} tok/s")
        self.stat("Load Time", f"{self.load_time:.2f} s")

        print("\n🔧 Tools:")
        if self.tool_times:
            for tool in self.tool_times:
                self.stat(
                    tool["name"],
                    f"{tool['elapsed']:.2f} s"
                )
        else:
            self.stat("None", "")

        print("\n⏱ Response:")
        self.stat("Total", f"{self.total_time:.2f} s")

        print("=" * 50 + RESET)