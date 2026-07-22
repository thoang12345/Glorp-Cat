import logging
import torch
import time

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     datefmt='%Y-%m-%d %I:%M:%S %p')
logger = logging.getLogger(__name__)

def giveGPUstatus() -> None:
        logger.info("=" * 50)
        logger.info(f"torch: {torch.__version__}")
        logger.info(f"hip: {torch.version.hip}")
        logger.info(f"cuda available: {torch.cuda.is_available()}")

        if not torch.cuda.is_available():
                raise SystemExit("ROCm GPU is not visible to PyTorch")

        device = "cuda"
        logger.info(f"device: {torch.cuda.get_device_name(0)}")

        x = torch.randn((4096, 4096), device=device, dtype=torch.float16)
        y = torch.randn((4096, 4096), device=device, dtype=torch.float16)

        torch.cuda.synchronize()
        start = time.time()

        for _ in range(20):
                z = x @ y

        torch.cuda.synchronize()
        logger.info(f"seconds: {round(time.time() - start, 3)}")
        logger.info(f"ok: {z.shape}, {z.dtype}")
        logger.info(f"{'=' * 50}\n")

def initializeDoclingChunker() -> list[HybridChunker, HuggingFaceTokenizer]:
        EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
        MAX_TOKENS = 400

        logger.info("=" * 50)
        logger.info(f"Initializing Docling Chunker with model: {EMBED_MODEL_ID} and max tokens: {MAX_TOKENS}")
        tokenizer = HuggingFaceTokenizer(
                tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
                max_tokens = MAX_TOKENS
        )

        logger.info(f"Initializing HybridChunker with tokenizer and merge_peers set to True")
        logger.info("=" * 50 + "\n")
        chunker = HybridChunker(
                tokenizer=tokenizer,
                merge_peers = True
        )

        chunkingTools = [chunker, tokenizer]
        return chunkingTools