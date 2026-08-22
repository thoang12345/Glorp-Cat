from Functions.Model.config import MODEL_NAME, STREAM, THINKING, CONTEXT_WINDOW
from Functions.utilities import t
import ollama

async def streamResponse(
    messages: dict,
    toolManager,
    stats,
    on_event=None
) -> dict[str, str]:

    async def emit(event_type, data):
        if on_event:
            await on_event({
                "type": event_type,
                "data": data
            })

    responseContent = ""
    thinkingContent = ""
    toolCalls = []

    client = ollama.AsyncClient()

    response = await client.chat(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        think=True,
        tools=toolManager.schema(),
    )

    last_chunk = None

    async for chunk in response:
        last_chunk = chunk

        if chunk.message.thinking:
            thinkingContent += chunk.message.thinking

            await emit(
                "thinking_delta",
                chunk.message.thinking
            )

        if chunk.message.content:
            responseContent += chunk.message.content

            await emit(
                "content_delta",
                chunk.message.content
            )

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

    return {
        "thinking": thinkingContent,
        "content": responseContent,
        "tool_calls": toolCalls
    }