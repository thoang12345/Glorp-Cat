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

SYSTEM_PROMPT = (
    f"You are {CHATBOT_NAME}. You are a helpful assistant. Have fun! :)"
    f"You have access to a vector database containing documents, handbooks, "
    f"notes, manuals, and other user-provided knowledge."
    f"When a question could reasonably be answered from these documents—even "
    f"if you have general knowledge about the topic—prefer retrieving the "
    f"relevant information first."
    f"If you do not know which collection is appropriate, call "
    f"`get_collections` before using `query_collection`."
    f"The 'handbook' database contains a 'arts_lab_graduate_handbook', that "
    f"contains information relating to graduate studies, conferences, paper "
    f"style guides and more."
)