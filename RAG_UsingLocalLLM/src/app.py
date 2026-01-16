from ingestion.embedder import get_embeddings
from vectorstore.chroma_manager import ChromaManager
from rag_pipeline import RAGPipeline
import os
from config.settings import CHROMA_DB_PATH


def main():
    """Main query flow application"""

    # Check if vectorstore exists
    if not os.path.exists(CHROMA_DB_PATH):
        print("Error: ChromaDB not found. Please run configuration first:")
        print("  python configure.py <pdf_filename>")
        return

    print("\n=== KT Assistant (RAG with ChromaDB) ===")
    print("Loading knowledge base...")

    # Load vectorstore
    embeddings = get_embeddings()
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.load_vectorstore()

    # Initialize RAG pipeline
    rag = RAGPipeline(vectorstore)

    print("Ready! Ask questions about KT. Type 'exit', 'bye', or 'quit' to close.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() in ['exit', 'bye', 'quit']:
            print("Assistant: Goodbye!")
            break

        if query:
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'greetings']
            if query.lower() in greetings:
                print("Assistant: Hello! I'm your KT Assistant. Ask me anything about the QA automation knowledge transfer documents.\n")
            else:
                answer = rag.query(query)
                print(f"Assistant: {answer}\n")


if __name__ == "__main__":
    main()