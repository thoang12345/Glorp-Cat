from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import (
    FastAPI,
    WebSocket, 
    WebSocketDisconnect, 
    UploadFile, 
    File,
    Form
    )

from Functions.Agent.factory import create_runtime
from Functions.Storage.database import Database
from Functions.Model.config import DATA_PATH

from Functions.Conversation.manager import ConversationManager
from pydantic import BaseModel
import uuid
from pathlib import Path
import asyncio

runtime = None
database = None
conversation_manager = None
pending_attachments = {}

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

@app.post("/api/attachments")
async def upload_attachments(
    file : UploadFile = File(...),
    conversation_id : int = Form(...),
    message_id: int = Form(...)
):
    conversation = conversation_manager.get_conversation(
        conversation_id
    )

    if conversation is None:
        return {
            "error": "Conversation not found"
        }

    messages = conversation["messages"]

    match = None
    for message in messages:
        if message_id != message["id"]:
            continue

        match = message 
        break

    if match is None:
        return {
            "error": "Message not found"
        }

    if match["role"] != "user":
        return {
            "error": "Message not from user"
        }

    conversation_media = DATA_PATH / "media" / str(conversation_id) 

    conversation_media.mkdir(
            parents=True,
            exist_ok=True
        )

    contents = await file.read()
    original = Path(file.filename)
    name = original.stem.replace(" ", "_")
    extension = original.suffix

    stored_name = f"{conversation_id}_{message_id}_{uuid.uuid7()}_{name}{extension}"
    file_path = conversation_media / stored_name

    file_path.write_bytes(contents)

    attachment_id = conversation_manager.add_attachment(
        conversation_id=conversation_id,
        message_id=match["id"],
        original_name=file.filename,
        file_path=file_path,
        content_type=file.content_type,
        size=len(contents)
    )

    if attachment_id is None:
        file_path.unlink()
        return {
            "error": "Failed to save attachment"
        }

    event = pending_attachments.get(message_id)

    if event is not None:
        event.set()

    return {
        "attached": True,
        "id": attachment_id,
    }

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
            has_attachment = data.get("has_attachment", False)
            agent = conversation_manager.get_agent(
                conversation_id
            )
            
            if agent is None:
                await websocket.send_json({
                    "type": "error",
                    "data": "Conversation not found"
                })
                continue
            
            message_id = database.add_message(
                conversation_id=conversation_id,
                role="user",
                content=message
            )

            if has_attachment:
                event = asyncio.Event()
                pending_attachments[message_id] = event

            await websocket.send_json({
                "type": "user_message_saved",
                "data": {
                    "conversation_id": conversation_id,
                    "message_id": message_id
                }
            })

            if has_attachment:
                try:
                    await asyncio.wait_for(event.wait(), timeout=30.0)

                except TimeoutError:
                    await websocket.send_json({
                        "type": "error",
                        "data": "Image upload failed (Timedout)"
                    })
                    continue

                finally:
                    pending_attachments.pop(message_id, None)

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