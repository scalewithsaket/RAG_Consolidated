import os

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DOCUMENTS_PATH = os.path.join(PROJECT_ROOT, "..", "documents")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")

# Embedding settings
EMBEDDING_MODEL = "nomic-embed-text"  # Ollama model

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K_RESULTS = 3

# LLM settings
LLM_MODEL = "llama3.2:1b"  # Faster smaller model
LLM_TEMPERATURE = 0

# ChromaDB settings
COLLECTION_NAME = "kt_documents"