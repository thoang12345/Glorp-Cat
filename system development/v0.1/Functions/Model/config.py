from pathlib import Path

MODEL_NAME = "nemotron-3.5-lightning-fixed:30b"
VISION_NAME = "gemma4:e2b"
CHATBOT_NAME = "GlorpCat"
RERANKER_MODEL = "BAAI/bge-reranker-base"

CHROMADB_PATH = "/home/thienan/Documents/GitHub/PaperParsing/Docling Parsing/v0.2/ChromaDB"
DATA_PATH = Path("/home/thienan/Documents/GitHub/Glorp-Cat/system development/v0.1/Data")

STREAM = True
THINKING = True
CONTEXT_WINDOW = 16384
DEFAULT_LOCATION = "Columbia, South Carolina, United States"