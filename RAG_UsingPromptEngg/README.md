# KT Project: RAG Evolution Journey

A comprehensive project demonstrating the evolution from simple prompt engineering to production-ready RAG (Retrieval-Augmented Generation) applications.

## 🎯 Project Overview

This project showcases three progressive implementations of a Knowledge Transfer (KT) assistant:

1. **Phase 1:** RAG_UsingPromptEngg - Simple prompt engineering with full context injection
2. **Phase 2:** RAG_UsingLocalLLM - Full RAG with ChromaDB vector store and semantic search
3. **Phase 3:** RAG_UsingAWSBedrock - Cloud-native RAG using AWS Bedrock

## 📊 Current Status

- ✅ **Phase 1:** Complete - Working CLI with Ollama LLM
- 🚀 **Phase 2:** Ready to implement - Full documentation provided
- ☁️ **Phase 3:** Planned - AWS Bedrock migration

## 📚 Documentation

This project includes comprehensive documentation:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** | High-level overview and quick reference | 5 min |
| **[QUICK_START.md](QUICK_START.md)** | Immediate next steps and setup guide | 10 min |
| **[PROJECT_PLAN.md](PROJECT_PLAN.md)** | Complete 3-phase roadmap and strategy | 15 min |
| **[IMPLEMENTATION_GUIDE_PHASE2.md](IMPLEMENTATION_GUIDE_PHASE2.md)** | Step-by-step Phase 2 implementation | 20 min |
| **[PHASE_COMPARISON.md](PHASE_COMPARISON.md)** | Detailed comparison of all phases | 15 min |
| **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** | System architecture and data flows | 15 min |

**Start here:** 👉 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

## 🏗️ Project Structure

```
kt_project_prompt_engineering/
│
├── documents/                    # Shared knowledge base
│   ├── kt_manual.md             # QA automation KT document
│   └── qa_guidelines.pdf        # PDF version
│
├── prompts/                      # Shared prompt templates
│   └── kt_assistant_prompt.md
│
├── RAG_UsingPromptEngg/         # Phase 1: Prompt Engineering ✅
│   ├── src/
│   │   ├── kt_assistant.py
│   │   ├── prompt_manager.py
│   │   ├── file_reader.py
│   │   └── app.py
│   └── requirements.txt
│
├── RAG_UsingLocalLLM/           # Phase 2: Local RAG 🚀
│   ├── src/
│   │   ├── config/
│   │   ├── ingestion/
│   │   ├── vectorstore/
│   │   ├── retrieval/
│   │   ├── llm/
│   │   ├── rag_pipeline.py
│   │   ├── configure.py
│   │   └── app.py
│   ├── data/chroma_db/
│   └── requirements.txt
│
├── RAG_UsingAWSBedrock/         # Phase 3: AWS Cloud ☁️
│   └── (To be implemented)
│
├── Study/                        # Learning materials
│   ├── Rag_study.md
│   └── RAG_StudyPlan.md
│
├── EXECUTIVE_SUMMARY.md         # 📋 Start here!
├── QUICK_START.md               # ⚡ Next steps
├── PROJECT_PLAN.md              # 📊 Complete roadmap
├── IMPLEMENTATION_GUIDE_PHASE2.md  # 🔧 Step-by-step guide
├── PHASE_COMPARISON.md          # 📈 Compare approaches
├── ARCHITECTURE_OVERVIEW.md     # 🏗️ System design
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

### Phase 1: Run Current Implementation

```bash
cd RAG_UsingPromptEngg/src
pip install -r ../requirements.txt
python app.py
```

### Phase 2: Setup (Next Step)

Follow the detailed guide in [QUICK_START.md](QUICK_START.md)

```bash
# Create structure
mkdir RAG_UsingLocalLLM
cd RAG_UsingLocalLLM

# Install dependencies
pip install langchain langchain-ollama langchain-chroma chromadb pypdf

# Follow IMPLEMENTATION_GUIDE_PHASE2.md for code
```

## 🎓 Learning Objectives

### Phase 1 (Completed)
- ✅ Prompt engineering fundamentals
- ✅ LangChain basics
- ✅ Ollama LLM integration
- ✅ CLI application development

### Phase 2 (In Progress)
- 📚 Document chunking strategies
- 🧮 Embeddings and vector representations
- 🔍 Semantic search with ChromaDB
- 🔗 RAG pipeline orchestration
- 📊 Context retrieval and ranking

### Phase 3 (Planned)
- ☁️ AWS Bedrock API integration
- 🔐 Cloud authentication and security
- 📈 Scalable vector databases
- 🚀 Production deployment patterns

## 📊 Phase Comparison

| Feature | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|
| **LLM** | Ollama (Local) | Ollama (Local) | AWS Bedrock |
| **Vector Store** | None | ChromaDB | OpenSearch/ChromaDB |
| **Search** | None | Semantic | Semantic |
| **Max Doc Size** | 10 pages | 1000+ pages | Unlimited |
| **Cost** | Free | Free | ~$20-50/month |
| **Deployment** | Local | Local | Cloud |

See [PHASE_COMPARISON.md](PHASE_COMPARISON.md) for detailed comparison.

## 🔄 Implementation Flows

### Phase 2: Configuration Flow
```
PDF → Load → Chunk → Embed → ChromaDB
```

### Phase 2: Query Flow
```
Query → Embed → Search → Retrieve → LLM → Answer
```

See [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) for detailed diagrams.

## 🧪 Example Usage

### Phase 1 (Current)
```bash
$ python app.py

--- KT ASSISTANT ---
Ask questions about KT. Type 'exit', 'bye', or 'quit' to close.

You: What is the framework for testing?
Assistant: The framework used for testing is Playwright (Version 1.40+).

You: Can we use Selenium?
Assistant: No, Selenium is strictly prohibited. All legacy Selenium scripts 
must be migrated to Playwright by Q3.

You: exit
Assistant: Goodbye!
```

### Phase 2 (To Be Implemented)
```bash
# Configuration (one-time)
$ python configure.py qa_guidelines.pdf
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

# Query (interactive)
$ python app.py
=== KT Assistant (RAG with ChromaDB) ===
Loading knowledge base...
Ready! Ask questions about KT.

You: What is the framework for testing?
Assistant: The framework used for testing is Playwright (Version 1.40+).
```

## 📦 Dependencies

### Phase 1
```
langchain
langchain-ollama
langchain-community
pypdf
```

### Phase 2
```
langchain
langchain-ollama
langchain-chroma
langchain-community
chromadb
pypdf
```

### Phase 3
```
langchain
langchain-aws
boto3
chromadb (optional)
opensearch-py (optional)
```

## 🎯 Success Metrics

### Phase 2 Complete When:
- ✅ Configuration script runs successfully
- ✅ ChromaDB created with embeddings
- ✅ Semantic search retrieves relevant context
- ✅ Answers are accurate and contextual
- ✅ Handles out-of-scope queries gracefully
- ✅ Response time < 5 seconds per query

## 🐛 Troubleshooting

### Common Issues

**Issue:** Ollama connection refused  
**Solution:** Start Ollama: `ollama serve`

**Issue:** Module not found  
**Solution:** Install dependencies: `pip install -r requirements.txt`

**Issue:** ChromaDB permission error  
**Solution:** Ensure `data/` folder has write permissions

See [QUICK_START.md](QUICK_START.md) for more troubleshooting tips.

## 📈 Performance Expectations

### Phase 2
- **Configuration:** ~15-20 seconds (one-time)
- **Query:** ~3-4 seconds per request
- **Accuracy:** High (semantic search)
- **Scalability:** Medium (local deployment)

## 🔗 Resources

- **LangChain Documentation:** https://python.langchain.com/docs/
- **ChromaDB Documentation:** https://docs.trychroma.com/
- **Ollama Models:** https://ollama.com/library
- **AWS Bedrock:** https://aws.amazon.com/bedrock/

## 🤝 Contributing

This is a learning project. Feel free to:
- Experiment with different chunk sizes
- Try different embedding models
- Test various LLMs
- Add new features

## 📝 License

This project is for educational purposes.

## 👤 Author

Based on Databricks GenAI Engineering Course learnings.

## 🎉 Next Steps

1. **Read:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for overview
2. **Follow:** [QUICK_START.md](QUICK_START.md) for immediate actions
3. **Implement:** [IMPLEMENTATION_GUIDE_PHASE2.md](IMPLEMENTATION_GUIDE_PHASE2.md) for Phase 2
4. **Compare:** [PHASE_COMPARISON.md](PHASE_COMPARISON.md) to understand trade-offs

**Ready to build Phase 2? Start with [QUICK_START.md](QUICK_START.md)! 🚀**

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Phase 1 Complete, Phase 2 Ready to Implement
