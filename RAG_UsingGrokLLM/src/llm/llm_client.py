from langchain_ollama import ChatOllama
from config.settings import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE

def get_llm():
    """Return LLM instance based on provider"""

    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE
        )
   
