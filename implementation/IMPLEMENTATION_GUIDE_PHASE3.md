# Phase 3 Implementation Guide: RAG_UsingAWSBedrock

## 🎯 Goal
Migrate the local RAG system to AWS Bedrock for production-ready, scalable deployment with managed services.

---

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Phase 2** completed and working
4. **Bedrock Access** enabled in your AWS region (us-east-1 recommended)
5. **Python 3.9+** installed

---

## 🔑 AWS Setup (30 min)

### STEP 0.1: Install AWS CLI
```bash
# Windows
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
```

### STEP 0.2: Configure AWS Credentials
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

### STEP 0.3: Enable Bedrock Models
1. Go to AWS Console → Bedrock → Model access
2. Request access to:
   - **Claude 3 Haiku** (for LLM)
   - **Titan Embeddings G1 - Text** (for embeddings)
3. Wait for approval (~2-5 minutes)

---

## 🔧 Step-by-Step Implementation

### STEP 1: Create Project Structure (5 min)

```
RAG_UsingAWSBedrock/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── aws/
│   │   ├── __init__.py
│   │   ├── bedrock_client.py
│   │   └── bedrock_embeddings.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   └── chunker.py
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── chroma_manager.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py
│   ├── rag_pipeline.py
│   ├── configure.py
│   └── app.py
├── data/
│   └── chroma_db/
├── requirements.txt
└── README.md
```

---

### STEP 2: Install Dependencies (5 min)

**requirements.txt:**
```
langchain
langchain-aws
langchain-community
boto3
chromadb
pypdf
pytest
```

Install:
```bash
cd RAG_UsingAWSBedrock
pip install -r requirements.txt
```

---

### STEP 3: Configuration Settings (10 min)

**src/config/settings.py:**
```python
import os

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DOCUMENTS_PATH = os.path.join(PROJECT_ROOT, "..", "documents")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")

# AWS Settings
AWS_REGION = "us-east-1"
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K_RESULTS = 3

# LLM settings
LLM_TEMPERATURE = 0
MAX_TOKENS = 1000

# ChromaDB settings
COLLECTION_NAME = "kt_documents_bedrock"
```

---

### STEP 4: Bedrock Embeddings Client (15 min)

**src/aws/bedrock_embeddings.py:**
```python
import boto3
import json
from typing import List
from config.settings import AWS_REGION, BEDROCK_EMBEDDING_MODEL_ID


class BedrockEmbeddings:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
        self.model_id = BEDROCK_EMBEDDING_MODEL_ID
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = []
        for text in texts:
            embedding = self._embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embed_text(text)
    
    def _embed_text(self, text: str) -> List[float]:
        """Call Bedrock API to get embeddings"""
        body = json.dumps({"inputText": text})
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
```

---

### STEP 5: Bedrock LLM Client (15 min)

**src/aws/bedrock_client.py:**
```python
import boto3
import json
from config.settings import AWS_REGION, BEDROCK_MODEL_ID, LLM_TEMPERATURE, MAX_TOKENS


class BedrockLLM:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
        self.model_id = BEDROCK_MODEL_ID
    
    def invoke(self, prompt: str) -> str:
        """Invoke Bedrock LLM with prompt"""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']


def get_llm():
    """Get Bedrock LLM instance"""
    return BedrockLLM()
```

---

### STEP 6: PDF Loader (Copy from Phase 2)

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

### STEP 7: Text Chunker (Copy from Phase 2)

**src/ingestion/chunker.py:**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
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

### STEP 8: ChromaDB Manager (Modified for Bedrock)

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

### STEP 9: Retriever (Copy from Phase 2)

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
        docs = self.retriever.invoke(query)
        return docs
    
    def format_context(self, docs):
        """Format retrieved documents into context string"""
        if not docs:
            return None
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
```

---

### STEP 10: RAG Pipeline (Modified for Bedrock)

**src/rag_pipeline.py:**
```python
from retrieval.retriever import Retriever
from aws.bedrock_client import get_llm

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
        final_prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        response = self.llm.invoke(final_prompt)
        
        return response
```

---

### STEP 11: Configuration Script (Modified for Bedrock)

**src/configure.py:**
```python
import os
import sys
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import chunk_documents
from aws.bedrock_embeddings import BedrockEmbeddings
from vectorstore.chroma_manager import ChromaManager
from config.settings import DOCUMENTS_PATH


def configure(pdf_filename: str):
    """Run configuration flow: PDF -> Chunks -> Embeddings -> ChromaDB"""
    
    print("\n=== RAG Configuration Flow (AWS Bedrock) ===\n")
    
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
    
    # 3. Initialize Bedrock embeddings
    print("\n3. Initializing AWS Bedrock embeddings...")
    embeddings = BedrockEmbeddings()
    print("   [OK] Bedrock embeddings ready")
    
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
        print("Example: python configure.py kt_qa_guidelines.pdf")
        sys.exit(1)
    
    pdf_filename = sys.argv[1]
    configure(pdf_filename)
```

---

### STEP 12: Query CLI Application (Modified for Bedrock)

**src/app.py:**
```python
from aws.bedrock_embeddings import BedrockEmbeddings
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
    
    print("\n=== KT Assistant (AWS Bedrock RAG) ===")
    print("Loading knowledge base...")
    
    # Load vectorstore with Bedrock embeddings
    embeddings = BedrockEmbeddings()
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
                print("Assistant: Hello! I'm your KT Assistant powered by AWS Bedrock. Ask me anything about the QA automation knowledge transfer documents.\n")
            else:
                answer = rag.query(query)
                print(f"Assistant: {answer}\n")


if __name__ == "__main__":
    main()
```

---

### STEP 13: Testing Script (15 min)

**tests/test_bedrock_rag.py:**
```python
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aws.bedrock_embeddings import BedrockEmbeddings
from vectorstore.chroma_manager import ChromaManager
from rag_pipeline import RAGPipeline


@pytest.fixture(scope="module")
def qa_chain():
    """Initialize RAG pipeline with Bedrock"""
    embeddings = BedrockEmbeddings()
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.load_vectorstore()
    return RAGPipeline(vectorstore)


test_cases = [
    ("What is the framework used for testing?", "Playwright"),
    ("Which language is used for writing tests?", "TypeScript"),
    ("What runtime is required?", "NodeJS"),
    ("Is unit testing covered in this KT?", "not covered"),
    ("Can we use Selenium for automation?", "prohibited"),
    ("What reporting tool is used?", "Allure"),
]


@pytest.mark.parametrize("query,expected", test_cases)
def test_bedrock_rag_answers(qa_chain, query, expected):
    """Test Bedrock RAG responses"""
    response = qa_chain.query(query)
    assert expected.lower() in response.lower(), f"Query: {query} | Response: {response}"
```

---

### STEP 14: README Documentation (10 min)

**README.md:**
```markdown
# RAG Using AWS Bedrock (Phase 3)

Production-ready RAG implementation with AWS Bedrock (Claude 3 Haiku) and Titan Embeddings.

## Prerequisites

1. AWS Account with Bedrock access
2. AWS CLI configured
3. Bedrock models enabled:
   - Claude 3 Haiku
   - Titan Embeddings G1 - Text

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Verify Bedrock access:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

## Usage

### Configuration Flow (One-time)
```bash
cd src
python configure.py kt_qa_guidelines.pdf
```

### Query Flow (Interactive)
```bash
python app.py
```

## Testing

```bash
pytest tests/ -v
```

## Cost Estimation

- **Claude 3 Haiku:** ~$0.25 per 1K input tokens, ~$1.25 per 1K output tokens
- **Titan Embeddings:** ~$0.0001 per 1K tokens
- **Estimated cost for 1000 queries:** ~$5-10

## Architecture

- **Embeddings:** Amazon Titan Embeddings G1
- **LLM:** Claude 3 Haiku (Anthropic via Bedrock)
- **Vector Store:** ChromaDB (local)
- **Retrieval:** Semantic search with Top-K

## Migration from Phase 2

Key changes:
1. Replaced Ollama with Bedrock clients
2. Updated embeddings to use Titan
3. Modified LLM calls for Claude API
4. Added AWS authentication
```

---

## ✅ Testing Your Implementation

### Test AWS Connection:
```bash
aws bedrock list-foundation-models --region us-east-1 | grep -i claude
```

### Test Configuration Flow:
```bash
cd RAG_UsingAWSBedrock/src
python configure.py kt_qa_guidelines.pdf
```

Expected output:
```
=== RAG Configuration Flow (AWS Bedrock) ===

1. Loading PDF: kt_qa_guidelines.pdf...
   [OK] Loaded 3 pages

2. Chunking documents...
   [OK] Created 7 chunks

3. Initializing AWS Bedrock embeddings...
   [OK] Bedrock embeddings ready

4. Creating ChromaDB vectorstore...
   [OK] Vectorstore created and persisted

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

---

## 🎓 Key Learnings

1. **AWS Authentication:** Boto3 handles credentials automatically
2. **Bedrock API:** Different from Ollama, requires JSON formatting
3. **Cost Management:** Monitor usage in AWS Console
4. **Latency:** Network calls add 1-2s compared to local
5. **Model Selection:** Claude 3 Haiku balances cost and quality

---

## 🚀 Production Enhancements (Optional)

### Add CloudWatch Logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Add Error Handling:
```python
try:
    response = self.client.invoke_model(...)
except Exception as e:
    logger.error(f"Bedrock API error: {e}")
    return "Service temporarily unavailable"
```

### Add Caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question: str):
    return rag.query(question)
```

### Migrate to OpenSearch (Advanced):
Replace ChromaDB with Amazon OpenSearch for better scalability.

---

## 📊 Phase Comparison

| Feature | Phase 2 (Local) | Phase 3 (Bedrock) |
|---------|----------------|-------------------|
| LLM | Ollama (Free) | Claude 3 ($) |
| Embeddings | Ollama (Free) | Titan ($) |
| Latency | 2-3s | 3-5s |
| Cost | $0 | ~$5-10/1K queries |
| Scalability | Limited | High |
| Production Ready | No | Yes |

---

## 🎯 Next Steps

1. **Monitor Costs:** Check AWS Billing Dashboard daily
2. **Optimize Prompts:** Reduce token usage
3. **Add Caching:** Reduce redundant API calls
4. **Deploy to Lambda:** Serverless deployment
5. **Add API Gateway:** REST API for web apps
6. **Implement OpenSearch:** For better vector search at scale

---

## 🐛 Troubleshooting

### Error: "AccessDeniedException"
- Enable Bedrock model access in AWS Console
- Check IAM permissions

### Error: "ThrottlingException"
- Reduce request rate
- Request quota increase

### High Costs
- Use Claude 3 Haiku (cheapest)
- Implement caching
- Reduce chunk size
- Lower TOP_K_RESULTS

---

## 📚 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3 Model Card](https://www.anthropic.com/claude)
- [Titan Embeddings Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [LangChain AWS Integration](https://python.langchain.com/docs/integrations/platforms/aws)

---

**Congratulations!** 🎉 You've completed all 3 phases of the RAG implementation journey!
