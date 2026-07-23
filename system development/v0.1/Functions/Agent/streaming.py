from Functions.model import modelName, chatBotName, stream, thinking
import ollama

# ANSI colors
GREY = "\033[90m"
RESET = "\033[0m"

def streamResponse(messages: dict, toolManager) -> dict[str, str]:
    inThinking = False
    responseContent = ""
    thinkingContent = ""
    toolCalls = []

    response = ollama.chat(
        model=modelName,
        messages=messages,
        stream=stream,
        think=thinking,
        tools=toolManager.schema()
    )

    for chunk in response:
        if chunk.message.thinking:
            if not inThinking:
                inThinking = True
                print(f"\n{GREY}{chatBotName} thinking:\n", end="")

            thinkingContent += chunk.message.thinking
            print(chunk.message.thinking, end="", flush=True)

        if chunk.message.content:
            if inThinking:
                print(f"{RESET}\n\n{chatBotName}:\n", end="")
                inThinking = False

            responseContent += chunk.message.content
            print(chunk.message.content, end="", flush=True)

        if chunk.message.tool_calls:
            toolCalls.extend(chunk.message.tool_calls)
            print(chunk.message.tool_calls)

    # Make sure the terminal color is reset if the stream ends while thinking
    if inThinking:
        print(RESET, end="")

    return {
        "thinking": thinkingContent,
        "content": responseContent,
        "tool_calls": toolCalls
    }