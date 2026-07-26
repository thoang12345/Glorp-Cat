from Functions.Model.info import ModelInfo
from Functions.Model.config import MODEL_NAME
import ollama


class ModelManager:

    def __init__(self):
        self.info = ModelInfo()

    async def load_static(self):
        model_info = ollama.show(MODEL_NAME)
        details = model_info.details

        self.info.name = MODEL_NAME
        self.info.parameter_size = details.parameter_size
        self.info.quantization = details.quantization_level
        self.info.family = details.family
        self.info.license = model_info.license

    async def load_active(self):
        running_info = ollama.ps()

        model = next(
            (m for m in running_info.models if m.name == MODEL_NAME),
            None
        )

        if model is None:
            self.info.loaded = False
            return

        self.info.loaded = True
        self.info.context_length = model.context_length
        self.info.vram_gb = model.size_vram / (1024 ** 3)
        self.info.expires_at = model.expires_at

    async def load(self):
        await self.load_static()
        await self.load_active()