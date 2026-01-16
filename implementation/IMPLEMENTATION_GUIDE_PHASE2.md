# Phase 2 Implementation Guide: RAG_UsingLocalLLM

## 🎯 Goal
Build a complete RAG system with semantic search using ChromaDB and local Ollama LLM.

---

## 📋 Prerequisites

1. **Ollama Installed** with models:
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text  # For embeddings
   ```

2. **Python 3.9+** installed

3. **Current Phase 1** working correctly

---

## 🔧 Step-by-Step Implementation

### STEP 1: Create Project Structure (5 min)

Create the following directory structure:

```
RAG_UsingLocalLLM/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── chunker.py
│   │   └── embedder.py
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── chroma_manager.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── ollama_client.py
│   ├── rag_pipeline.py
│   ├── configure.py
│   └── app.py
├── data/
│   └── chroma_db/  # Will be created automatically
├── requirements.txt
└── README.md
```

---

### STEP 2: Install Dependencies (2 min)

**requirements.txt:**
```
langchain==0.1.0
langchain-ollama==0.1.0
langchain-chroma==0.1.0
langchain-community==0.0.20
chromadb==0.4.22
pypdf==4.0.0
```

Install:
```bash
cd RAG_UsingLocalLLM
pip install -r requirements.txt
```

---

### STEP 3: Configuration Settings (5 min)

**src/config/settings.py:**
```python
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
LLM_MODEL = "llama3.2"
LLM_TEMPERATURE = 0

# ChromaDB settings
COLLECTION_NAME = "kt_documents"
```

---

### STEP 4: PDF Loader (5 min)

**src/ingestion/pdf_loader.py:**
```python
from langchain_community.document_loaders import PyPDFLoader

def load_pdf(pdf_path: str):
    """Load PDF and return documents"""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents
```

---

### STEP 5: Text Chunker (5 min)

**src/ingestion/chunker.py:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_documents(documents):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks
```

---

### STEP 6: Embedder (5 min)

**src/ingestion/embedder.py:**
```python
from langchain_ollama import OllamaEmbeddings
from config.settings import EMBEDDING_MODEL

def get_embeddings():
    """Get embedding model"""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)
```

---

### STEP 7: ChromaDB Manager (10 min)

**src/vectorstore/chroma_manager.py:**
```python
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
```

---

### STEP 8: Retriever (10 min)

**src/retrieval/retriever.py:**
```python
from config.settings import TOP_K_RESULTS

class Retriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )
    
    def retrieve(self, query: str):
        """Retrieve relevant documents for query"""
        docs = self.retriever.get_relevant_documents(query)
        return docs
    
    def format_context(self, docs):
        """Format retrieved documents into context string"""
        if not docs:
            return None
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
```

---

### STEP 9: Ollama LLM Client (5 min)

**src/llm/ollama_client.py:**
```python
from langchain_ollama import ChatOllama
from config.settings import LLM_MODEL, LLM_TEMPERATURE

def get_llm():
    """Get Ollama LLM instance"""
    return ChatOllama(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )
```

---

### STEP 10: RAG Pipeline (15 min)

**src/rag_pipeline.py:**
```python
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
```

---

### STEP 11: Configuration Script (10 min)

**src/configure.py:**
```python
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
    print(f"   ✓ Loaded {len(documents)} pages")
    
    # 2. Chunk documents
    print("\n2. Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"   ✓ Created {len(chunks)} chunks")
    
    # 3. Get embeddings
    print("\n3. Initializing embeddings model...")
    embeddings = get_embeddings()
    print("   ✓ Embeddings model ready")
    
    # 4. Create vectorstore
    print("\n4. Creating ChromaDB vectorstore...")
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.create_vectorstore(chunks)
    print("   ✓ Vectorstore created and persisted")
    
    print("\n=== Configuration Complete! ===")
    print("You can now run 'python app.py' to query the knowledge base.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python configure.py <pdf_filename>")
        print("Example: python configure.py qa_guidelines.pdf")
        sys.exit(1)
    
    pdf_filename = sys.argv[1]
    configure(pdf_filename)
```

---

### STEP 12: Query CLI Application (10 min)

**src/app.py:**
```python
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
            answer = rag.query(query)
            print(f"Assistant: {answer}\n")

if __name__ == "__main__":
    main()
```

---

### STEP 13: README Documentation (5 min)

**README.md:**
```markdown
# RAG Using Local LLM (Phase 2)

Full RAG implementation with ChromaDB vector store and Ollama LLM.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running with required models:
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

## Usage

### Configuration Flow (One-time)
```bash
cd src
python configure.py qa_guidelines.pdf
```

### Query Flow (Interactive)
```bash
cd src
python app.py
```

## Architecture

- **Ingestion:** PDF → Chunks → Embeddings → ChromaDB
- **Retrieval:** Query → Semantic Search → Top-K Chunks
- **Generation:** Context + Query → LLM → Answer
```

---

## ✅ Testing Your Implementation

### Test Configuration Flow:
```bash
cd RAG_UsingLocalLLM/src
python configure.py qa_guidelines.pdf
```

Expected output:
```
=== RAG Configuration Flow ===

1. Loading PDF: qa_guidelines.pdf...
   ✓ Loaded 2 pages

2. Chunking documents...
   ✓ Created 15 chunks

3. Initializing embeddings model...
   ✓ Embeddings model ready

4. Creating ChromaDB vectorstore...
   ✓ Vectorstore created and persisted

=== Configuration Complete! ===
```

### Test Query Flow:
```bash
python app.py
```

Try these queries:
1. "What is the framework for testing?"
2. "Can we use Selenium?"
3. "What is the reporting tool?"
4. "How do I set up a React project?" (should say no info)

---

## 🎓 Key Learnings

1. **Chunking Strategy:** Balance between context and precision
2. **Embedding Quality:** Better embeddings = better retrieval
3. **Top-K Selection:** Too few = miss context, too many = noise
4. **Prompt Engineering:** Still crucial even with RAG
5. **Vector Search:** Semantic similarity vs keyword matching

---

## 🚀 Next: Phase 3 (AWS Bedrock)

After validating Phase 2, we'll migrate to AWS Bedrock with:
- Amazon Bedrock LLM (Claude/Titan)
- Amazon Titan Embeddings
- Optional: Amazon OpenSearch for vector store
- Production deployment patterns
