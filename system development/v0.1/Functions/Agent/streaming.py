from Functions.model import modelName, chatBotName, stream, thinking
import ollama

def streamResponse(messages : dict, toolManager) -> dict[str : str]:
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
                print(f"\n{chatBotName} thinking:\n", end="")

            thinkingContent += chunk.message.thinking
            print(chunk.message.thinking, end="", flush=True)

        if chunk.message.content:
            if inThinking:
                print(f"\n\n{chatBotName}:\n", end="")
                inThinking = False

            responseContent += chunk.message.content
            print(chunk.message.content, end="", flush=True)

        if chunk.message.tool_calls:
            toolCalls.extend(chunk.message.tool_calls)
            print(chunk.message.tool_calls)

    return {"thinking" : thinkingContent, "content" : responseContent, "tool_calls" : toolCalls}