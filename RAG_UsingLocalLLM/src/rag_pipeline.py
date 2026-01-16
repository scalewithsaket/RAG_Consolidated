from langchain_core.prompts import PromptTemplate
from retrieval.retriever import Retriever
from llm.ollama_client import get_llm

PROMPT_TEMPLATE = """### INSTRUCTIONS

You are a technical assistant for the QA team.
Use ONLY the provided Context below to answer the user's question.

RULES:
- Use ONLY the provided Context to answer.
- If the Context mentions a tool is prohibited or discouraged, apply that rule strictly.
- If the answer cannot be found in the context, say: "I don't have information about this in the KT documents."
- Be concise and accurate.

### CONTEXT

{context}

### QUESTION

{question}

### ANSWER
"""


class RAGPipeline:
    def __init__(self, vectorstore):
        self.retriever = Retriever(vectorstore)
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=PROMPT_TEMPLATE
        )

    def query(self, question: str):
        """Process query through RAG pipeline"""
        # Retrieve relevant documents
        docs = self.retriever.retrieve(question)

        # Format context
        context = self.retriever.format_context(docs)

        # Handle no context found
        if not context:
            return "I don't have information about this in the KT documents."

        # Generate answer
        final_prompt = self.prompt.format(context=context, question=question)
        response = self.llm.invoke(final_prompt)

        return response.content