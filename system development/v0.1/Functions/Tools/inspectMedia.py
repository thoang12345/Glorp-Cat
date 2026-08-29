from Functions.tool import Tool

class InspectMedia(Tool):
    def __init__(self, conversation_id, conversation_manager, media_inspector):
        super().__init__(
            "inspect_media",
            "Inspects an image or audio attachment from the current conversation "
            "and answers a question about its contents. Use this tool when you "
            "need to see, read, interpret, or re-examine attached media."
        )

        self.conversation_id = conversation_id
        self.conversation_manager = conversation_manager
        self.media_inspector = media_inspector

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "attachment_id": {
                            "type": "integer",
                            "description": (
                                "ID of the image or audio attachment to inspect. "
                                "Use the attachment ID associated with the relevant "
                                "media in the current conversation."
                            )
                        },
                        "question": {
                            "type": "string",
                            "description": (
                                "Specific question to ask about the attachment. "
                                "Ask for the visual or audio information needed "
                                "to answer the user's request."
                            )
                        }
                    },
                    "required": ["attachment_id", "question"]
                }
            }
        }

    async def execute(self, attachment_id, question):
        attachment = self.conversation_manager.get_attachment(
            self.conversation_id,
            attachment_id
        )

        if attachment is None:
            return {
                "error": "no attachment found",
                "attachment_id": attachment_id
            }
        
        content_type = attachment["content_type"]
        if content_type.startswith("image/"):
            file_path = attachment["file_path"]

            response = await self.media_inspector.inspect_image(file_path, question)
        else:
            return {
                "error": "invalid file type",
                "content_type": content_type
            }

        return {
            "response": response
        }