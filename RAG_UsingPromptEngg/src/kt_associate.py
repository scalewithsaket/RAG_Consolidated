from langchain_ollama import ChatOllama
from prompt_manager import get_kt_prompt_template
from file_reader import load_kt_context, load_pdf_text

class KTAssociate:
    def __init__(self, model="llama3.2", temperature=0):
        """Initialize the KT Assistant with LLM"""
        self.llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)
        self.prompt_template = get_kt_prompt_template()
    
    def ask(self, query):
        """Ask the KT assistant a question"""
        context = load_kt_context()
        final_prompt = self.prompt_template.format(context=context, question=query)
        response = self.llm.invoke(final_prompt)
        return response.content
    
    def ask_pdf_assistant(self, query):
        """Ask the KT assistant a question"""
        context = load_pdf_text()
        final_prompt = self.prompt_template.format(context=context, question=query)
        response = self.llm.invoke(final_prompt)
        return response.content    