from Functions.Model.config import MODEL_NAME, CHATBOT_NAME, STREAM, THINKING, CONTEXT_WINDOW
from Functions.utilities import t
import ollama

# ANSI colors
GREY = "\033[90m"
RESET = "\033[0m"

async def streamResponse(messages: dict, toolManager, stats) -> dict[str, str]:
    inThinking = False
    responseContent = ""
    thinkingContent = ""
    toolCalls = []

    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        think=True,
        tools=toolManager.schema(),
    )

    last_chunk = None

    for chunk in response:
        last_chunk = chunk
        if chunk.message.thinking:
            if not inThinking:
                inThinking = True
                print(f"\n{GREY}{CHATBOT_NAME} thinking:\n", end="")

            thinkingContent += chunk.message.thinking
            print(chunk.message.thinking, end="", flush=True)

        if chunk.message.content:
            if inThinking:
                print(f"{RESET}\n\n{CHATBOT_NAME}:\n", end="")
                inThinking = False

            responseContent += chunk.message.content
            print(chunk.message.content, end="", flush=True)

        if chunk.message.tool_calls:
            toolCalls.extend(chunk.message.tool_calls)

    stats.set_llm(
        prompt_tokens=last_chunk.prompt_eval_count,
        generated_tokens=last_chunk.eval_count,
        prompt_duration=last_chunk.prompt_eval_duration,
        generation_duration=last_chunk.eval_duration,
        load_duration=last_chunk.load_duration,
        total_duration=last_chunk.total_duration
    )

    # Make sure the terminal color is reset if the stream ends while thinking
    if inThinking:
        print(RESET, end="")

    return {
        "thinking": thinkingContent,
        "content": responseContent,
        "tool_calls": toolCalls
    }