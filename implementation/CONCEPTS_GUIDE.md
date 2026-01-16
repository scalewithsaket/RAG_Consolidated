# RAG Concepts Guide: Deep Dive

## 📚 Table of Contents
1. [Vector Embeddings Explained](#vector-embeddings)
2. [Vector Databases Internals](#vector-databases)
3. [AWS Bedrock Architecture](#aws-bedrock)
4. [RAG Pipeline Deep Dive](#rag-pipeline)
5. [Optimization Strategies](#optimization)

---

## 1. Vector Embeddings Explained {#vector-embeddings}

### What Are Embeddings?

**Simple Definition:** Converting text into arrays of numbers that capture meaning.

```
Text: "What is Playwright?"
↓
Embedding Model (Titan/nomic-embed)
↓
Vector: [0.23, -0.45, 0.67, ..., 0.12]  (768 or 1536 dimensions)
```

### Why Embeddings Work

**Key Insight:** Similar meanings → Similar vectors

```
"dog" → [0.8, 0.2, 0.1, ...]
"puppy" → [0.79, 0.21, 0.09, ...]  ← Close in vector space!
"car" → [0.1, 0.9, 0.3, ...]       ← Far from dog/puppy
```

### Embedding Dimensions

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| nomic-embed-text | 768 | General purpose, fast |
| Titan Embeddings G1 | 1536 | AWS, high quality |
| OpenAI text-embedding-3-small | 1536 | High quality |
| OpenAI text-embedding-3-large | 3072 | Best quality, slower |

**More dimensions = More nuanced meaning capture (but slower)**

### How Similarity is Measured

#### Cosine Similarity (Most Common)
```python
import numpy as np

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

# Range: -1 to 1
# 1 = identical
# 0 = orthogonal (unrelated)
# -1 = opposite
```

#### Euclidean Distance
```python
def euclidean_distance(vec1, vec2):
    return np.linalg.norm(vec1 - vec2)

# Lower = more similar
```

### Embedding Generation Process

```
1. Tokenization
   "What is Playwright?" → ["What", "is", "Play", "wright", "?"]

2. Token IDs
   ["What", "is", "Play", "wright", "?"] → [2054, 318, 3811, 29995, 30]

3. Neural Network Processing
   Token IDs → Transformer layers → Contextual representations

4. Pooling
   Multiple token vectors → Single sentence vector

5. Normalization
   Vector → Unit vector (length = 1)
```

### Embedding Model Comparison

| Feature | Titan | nomic-embed | OpenAI |
|---------|-------|-------------|--------|
| Cost | $0.0001/1K tokens | Free (local) | $0.0001/1K tokens |
| Speed | Fast | Very Fast | Fast |
| Quality | High | Good | Very High |
| Max Tokens | 8192 | 8192 | 8191 |
| Dimensions | 1536 | 768 | 1536/3072 |

---

## 2. Vector Databases Internals {#vector-databases}

### What is a Vector Database?

**Traditional DB:**
```sql
SELECT * FROM documents WHERE title = 'Playwright'
```
Exact match only!

**Vector DB:**
```python
vectorstore.similarity_search("testing framework", k=3)
```
Finds semantically similar content!

### How Vector DBs Work

#### 1. Indexing Phase
```
Document → Chunks → Embeddings → Index Structure
```

**Example:**
```
Chunk 1: "Playwright is a testing framework"
         ↓ Embed
         [0.23, 0.45, 0.67, ...]
         ↓ Store in index
         Node in HNSW graph

Chunk 2: "TypeScript is the language"
         ↓ Embed
         [0.12, 0.89, 0.34, ...]
         ↓ Store in index
         Another node in graph
```

#### 2. Query Phase
```
Query: "What is the testing tool?"
       ↓ Embed
       [0.24, 0.44, 0.68, ...]
       ↓ Search index
       Find nearest neighbors
       ↓
       Return top-K chunks
```

### Indexing Algorithms

#### HNSW (Hierarchical Navigable Small World)
Used by: ChromaDB, Pinecone, Weaviate

```
Layer 2:  A ←→ B
          ↓    ↓
Layer 1:  A ←→ C ←→ B ←→ D
          ↓    ↓    ↓    ↓
Layer 0:  A-C-E-B-F-D-G-H

Search: Start at top layer, navigate down
Speed: O(log N)
```

**Pros:**
- Very fast queries
- Good recall (finds relevant docs)

**Cons:**
- Slower indexing
- More memory usage

#### IVF (Inverted File Index)
Used by: FAISS, some OpenSearch configs

```
Cluster 1: [Doc1, Doc5, Doc9]  ← "Testing" cluster
Cluster 2: [Doc2, Doc6, Doc10] ← "Language" cluster
Cluster 3: [Doc3, Doc7, Doc11] ← "Tools" cluster

Search: Find nearest cluster → Search within cluster
```

**Pros:**
- Fast indexing
- Less memory

**Cons:**
- Slower queries than HNSW
- May miss some relevant docs

### Vector DB Comparison

| Database | Algorithm | Best For | Hosting |
|----------|-----------|----------|---------|
| ChromaDB | HNSW | Local dev, small scale | Local/Self-hosted |
| Pinecone | HNSW | Production, managed | Cloud only |
| Weaviate | HNSW | Hybrid search | Self/Cloud |
| OpenSearch | IVF/HNSW | AWS ecosystem | AWS managed |
| FAISS | IVF | Research, custom | Local only |

### ChromaDB Architecture

```
┌─────────────────────────────────────┐
│         ChromaDB Client             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Collection Manager             │
│  - Manages multiple collections     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         HNSW Index                  │
│  - Fast similarity search           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Persistent Storage             │
│  - SQLite (metadata)                │
│  - Parquet (vectors)                │
└─────────────────────────────────────┘
```

### OpenSearch Serverless Architecture

```
┌─────────────────────────────────────┐
│      API Gateway                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Compute Capacity (OCU)           │
│  - Auto-scales based on load        │
│  - Min: 2 OCU (~$700/month)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Vector Engine                  │
│  - k-NN plugin                      │
│  - HNSW/IVF algorithms              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      S3 Storage                     │
│  - Vectors + metadata               │
│  - Automatic backups                │
└─────────────────────────────────────┘
```

---

## 3. AWS Bedrock Architecture {#aws-bedrock}

### Bedrock Components

```
┌─────────────────────────────────────────────────────┐
│                  AWS Bedrock                        │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Foundation   │  │  Knowledge   │  │  Agents  │ │
│  │   Models     │  │    Bases     │  │          │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
```

### Foundation Models

#### Available Models:
```
Anthropic:
  - Claude 3 Opus (most capable, expensive)
  - Claude 3 Sonnet (balanced)
  - Claude 3 Haiku (fast, cheap) ← We use this

Amazon:
  - Titan Text G1 (general)
  - Titan Embeddings G1 (embeddings) ← We use this

Meta:
  - Llama 2/3 (open source)

Cohere:
  - Command (text generation)
  - Embed (embeddings)
```

#### Model Invocation Flow:
```
Your App
    ↓ boto3 API call
AWS Bedrock API Gateway
    ↓ Route to model
Model Inference Endpoint (GPU cluster)
    ↓ Process request
Response
    ↓ Return
Your App
```

### Knowledge Base Architecture

```
┌─────────────────────────────────────────────────────┐
│                    S3 Bucket                        │
│  - PDFs, docs, text files                          │
└────────────────────┬────────────────────────────────┘
                     │ Sync trigger
                     ▼
┌─────────────────────────────────────────────────────┐
│              Data Source Connector                  │
│  - Monitors S3 for changes                          │
│  - Triggers ingestion jobs                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Ingestion Pipeline                     │
│  1. Parse documents (PDF → text)                    │
│  2. Chunk text (default: 300 tokens, 20% overlap)   │
│  3. Generate embeddings (Titan)                     │
│  4. Store in vector DB                              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         OpenSearch Serverless Collection            │
│  - Stores vectors + metadata                        │
│  - Handles similarity search                        │
└─────────────────────────────────────────────────────┘
```

### Knowledge Base Query Flow

```
User Query: "What is Playwright?"
    ↓
Your FastAPI Backend
    ↓ retrieve_and_generate() API call
Bedrock Knowledge Base
    ↓
1. Embed query (Titan Embeddings)
    ↓
2. Search OpenSearch (k-NN)
    ↓
3. Retrieve top-K chunks
    ↓
4. Build context prompt
    ↓
5. Call LLM (Claude 3 Haiku)
    ↓
6. Generate answer with citations
    ↓
Response with answer + sources
    ↓
Your FastAPI Backend
    ↓
React Frontend
```

### Bedrock Pricing Breakdown

#### Foundation Models (Claude 3 Haiku):
```
Input:  $0.25 per 1M tokens
Output: $1.25 per 1M tokens

Example query:
- Context: 1000 tokens (3 chunks × 300 tokens)
- Question: 20 tokens
- Answer: 100 tokens

Cost = (1020 × $0.25 + 100 × $1.25) / 1M
     = $0.00038 per query
     ≈ $0.38 per 1000 queries
```

#### Titan Embeddings:
```
$0.0001 per 1K tokens

Example:
- 10 chunks × 300 tokens = 3000 tokens
- Cost = 3 × $0.0001 = $0.0003
```

#### Knowledge Base:
```
Storage: $0.10 per GB/month
OpenSearch Serverless: ~$700/month minimum (2 OCU)
```

### Bedrock vs Local Comparison

| Aspect | Local (Ollama) | AWS Bedrock |
|--------|---------------|-------------|
| **Setup** | Install Ollama | AWS account + permissions |
| **Cost** | $0 | ~$0.01 per query + $700/month KB |
| **Speed** | 5-10s (CPU) | 1-3s (GPU clusters) |
| **Scaling** | Single machine | Auto-scales to 1000s |
| **Maintenance** | Manual updates | Fully managed |
| **Models** | Limited | 20+ models |
| **Quality** | Good | Excellent |

---

## 4. RAG Pipeline Deep Dive {#rag-pipeline}

### Complete RAG Flow

```
┌─────────────────────────────────────────────────────┐
│                 INDEXING PHASE                      │
│                  (One-time setup)                   │
└─────────────────────────────────────────────────────┘

1. Document Loading
   PDF → PyPDFLoader → List[Document]

2. Text Splitting
   Document → RecursiveCharacterTextSplitter → Chunks
   
   Example:
   "Playwright is a testing framework for web apps.
    It supports TypeScript and JavaScript.
    Tests run in parallel for speed."
   
   ↓ Split (chunk_size=50, overlap=10)
   
   Chunk 1: "Playwright is a testing framework for web apps."
   Chunk 2: "web apps. It supports TypeScript and JavaScript."
   Chunk 3: "JavaScript. Tests run in parallel for speed."

3. Embedding Generation
   Each chunk → Embedding model → Vector
   
   Chunk 1 → [0.23, 0.45, 0.67, ..., 0.12]
   Chunk 2 → [0.34, 0.56, 0.78, ..., 0.23]
   Chunk 3 → [0.45, 0.67, 0.89, ..., 0.34]

4. Vector Storage
   Vectors + metadata → ChromaDB/OpenSearch

┌─────────────────────────────────────────────────────┐
│                  QUERY PHASE                        │
│                  (Runtime)                          │
└─────────────────────────────────────────────────────┘

1. Query Embedding
   "What is Playwright?" → [0.24, 0.44, 0.68, ..., 0.13]

2. Similarity Search
   Query vector → Compare with all stored vectors
   → Return top-K most similar chunks
   
   Results:
   - Chunk 1: similarity = 0.95 ✓
   - Chunk 2: similarity = 0.78 ✓
   - Chunk 3: similarity = 0.45 ✗

3. Context Building
   Retrieved chunks → Format into context string
   
   Context = """
   Chunk 1: Playwright is a testing framework for web apps.
   Chunk 2: web apps. It supports TypeScript and JavaScript.
   """

4. Prompt Construction
   Template + Context + Question → Final prompt
   
   """
   Use the following context to answer the question.
   
   Context: Playwright is a testing framework...
   
   Question: What is Playwright?
   
   Answer:
   """

5. LLM Generation
   Prompt → LLM → Answer
   
   "Playwright is a testing framework for web applications."

6. Response
   Answer → User
```

### Chunking Strategies

#### Fixed-Size Chunking (What we use)
```python
chunk_size = 500 tokens
chunk_overlap = 50 tokens

Document: [0...500] [450...950] [900...1400] ...
           ↑         ↑           ↑
           Chunk 1   Chunk 2     Chunk 3
```

**Pros:**
- Simple
- Predictable
- Fast

**Cons:**
- May split sentences
- No semantic awareness

#### Semantic Chunking (Advanced)
```python
# Split by paragraphs, then combine to target size
chunks = split_by_paragraphs(document)
semantic_chunks = combine_to_target_size(chunks, target=500)
```

**Pros:**
- Preserves meaning
- Better context

**Cons:**
- Slower
- More complex

#### Sentence-Based Chunking
```python
sentences = split_into_sentences(document)
chunks = group_sentences(sentences, max_tokens=500)
```

**Pros:**
- Never splits sentences
- Good for Q&A

**Cons:**
- Variable chunk sizes

### Retrieval Strategies

#### 1. Basic Similarity Search (What we use)
```python
results = vectorstore.similarity_search(query, k=3)
```

#### 2. MMR (Maximal Marginal Relevance)
```python
results = vectorstore.max_marginal_relevance_search(
    query, 
    k=3,
    fetch_k=20,  # Fetch 20, return diverse 3
    lambda_mult=0.5  # Balance relevance vs diversity
)
```

**Use when:** You want diverse results, not just similar ones

#### 3. Hybrid Search (Keyword + Semantic)
```python
# Combine BM25 (keyword) + vector search
keyword_results = bm25_search(query)
vector_results = vector_search(query)
final_results = combine_and_rerank(keyword_results, vector_results)
```

**Use when:** Need both exact matches and semantic matches

#### 4. Reranking
```python
# Get more results, then rerank
candidates = vectorstore.similarity_search(query, k=20)
reranked = reranker_model.rerank(query, candidates)
final_results = reranked[:3]
```

**Use when:** Need highest quality results

### Prompt Engineering for RAG

#### Basic Template (What we use)
```python
template = """
Use the context to answer the question.

Context: {context}

Question: {question}

Answer:
"""
```

#### Advanced Template
```python
template = """
You are a technical assistant. Answer based ONLY on the context.

RULES:
1. If answer not in context, say "I don't know"
2. Cite sources using [Source X]
3. Be concise and accurate

CONTEXT:
{context}

QUESTION:
{question}

ANSWER (with citations):
"""
```

#### Few-Shot Template
```python
template = """
Answer based on context. Examples:

Q: What is X?
A: X is a tool for Y. [Source 1]

Q: How to use Z?
A: To use Z, follow these steps... [Source 2]

Now answer:

Context: {context}
Question: {question}
Answer:
"""
```

---

## 5. Optimization Strategies {#optimization}

### Chunking Optimization

#### Experiment with Chunk Size
```python
# Test different sizes
chunk_sizes = [200, 300, 500, 1000]
for size in chunk_sizes:
    chunks = chunk_documents(docs, chunk_size=size)
    # Evaluate retrieval quality
```

**Guidelines:**
- Small chunks (200-300): Better precision, may miss context
- Large chunks (800-1000): More context, may include noise
- Sweet spot: 400-600 tokens

#### Optimize Overlap
```python
# Overlap prevents splitting important info
chunk_overlap = chunk_size * 0.1  # 10% overlap
```

### Retrieval Optimization

#### Tune TOP_K
```python
# Test different K values
for k in [1, 3, 5, 10]:
    results = retriever.retrieve(query, k=k)
    # Measure: precision, recall, response quality
```

**Guidelines:**
- K=1: Fast, may miss context
- K=3: Good balance (our default)
- K=5+: More context, more noise

#### Add Metadata Filtering
```python
# Filter by document type, date, etc.
results = vectorstore.similarity_search(
    query,
    k=3,
    filter={"document_type": "guidelines", "year": 2024}
)
```

### Embedding Optimization

#### Choose Right Model
```python
# For speed
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# For quality
embeddings = BedrockEmbeddings(model="titan-embed-text-v1")
```

#### Batch Embeddings
```python
# Instead of one-by-one
for chunk in chunks:
    embedding = embed(chunk)  # Slow!

# Batch process
embeddings = embed_batch(chunks)  # Fast!
```

### LLM Optimization

#### Reduce Token Usage
```python
# Shorter context = lower cost
context = "\n".join([chunk.page_content[:200] for chunk in chunks])
```

#### Use Cheaper Models
```python
# Development
model = "llama3.2:1b"  # Free, fast

# Production
model = "claude-3-haiku"  # $0.25/1M tokens
```

#### Add Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question: str):
    return rag_pipeline.query(question)
```

### Performance Metrics

#### Retrieval Metrics
```python
# Precision: % of retrieved docs that are relevant
precision = relevant_retrieved / total_retrieved

# Recall: % of relevant docs that were retrieved
recall = relevant_retrieved / total_relevant

# F1 Score: Harmonic mean
f1 = 2 * (precision * recall) / (precision + recall)
```

#### Generation Metrics
```python
# Faithfulness: Answer based on context?
faithfulness_score = check_faithfulness(answer, context)

# Relevance: Answer addresses question?
relevance_score = check_relevance(answer, question)

# Conciseness: Answer is concise?
conciseness_score = len(answer) / optimal_length
```

### Cost Optimization

#### Bedrock Cost Reduction
```python
# 1. Use smaller chunks (less context tokens)
chunk_size = 300  # Instead of 500

# 2. Reduce TOP_K
top_k = 2  # Instead of 3

# 3. Use Haiku instead of Sonnet
model = "claude-3-haiku"  # 5x cheaper

# 4. Add caching
# 5. Batch requests
```

#### Knowledge Base Cost Reduction
```python
# Use ChromaDB for dev/test
# Use Knowledge Base only for production

if environment == "production":
    use_knowledge_base()
else:
    use_chromadb()
```

---

## 🎓 Key Takeaways

### Embeddings
- Convert text to vectors that capture meaning
- Similar meanings = similar vectors
- 768-1536 dimensions typical
- Cosine similarity for comparison

### Vector Databases
- Store and search embeddings efficiently
- HNSW algorithm for fast search
- ChromaDB for local, OpenSearch for cloud
- Trade-off: speed vs accuracy vs cost

### AWS Bedrock
- Managed LLMs and embeddings
- Knowledge Base = automatic RAG
- OpenSearch Serverless = managed vector DB
- Cost: ~$0.01/query + $700/month minimum

### RAG Pipeline
- Index: Load → Chunk → Embed → Store
- Query: Embed → Search → Context → Generate
- Optimize: chunk size, TOP_K, prompts
- Measure: precision, recall, faithfulness

### Best Practices
- Start with defaults (chunk=500, k=3)
- Experiment and measure
- Use local for dev, cloud for prod
- Monitor costs and performance

---

**Next:** Practice with Phase 2, then move to deployment! 🚀
