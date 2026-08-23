from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from Functions.Agent.factory import (
    create_runtime,
    create_agent
)
from Functions.Storage.database import Database
from Functions.Conversation.manager import ConversationManager
from pydantic import BaseModel

runtime = None
database = None
conversation_manager = None


class UpdateName(BaseModel):
    title : str 


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runtime
    global database
    global conversation_manager

    runtime = await create_runtime()

    database = Database()

    conversation_manager = ConversationManager(
        runtime=runtime,
        database=database
    )

    yield

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

@app.get("/api/conversations")
async def get_conversations():
    return conversation_manager.get_conversations()

@app.post("/api/conversations")
async def create_conversation():
    conversation_id = conversation_manager.create()

    return {
        "id": conversation_id
    }

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    conversation = conversation_manager.get_conversation(
        conversation_id
    )

    if conversation is None:
        return {
            "error": "Conversation not found"
        }

    return conversation

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.patch("/api/conversations/{conversation_id}")
async def rename_conversation(
        conversation_id: int,
        new_name: UpdateName
    ):
    renamed = conversation_manager.rename(
        conversation_id, new_name.title
    )

    if not renamed:
        return {
            "error": "Conversation not found"
        }

    return {
        "renamed": True,
        "id": conversation_id,
        "title": renamed
    }

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    deleted = conversation_manager.delete(
        conversation_id
    )

    if not deleted:
        return {
            "error": "Conversation not found"
        }

    return {
        "deleted": True,
        "id": conversation_id
    }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            conversation_id = data["conversation_id"]
            message = data["message"]

            agent = conversation_manager.get_agent(
                conversation_id
            )

            if agent is None:
                await websocket.send_json({
                    "type": "error",
                    "data": "Conversation not found"
                })
                continue

            database.add_message(
                conversation_id=conversation_id,
                role="user",
                content=message
            )

            title = conversation_manager.set_title_from_message(
                conversation_id,
                message
            )

            await websocket.send_json({
                "type": "conversation_title",
                "data": {
                    "conversation_id": conversation_id,
                    "title": title
                }
            })

            async def send_event(event):
                await websocket.send_json(event)

            assistant = await agent.chat(
                message,
                on_event=send_event
            )

            database.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant["content"],
                thinking=assistant["thinking"]
            )

            await websocket.send_json({
                "type": "done"
            })

    except WebSocketDisconnect:
        pass