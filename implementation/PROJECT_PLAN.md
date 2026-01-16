# RAG Project Evolution Plan

## 🎯 Project Goal
Build a Knowledge Transfer (KT) RAG application that evolves from simple prompt engineering to full-fledged local RAG, and finally to AWS Bedrock cloud deployment.

---

## 📊 Current State Analysis

### Existing Implementation (RAG_UsingPromptEngg)
- **Status:** ✅ Complete
- **Components:**
  - `kt_assistant.py`: LLM wrapper using Ollama
  - `prompt_manager.py`: Loads prompt templates
  - `file_reader.py`: Reads KT documents (MD/PDF)
  - `app.py`: CLI interface
- **Approach:** Entire document loaded into context
- **Limitation:** No semantic search, context window limits

---

## 🏗️ Proposed Project Structure

```
kt_project_prompt_engineering/
│
├── documents/                          # Knowledge base documents
│   ├── kt_manual.md
│   └── qa_guidelines.pdf
│
├── prompts/                            # Prompt templates
│   └── kt_assistant_prompt.md
│
├── RAG_UsingPromptEngg/               # Phase 1: Current implementation
│   ├── src/
│   │   ├── kt_assistant.py
│   │   ├── prompt_manager.py
│   │   ├── file_reader.py
│   │   └── app.py
│   ├── requirements.txt
│   └── README.md
│
├── RAG_UsingLocalLLM/                 # Phase 2: Full RAG with ChromaDB
│   ├── backend/
│   │   ├── src/
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   └── settings.py            # Configuration settings
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdf_loader.py          # Load PDF documents
│   │   │   │   ├── chunker.py             # Text chunking strategies
│   │   │   │   └── embedder.py            # Generate embeddings
│   │   │   ├── vectorstore/
│   │   │   │   ├── __init__.py
│   │   │   │   └── chroma_manager.py      # ChromaDB operations
│   │   │   ├── retrieval/
│   │   │   │   ├── __init__.py
│   │   │   │   └── retriever.py           # Query and retrieve context
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   └── ollama_client.py       # Ollama LLM wrapper
│   │   │   ├── rag_pipeline.py            # Main RAG orchestration
│   │   │   ├── api.py                     # FastAPI endpoints
│   │   │   └── configure.py               # Configuration flow script
│   │   ├── data/
│   │   │   └── chroma_db/                 # ChromaDB storage (gitignored)
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   └── ChatContainer.jsx
│   │   │   ├── services/
│   │   │   │   └── api.js
│   │   │   ├── App.jsx
│   │   │   └── main.jsx
│   │   ├── package.json
│   │   └── README.md
│   ├── app.py                         # CLI version (optional)
│   └── README.md
│
├── RAG_UsingAWSBedrock/               # Phase 3: AWS Cloud deployment
│   ├── backend/
│   │   ├── src/
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   └── aws_settings.py        # AWS configuration
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdf_loader.py
│   │   │   │   ├── chunker.py
│   │   │   │   └── bedrock_embedder.py    # AWS Bedrock embeddings
│   │   │   ├── vectorstore/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── opensearch_manager.py  # Amazon OpenSearch (optional)
│   │   │   │   └── chroma_manager.py      # Or continue with ChromaDB
│   │   │   ├── retrieval/
│   │   │   │   ├── __init__.py
│   │   │   │   └── retriever.py
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   └── bedrock_client.py      # AWS Bedrock LLM
│   │   │   ├── rag_pipeline.py
│   │   │   ├── api.py                     # FastAPI endpoints
│   │   │   └── configure.py
│   │   ├── infrastructure/                # IaC (optional)
│   │   │   └── cloudformation.yaml
│   │   └── requirements.txt
│   ├── frontend/                          # Same React UI as Phase 2
│   │   ├── src/
│   │   ├── package.json
│   │   └── README.md
│   └── README.md
│
├── shared/                            # Shared utilities across phases
│   ├── __init__.py
│   └── prompt_templates.py
│
├── tests/                             # Unit and integration tests
│   ├── test_prompt_engg/
│   ├── test_local_llm/
│   └── test_bedrock/
│
├── .gitignore
├── PROJECT_PLAN.md                    # This file
└── README.md                          # Main project README
```

---

## 🔄 Phase 2: RAG_UsingLocalLLM - Detailed Flow

### Configuration Flow (One-time setup)
```
PDF Document
    ↓
1. Load PDF (PyPDFLoader)
    ↓
2. Chunk Text (RecursiveCharacterTextSplitter)
   - chunk_size: 500-1000 tokens
   - chunk_overlap: 50-100 tokens
    ↓
3. Generate Embeddings (OllamaEmbeddings)
   - Model: nomic-embed-text or mxbai-embed-large
    ↓
4. Store in ChromaDB
   - Collection: "kt_documents"
   - Persist to disk
```

### Query Flow (Runtime)
```
User Query: "What is the framework for testing?"
    ↓
1. Generate Query Embedding (OllamaEmbeddings)
    ↓
2. Semantic Search in ChromaDB
   - Retrieve top-k similar chunks (k=3-5)
    ↓
3. Build Context from Retrieved Chunks
    ↓
4. Format Prompt Template
   - System instructions
   - Retrieved context
   - User query
    ↓
5. Send to Ollama LLM (llama3.2 or qwen2.5)
    ↓
6. Return Answer
   - If context found: Answer based on context
   - If no context: "I don't have information about this"
```

---

## 🛠️ Phase 2 Implementation Steps

### Step 1: Setup ChromaDB & Embeddings
- Install dependencies: `chromadb`, `langchain-chroma`, `sentence-transformers`
- Choose embedding model: `nomic-embed-text` (Ollama) or `all-MiniLM-L6-v2`
- Initialize ChromaDB persistent client

### Step 2: Build Ingestion Pipeline
- Load PDF using `PyPDFLoader`
- Chunk text using `RecursiveCharacterTextSplitter`
- Generate embeddings for each chunk
- Store in ChromaDB with metadata (page number, source)

### Step 3: Build Retrieval Pipeline
- Accept user query
- Generate query embedding
- Perform similarity search (cosine similarity)
- Retrieve top-k relevant chunks
- Combine chunks into context

### Step 4: Build RAG Pipeline
- Integrate retriever with LLM
- Use prompt template with retrieved context
- Handle "no context found" scenario
- Return formatted response

### Step 5: CLI Application
- Configuration mode: `python configure.py --pdf documents/qa_guidelines.pdf`
- Query mode: `python app.py` (interactive CLI)

---

## 🔄 Phase 3: RAG_UsingAWSBedrock - Migration Plan

### Changes from Phase 2
1. **LLM:** Ollama → AWS Bedrock (Claude 3 Sonnet/Haiku or Titan)
2. **Embeddings:** Ollama → Amazon Titan Embeddings
3. **Vector Store:** ChromaDB → Amazon OpenSearch (optional) or keep ChromaDB
4. **Authentication:** AWS credentials via boto3
5. **Deployment:** Local → AWS Lambda/ECS/EC2

### AWS Services Used
- **Amazon Bedrock:** LLM inference (Claude, Titan, Llama)
- **Amazon Titan Embeddings:** Generate embeddings
- **Amazon OpenSearch:** Vector database (alternative to ChromaDB)
- **AWS Lambda:** Serverless query endpoint (optional)
- **Amazon S3:** Store PDF documents
- **AWS Secrets Manager:** Store API keys/credentials

---

## 📦 Dependencies by Phase

### Phase 1 (Current)
```
langchain
langchain-ollama
langchain-community
pypdf
```

### Phase 2 (Local RAG)
```
# Backend
langchain
langchain-ollama
langchain-chroma
langchain-community
chromadb
pypdf
fastapi
uvicorn[standard]
pydantic

# Frontend
react
react-dom
axios
tailwindcss
```

### Phase 3 (AWS Bedrock)
```
# Backend
langchain
langchain-aws
langchain-community
boto3
chromadb  # Or remove if using OpenSearch
pypdf
opensearch-py  # If using OpenSearch
fastapi
uvicorn[standard]
pydantic

# Frontend (same as Phase 2)
react
react-dom
axios
tailwindcss
```

---

## 🎓 Learning Objectives

### Phase 2 Focus
- ✅ Document chunking strategies
- ✅ Embedding generation and vector representations
- ✅ Vector similarity search
- ✅ RAG pipeline orchestration
- ✅ Context retrieval and ranking

### Phase 3 Focus
- ✅ AWS Bedrock API integration
- ✅ Cloud-based embeddings
- ✅ Managed vector databases
- ✅ AWS authentication and security
- ✅ Production deployment patterns

---

## 🚀 Next Steps

1. **Reorganize Current Code** → Move to `RAG_UsingPromptEngg/`
2. **Create Phase 2 Structure** → Setup `RAG_UsingLocalLLM/` folders
3. **Implement Configuration Flow** → PDF → Chunks → Embeddings → ChromaDB
4. **Implement Query Flow** → Query → Retrieve → Generate Answer
5. **Build FastAPI Backend** → REST API endpoints
6. **Build React Frontend** → Clean, minimalistic chat UI
7. **Test & Validate** → Compare with Phase 1 results
8. **Document Learnings** → Update README with insights
9. **Plan Phase 3** → AWS Bedrock migration strategy

---

## 📝 Success Criteria

### Phase 2
- ✅ Successfully chunk and embed PDF document
- ✅ Store embeddings in ChromaDB
- ✅ Retrieve relevant context for queries
- ✅ Generate accurate answers using retrieved context
- ✅ Handle "no context found" gracefully
- ✅ FastAPI backend running smoothly
- ✅ React UI with clean, minimalistic design
- ✅ Real-time chat interaction working

### Phase 3
- ✅ Successfully migrate to AWS Bedrock
- ✅ Use AWS-managed embeddings
- ✅ Deploy as serverless or containerized app
- ✅ Implement proper error handling and logging
- ✅ Cost-effective and scalable
- ✅ Same React UI working with Bedrock backend

---

## 🔗 Resources

- **LangChain Docs:** https://python.langchain.com/docs/
- **ChromaDB Docs:** https://docs.trychroma.com/
- **Ollama Models:** https://ollama.com/library
- **AWS Bedrock:** https://aws.amazon.com/bedrock/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Tailwind CSS:** https://tailwindcss.com/
- **Databricks GenAI Course:** Your completed course materials

---

**Author:** Your Name  
**Last Updated:** 2024  
**Version:** 1.0
