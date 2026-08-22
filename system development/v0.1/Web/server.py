from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from Functions.Agent.factory import (
    create_runtime,
    create_agent
)

runtime = None
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global runtime
    global agent

    # Startup
    runtime = await create_runtime()
    agent = create_agent(runtime)

    yield

    # Shutdown
    await runtime.shutdown()


app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory="Web/static"),
    name="static"
)

@app.get("/")
async def root():
    return FileResponse("Web/static/index.html")

class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = await agent.chat(request.message)

    return {
        "response": response
    }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_json()
        message = data["message"]

        async def send_event(event):
            await websocket.send_json(event)

        await agent.chat(
            message,
            on_event=send_event
        )

        await websocket.send_json({
            "type": "done"
        })