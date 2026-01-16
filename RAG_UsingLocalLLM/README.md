# RAG Using Local LLM (Phase 2)

Full RAG implementation with ChromaDB vector store and Ollama LLM.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Ollama and pull required models:
   ```bash
   ollama pull llama3.2:1b
   ollama pull nomic-embed-text
   ```

3. Configure the knowledge base:
   ```bash
   cd src
   python configure.py kt_qa_guidelines.pdf
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Running Tests

1. Install pytest (already in requirements.txt):
   ```bash
   pip install pytest
   ```

2. Run all tests:
   ```bash
   pytest tests/ -v
   ```

3. Run specific test:
   ```bash
   pytest tests/test_rag.py::test_rag_answers -v
   ```

4. Run with detailed output:
   ```bash
   pytest tests/ -v -s
   ```