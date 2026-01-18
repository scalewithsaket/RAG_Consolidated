from langchain_ollama import OllamaEmbeddings
from config.settings import EMBEDDING_MODEL

def get_embeddings():
    """Get embedding model"""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)