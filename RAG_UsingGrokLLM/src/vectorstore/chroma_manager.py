from langchain_chroma import Chroma
from config.settings import CHROMA_DB_PATH, COLLECTION_NAME


class ChromaManager:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vectorstore = None

    def create_vectorstore(self, chunks):
        """Create and persist vectorstore"""
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME
        )
        return self.vectorstore

    def load_vectorstore(self):
        """Load existing vectorstore"""
        self.vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME
        )
        return self.vectorstore