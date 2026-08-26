import ollama

from Functions.Model.config import VISION_NAME



class MediaInspector:
    def __init__(self):
        self.client = ollama.AsyncClient()
        self.model = VISION_NAME

    async def inspect_image(self, file_path, question):
        response = await self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "images": [file_path],
                }
            ],
        )

        return response.message.content