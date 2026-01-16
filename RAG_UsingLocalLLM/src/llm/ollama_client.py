from langchain_ollama import ChatOllama
from config.settings import LLM_MODEL, LLM_TEMPERATURE

def get_llm():
    """Get Ollama LLM instance"""
    return ChatOllama(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )