from pydantic import BaseModel, ConfigDict, ValidationError

class UpdateName(BaseModel):
    title : str 


#endpoint
@app.patch("/api/conversations/{conversation_id}")
async def rename_conversation(
    conversation_id: int,
    new_name: UpdateName
):
    new_name.title