# RAG Architecture Overview

## 🏗️ System Architecture Evolution

### Phase 1: Simple Prompt Engineering
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG_UsingPromptEngg                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   User   │─────▶│  CLI (app.py)│─────▶│ KTAssistant  │ │
│  └──────────┘      └──────────────┘      └──────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│                                          ┌────────────────┐ │
│                                          │ PromptManager  │ │
│                                          └────────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│                                          ┌────────────────┐ │
│                                          │  FileReader    │ │
│                                          │ (Load full KT) │ │
│                                          └────────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│                                          ┌────────────────┐ │
│                                          │  Ollama LLM    │ │
│                                          │ (qwen2.5:1.5b) │ │
│                                          └────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Limitations:
❌ No semantic search
❌ Limited by context window
❌ Loads entire document every time
```

---

### Phase 2: Full RAG with Vector Store
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAG_UsingLocalLLM                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CONFIGURATION FLOW (One-time):                                        │
│  ┌──────────┐                                                          │
│  │ PDF File │                                                          │
│  └────┬─────┘                                                          │
│       │                                                                │
│       ▼                                                                │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐        │
│  │  PDFLoader   │─────▶│   Chunker    │─────▶│  Embedder    │        │
│  │ (PyPDF)      │      │ (500 tokens) │      │ (nomic-embed)│        │
│  └──────────────┘      └──────────────┘      └──────┬───────┘        │
│                                                      │                │
│                                                      ▼                │
│                                             ┌────────────────┐        │
│                                             │   ChromaDB     │        │
│                                             │ (Vector Store) │        │
│                                             └────────────────┘        │
│                                                                       │
│  ─────────────────────────────────────────────────────────────────   │
│                                                                       │
│  QUERY FLOW (Runtime):                                               │
│  ┌──────────┐                                                        │
│  │   User   │                                                        │
│  │  Query   │                                                        │
│  └────┬─────┘                                                        │
│       │                                                              │
│       ▼                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │
│  │  Embedder    │─────▶│  ChromaDB    │─────▶│  Retriever   │      │
│  │ (Embed query)│      │ (Search top-K)│      │ (Format ctx) │      │
│  └──────────────┘      └──────────────┘      └──────┬───────┘      │
│                                                      │              │
│                                                      ▼              │
│                                             ┌────────────────┐      │
│                                             │ RAG Pipeline   │      │
│                                             │ (Prompt + LLM) │      │
│                                             └────────┬───────┘      │
│                                                      │              │
│                                                      ▼              │
│                                             ┌────────────────┐      │
│                                             │  Ollama LLM    │      │
│                                             │  (llama3.2)    │      │
│                                             └────────┬───────┘      │
│                                                      │              │
│                                                      ▼              │
│                                             ┌────────────────┐      │
│                                             │    Answer      │      │
│                                             └────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Advantages:
✅ Semantic search
✅ Handles large documents
✅ Efficient retrieval
✅ Scalable
```

---

### Phase 3: AWS Bedrock Cloud RAG
```
┌─────────────────────────────────────────────────────────────────────────┐
│                       RAG_UsingAWSBedrock                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐        │
│  │                      AWS Cloud                             │        │
│  │                                                            │        │
│  │  ┌──────────┐      ┌──────────────┐      ┌─────────────┐ │        │
│  │  │ S3 Bucket│─────▶│  Lambda/ECS  │─────▶│   Bedrock   │ │        │
│  │  │ (PDFs)   │      │ (Processing) │      │    LLM      │ │        │
│  │  └──────────┘      └──────────────┘      │ (Claude 3)  │ │        │
│  │                                           └─────────────┘ │        │
│  │                                                            │        │
│  │  ┌──────────────┐      ┌──────────────┐                  │        │
│  │  │ Titan Embed  │─────▶│  OpenSearch  │                  │        │
│  │  │ (Embeddings) │      │ (Vector DB)  │                  │        │
│  │  └──────────────┘      └──────────────┘                  │        │
│  │                                                            │        │
│  │  ┌──────────────┐      ┌──────────────┐                  │        │
│  │  │   Secrets    │      │  CloudWatch  │                  │        │
│  │  │   Manager    │      │  (Logging)   │                  │        │
│  │  └──────────────┘      └──────────────┘                  │        │
│  │                                                            │        │
│  └────────────────────────────────────────────────────────────┘        │
│                                                                         │
│  ┌──────────┐                                                          │
│  │   User   │──────▶ API Gateway ──────▶ Lambda ──────▶ Response      │
│  └──────────┘                                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Advantages:
✅ Production-ready
✅ Auto-scaling
✅ Managed services
✅ Enterprise security
```

---

## 📦 Component Details

### Phase 2 Components (RAG_UsingLocalLLM)

#### 1. Configuration Module (`src/config/`)
```
settings.py
├── Project paths
├── Embedding model config
├── Chunking parameters
├── Retrieval settings
└── LLM configuration
```

#### 2. Ingestion Module (`src/ingestion/`)
```
pdf_loader.py    → Load PDF documents
chunker.py       → Split text into chunks
embedder.py      → Generate vector embeddings
```

#### 3. Vector Store Module (`src/vectorstore/`)
```
chroma_manager.py
├── create_vectorstore()  → Initialize and populate
├── load_vectorstore()    → Load existing DB
└── search()              → Similarity search
```

#### 4. Retrieval Module (`src/retrieval/`)
```
retriever.py
├── retrieve()           → Get relevant docs
├── format_context()     → Combine chunks
└── rank_results()       → Optional reranking
```

#### 5. LLM Module (`src/llm/`)
```
ollama_client.py
├── get_llm()           → Initialize Ollama
└── generate()          → Generate response
```

#### 6. RAG Pipeline (`src/rag_pipeline.py`)
```
RAGPipeline
├── __init__()          → Setup components
├── query()             → Main query method
├── _retrieve()         → Get context
└── _generate()         → Generate answer
```

---

## 🔄 Data Flow Diagrams

### Configuration Flow (Phase 2)
```
Input: qa_guidelines.pdf (2 pages)
│
├─▶ Load PDF
│   Output: [Page1, Page2]
│
├─▶ Chunk Text
│   Output: 15 chunks (500 tokens each)
│   Example chunk:
│   "## 1. Technical Stack
│    - Framework: Playwright (Version 1.40+)
│    - Language: TypeScript..."
│
├─▶ Generate Embeddings
│   Output: 15 vectors (768 dimensions each)
│   Example: [0.234, -0.123, 0.456, ...]
│
└─▶ Store in ChromaDB
    Output: Collection "kt_documents" with 15 entries
    Metadata: {page: 1, source: "qa_guidelines.pdf"}
```

### Query Flow (Phase 2)
```
Input: "What is the framework for testing?"
│
├─▶ Embed Query
│   Output: [0.189, -0.234, 0.567, ...]
│
├─▶ Semantic Search
│   ChromaDB finds top-3 similar chunks:
│   1. Chunk 2 (similarity: 0.89)
│   2. Chunk 5 (similarity: 0.76)
│   3. Chunk 1 (similarity: 0.71)
│
├─▶ Build Context
│   Combine chunks:
│   "## 1. Technical Stack
│    - Framework: Playwright (Version 1.40+)
│    - Language: TypeScript
│    - Runtime: NodeJS 20.x..."
│
├─▶ Format Prompt
│   Template + Context + Query
│
├─▶ Send to LLM
│   Ollama (llama3.2)
│
└─▶ Generate Answer
    Output: "The framework used for testing is 
             Playwright (Version 1.40+)."
```

---

## 🎯 Key Differences

| Aspect | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Context Source** | Full document | Top-K chunks | Top-K chunks |
| **Search Method** | None | Semantic | Semantic |
| **Storage** | File system | ChromaDB | OpenSearch/ChromaDB |
| **Embeddings** | None | Local (Ollama) | Cloud (Titan) |
| **LLM** | Local (Ollama) | Local (Ollama) | Cloud (Bedrock) |
| **Deployment** | Local script | Local script | Cloud service |
| **Scalability** | Low | Medium | High |
| **Cost** | $0 | $0 | $20-50/month |

---

## 🧮 Vector Similarity Example

### How Semantic Search Works

**Query:** "What is the framework?"
**Query Embedding:** [0.2, 0.8, 0.1, ...]

**Chunk 1:** "Framework: Playwright"
**Chunk 1 Embedding:** [0.3, 0.7, 0.2, ...]
**Similarity Score:** 0.89 ✅ (High - Retrieved!)

**Chunk 2:** "Reports stored in S3"
**Chunk 2 Embedding:** [0.1, 0.2, 0.9, ...]
**Similarity Score:** 0.23 ❌ (Low - Not retrieved)

**Result:** Chunk 1 is semantically similar to query, so it's retrieved!

---

## 📊 Performance Metrics

### Phase 2 Expected Performance

**Configuration (One-time):**
- PDF Loading: ~1 second
- Chunking: ~2 seconds
- Embedding Generation: ~10-15 seconds (15 chunks)
- ChromaDB Storage: ~1 second
- **Total:** ~15-20 seconds

**Query (Per request):**
- Query Embedding: ~0.5 seconds
- Vector Search: ~0.1 seconds
- Context Formatting: ~0.1 seconds
- LLM Generation: ~2-3 seconds
- **Total:** ~3-4 seconds

---

## 🎓 Concepts to Master

### Phase 2 Learning Goals

1. **Text Chunking**
   - Understand chunk size trade-offs
   - Learn overlap importance
   - Experiment with different strategies

2. **Embeddings**
   - Vector representation of text
   - Semantic similarity concept
   - Embedding model selection

3. **Vector Databases**
   - How ChromaDB stores vectors
   - Similarity search algorithms
   - Indexing strategies

4. **RAG Pipeline**
   - Retrieval-Augmented Generation
   - Context window management
   - Prompt engineering with context

---

This architecture overview should help you visualize the entire system! 🚀
