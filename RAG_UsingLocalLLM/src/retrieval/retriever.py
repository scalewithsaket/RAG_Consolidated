from config.settings import TOP_K_RESULTS


class Retriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )

    def retrieve(self, query: str):
        """Retrieve relevant documents for query"""
        docs = self.retriever.invoke(query)
        return docs

    def format_context(self, docs):
        """Format retrieved documents into context string"""
        if not docs:
            return None
        context = "\n\n".join([doc.page_content for doc in docs])
        return context