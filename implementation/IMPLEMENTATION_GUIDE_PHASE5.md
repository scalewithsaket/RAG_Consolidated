# Phase 5 Implementation Guide: AWS Knowledge Base with S3

## 🎯 Goal
Use AWS-managed Knowledge Base service with S3 for automatic PDF ingestion, embedding, and vector storage - eliminating manual ChromaDB management.

---

## 📋 Prerequisites

1. **Phase 4** completed (Full-stack app working)
2. **AWS Account** with permissions for:
   - S3
   - Bedrock Knowledge Base
   - OpenSearch Serverless
3. **AWS CLI** configured
4. **Terraform** (optional, for IaC)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)               │
│  - Chat UI                                                   │
│  - File upload (optional)                                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                │
│  - /api/query endpoint                                       │
│  - /api/upload endpoint (optional)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  AWS Knowledge Base                          │
│  - Automatic PDF parsing                                     │
│  - Automatic chunking                                        │
│  - Automatic embedding (Titan)                               │
│  - Managed vector store (OpenSearch Serverless)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      S3 Bucket                               │
│  - PDF storage                                               │
│  - Automatic sync to Knowledge Base                          │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ No manual embedding generation
- ✅ No ChromaDB management
- ✅ Automatic PDF sync from S3
- ✅ Fully managed vector store
- ✅ Auto-scaling

---

## 🔧 AWS Setup

### STEP 1: Create S3 Bucket (10 min)

**Via AWS Console:**
1. Go to S3 Console
2. Create bucket: `kt-documents-bucket-{your-id}`
3. Enable versioning
4. Keep default encryption

**Via AWS CLI:**
```bash
aws s3 mb s3://kt-documents-bucket-12345 --region us-east-1
aws s3api put-bucket-versioning \
  --bucket kt-documents-bucket-12345 \
  --versioning-configuration Status=Enabled
```

---

### STEP 2: Upload PDF to S3 (5 min)

```bash
aws s3 cp ../documents/kt_qa_guidelines.pdf \
  s3://kt-documents-bucket-12345/documents/
```

---

### STEP 3: Create Knowledge Base (20 min)

**Via AWS Console:**

1. Go to **Bedrock Console** → **Knowledge Bases**
2. Click **Create knowledge base**
3. Configure:
   - **Name:** `kt-knowledge-base`
   - **Description:** QA Knowledge Transfer Documents
   - **IAM Role:** Create new role (auto-generated)

4. **Data Source:**
   - Type: S3
   - S3 URI: `s3://kt-documents-bucket-12345/documents/`
   - Chunking: Default (300 tokens, 20% overlap)

5. **Embeddings Model:**
   - Model: Titan Embeddings G1 - Text

6. **Vector Store:**
   - Type: OpenSearch Serverless
   - Create new collection (auto-managed)

7. Click **Create**

8. Wait for sync (2-5 minutes)

---

### STEP 4: Note Knowledge Base ID (2 min)

After creation, note:
- **Knowledge Base ID:** `ABCD1234EFGH`
- **Data Source ID:** `XYZ789`

---

## 💻 Backend Implementation

### STEP 5: Update Dependencies (5 min)

**backend/requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.0
boto3==1.34.0
```

Note: No more langchain, chromadb, pypdf needed!

---

### STEP 6: Update Environment Config (5 min)

**backend/.env:**
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Knowledge Base
KNOWLEDGE_BASE_ID=ABCD1234EFGH
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# S3 (optional for upload feature)
S3_BUCKET_NAME=kt-documents-bucket-12345
S3_DOCUMENTS_PREFIX=documents/
```

---

### STEP 7: Update Settings (5 min)

**backend/src/config/settings.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Settings
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

# S3 Settings (optional)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_DOCUMENTS_PREFIX = os.getenv("S3_DOCUMENTS_PREFIX", "documents/")

# RAG Settings
MAX_TOKENS = 1000
LLM_TEMPERATURE = 0
```

---

### STEP 8: Knowledge Base Client (20 min)

**backend/src/aws/knowledge_base_client.py:**
```python
import boto3
import json
from config.settings import AWS_REGION, KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID


class KnowledgeBaseClient:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=AWS_REGION
        )
        self.kb_id = KNOWLEDGE_BASE_ID
        self.model_id = BEDROCK_MODEL_ID
    
    def retrieve_and_generate(self, query: str) -> dict:
        """Query Knowledge Base with RetrieveAndGenerate API"""
        try:
            response = self.client.retrieve_and_generate(
                input={
                    'text': query
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.kb_id,
                        'modelArn': f'arn:aws:bedrock:{AWS_REGION}::foundation-model/{self.model_id}',
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': 3
                            }
                        }
                    }
                }
            )
            
            return {
                'answer': response['output']['text'],
                'citations': response.get('citations', []),
                'session_id': response.get('sessionId')
            }
        except Exception as e:
            raise Exception(f"Knowledge Base query failed: {str(e)}")
    
    def retrieve_only(self, query: str, max_results: int = 3) -> list:
        """Retrieve relevant documents without generation"""
        try:
            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            return response.get('retrievalResults', [])
        except Exception as e:
            raise Exception(f"Retrieval failed: {str(e)}")


def get_kb_client():
    """Get Knowledge Base client instance"""
    return KnowledgeBaseClient()
```

---

### STEP 9: S3 Upload Service (Optional - 15 min)

**backend/src/aws/s3_service.py:**
```python
import boto3
from config.settings import AWS_REGION, S3_BUCKET_NAME, S3_DOCUMENTS_PREFIX


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)
        self.bucket_name = S3_BUCKET_NAME
        self.prefix = S3_DOCUMENTS_PREFIX
    
    def upload_file(self, file_content: bytes, filename: str) -> str:
        """Upload file to S3"""
        try:
            key = f"{self.prefix}{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType='application/pdf'
            )
            return f"s3://{self.bucket_name}/{key}"
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def list_documents(self) -> list:
        """List all documents in S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            raise Exception(f"S3 list failed: {str(e)}")


def get_s3_service():
    """Get S3 service instance"""
    return S3Service()
```

---

### STEP 10: Update API Routes (20 min)

**backend/src/api/routes.py:**
```python
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import time

router = APIRouter()

# Global KB client
kb_client = None


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    response_time: float
    sources_count: int
    citations: list = []


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Handle query requests using Knowledge Base"""
    if not kb_client:
        raise HTTPException(status_code=503, detail="Knowledge Base not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Handle greetings
    greetings = ['hi', 'hello', 'hey', 'greetings']
    if request.question.lower().strip() in greetings:
        return QueryResponse(
            answer="Hello! I'm your KT Assistant powered by AWS Knowledge Base. Ask me anything about the QA automation knowledge transfer documents.",
            response_time=0.0,
            sources_count=0
        )
    
    try:
        start_time = time.time()
        result = kb_client.retrieve_and_generate(request.question)
        response_time = time.time() - start_time
        
        return QueryResponse(
            answer=result['answer'],
            response_time=round(response_time, 2),
            sources_count=len(result.get('citations', [])),
            citations=result.get('citations', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF to S3 (triggers auto-sync to Knowledge Base)"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        from aws.s3_service import get_s3_service
        s3_service = get_s3_service()
        
        content = await file.read()
        s3_uri = s3_service.upload_file(content, file.filename)
        
        return {
            "message": "File uploaded successfully",
            "s3_uri": s3_uri,
            "note": "Knowledge Base will sync automatically in 2-5 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "kb_initialized": kb_client is not None
    }


def set_kb_client(client):
    """Set the global KB client instance"""
    global kb_client
    kb_client = client
```

---

### STEP 11: Update Main Application (10 min)

**backend/src/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router, set_kb_client
from aws.knowledge_base_client import get_kb_client

app = FastAPI(
    title="KT Assistant API (Knowledge Base)",
    description="RAG powered by AWS Knowledge Base",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize Knowledge Base client on startup"""
    print("Initializing AWS Knowledge Base client...")
    
    try:
        kb_client = get_kb_client()
        set_kb_client(kb_client)
        print("Knowledge Base client initialized successfully!")
    except Exception as e:
        print(f"Error initializing KB client: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KT Assistant API (AWS Knowledge Base)",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🎨 Frontend Updates (Optional)

### STEP 12: Add File Upload Component (20 min)

**frontend/src/components/FileUpload.jsx:**
```jsx
import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setMessage('Only PDF files are allowed');
      return;
    }

    setUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage('✓ File uploaded! Knowledge Base will sync in 2-5 minutes.');
        onUploadSuccess && onUploadSuccess(data);
      } else {
        setMessage('✗ Upload failed');
      }
    } catch (error) {
      setMessage('✗ Upload error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileUpload}
        disabled={uploading}
        id="file-input"
      />
      <label htmlFor="file-input" className={uploading ? 'disabled' : ''}>
        {uploading ? 'Uploading...' : '📄 Upload PDF'}
      </label>
      {message && <p className="upload-message">{message}</p>}
    </div>
  );
};

export default FileUpload;
```

---

## 📚 Documentation

### STEP 13: Update README (10 min)

**README.md:**
```markdown
# Phase 5: AWS Knowledge Base RAG

Fully managed RAG using AWS Knowledge Base with S3 auto-sync.

## Architecture

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Knowledge Base:** AWS Bedrock Knowledge Base
- **Vector Store:** OpenSearch Serverless (managed)
- **Document Storage:** S3
- **Embeddings:** Titan (automatic)

## Key Benefits

✅ No manual embedding generation
✅ No ChromaDB management
✅ Automatic PDF sync from S3
✅ Fully managed vector store
✅ Auto-scaling
✅ Built-in citations

## Setup

### 1. Create S3 Bucket
```bash
aws s3 mb s3://kt-documents-bucket-12345
```

### 2. Upload Documents
```bash
aws s3 cp documents/kt_qa_guidelines.pdf s3://kt-documents-bucket-12345/documents/
```

### 3. Create Knowledge Base
- Go to Bedrock Console
- Create Knowledge Base
- Connect to S3 bucket
- Wait for sync (2-5 minutes)

### 4. Configure Backend
```bash
cd backend
pip install -r requirements.txt
# Update .env with KNOWLEDGE_BASE_ID
python src/main.py
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open http://localhost:3000
2. Ask questions
3. Get answers with citations
4. (Optional) Upload new PDFs

## Cost Estimation

- **Knowledge Base:** $0.10/GB/month storage
- **OpenSearch Serverless:** ~$700/month (minimum)
- **Bedrock API:** ~$0.01 per query
- **S3:** ~$0.023/GB/month

**Note:** OpenSearch Serverless has minimum cost. Use for production only.

## Comparison with Phase 4

| Feature | Phase 4 (ChromaDB) | Phase 5 (KB) |
|---------|-------------------|--------------|
| Setup | Manual | Automatic |
| Embeddings | Manual | Automatic |
| Vector Store | Self-managed | AWS-managed |
| Scaling | Manual | Auto |
| Cost | Lower | Higher |
| Maintenance | High | Low |
```

---

## ✅ Testing

### Test Knowledge Base:
```bash
# Via AWS CLI
aws bedrock-agent-runtime retrieve-and-generate \
  --knowledge-base-id ABCD1234EFGH \
  --input '{"text":"What is the testing framework?"}' \
  --region us-east-1
```

### Test Backend:
```bash
cd backend/src
python main.py
# Visit http://localhost:8000/docs
```

### Test Full Flow:
1. Upload PDF to S3
2. Wait 2-5 minutes for sync
3. Query via frontend
4. Verify citations

---

## 🚀 Advanced Features

### Add Sync Status Endpoint:
```python
@router.get("/sync-status")
async def get_sync_status():
    """Check Knowledge Base sync status"""
    client = boto3.client('bedrock-agent', region_name=AWS_REGION)
    response = client.get_data_source(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID
    )
    return response
```

### Add Manual Sync Trigger:
```python
@router.post("/sync")
async def trigger_sync():
    """Manually trigger Knowledge Base sync"""
    client = boto3.client('bedrock-agent', region_name=AWS_REGION)
    response = client.start_ingestion_job(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID
    )
    return {"job_id": response['ingestionJob']['ingestionJobId']}
```

---

## 📊 Phase Comparison

| Metric | Phase 4 | Phase 5 |
|--------|---------|---------|
| Setup Time | 4-6 hours | 2-3 hours |
| Maintenance | High | Low |
| Scalability | Medium | High |
| Cost (1K queries) | ~$5 | ~$10 + $700/month |
| Auto-sync | No | Yes |
| Citations | Manual | Built-in |

---

## 🎯 When to Use Phase 5

✅ Production deployment
✅ Multiple documents
✅ Frequent updates
✅ Need auto-sync
✅ Budget available ($700+/month)
✅ Want zero maintenance

❌ Development/testing (use Phase 4)
❌ Limited budget
❌ Single static document

---

**Congratulations!** 🎉 You now have a fully managed, production-ready RAG system!
