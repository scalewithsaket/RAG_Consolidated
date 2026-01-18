import os
import sys
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import chunk_documents
from ingestion.embedder import get_embeddings
from vectorstore.chroma_manager import ChromaManager
from config.settings import DOCUMENTS_PATH


def configure(pdf_filename: str):
    """Run configuration flow: PDF -> Chunks -> Embeddings -> ChromaDB"""

    print("\n=== RAG Configuration Flow ===\n")

    # 1. Load PDF
    pdf_path = os.path.join(DOCUMENTS_PATH, pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    print(f"1. Loading PDF: {pdf_filename}...")
    documents = load_pdf(pdf_path)
    print(f"   [OK] Loaded {len(documents)} pages")

    # 2. Chunk documents
    print("\n2. Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"   [OK] Created {len(chunks)} chunks")

    # 3. Get embeddings
    print("\n3. Initializing embeddings model...")
    embeddings = get_embeddings()
    print("   [OK] Embeddings model ready")

    # 4. Create vectorstore
    print("\n4. Creating ChromaDB vectorstore...")
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.create_vectorstore(chunks)
    print("   [OK] Vectorstore created and persisted")

    print("\n=== Configuration Complete! ===")
    print("You can now run 'python app.py' to query the knowledge base.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python configure.py <pdf_filename>")
        print("Example: python configure.py qa_guidelines.pdf")
        sys.exit(1)

    pdf_filename = sys.argv[1]
    configure(pdf_filename)