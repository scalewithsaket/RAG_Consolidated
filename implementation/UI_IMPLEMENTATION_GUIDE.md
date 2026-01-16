# UI Implementation Guide: React + FastAPI

## 🎨 Overview

Add a modern, minimalistic chat UI to Phase 2 and Phase 3 using:
- **Frontend:** React with clean, responsive design
- **Backend:** FastAPI endpoint for RAG queries
- **Styling:** Tailwind CSS for minimalistic look

---

## 📁 Updated Project Structure

### Phase 2: RAG_UsingLocalLLM
```
RAG_UsingLocalLLM/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   ├── ingestion/
│   │   ├── vectorstore/
│   │   ├── retrieval/
│   │   ├── llm/
│   │   ├── rag_pipeline.py
│   │   ├── api.py              # FastAPI endpoints
│   │   └── configure.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   └── ChatContainer.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── README.md
│
├── app.py                      # CLI version (optional)
└── README.md
```

---

## 🔧 Phase 2 Implementation

### STEP 1: FastAPI Backend (30 min)

#### backend/src/api.py
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from ingestion.embedder import get_embeddings
from vectorstore.chroma_manager import ChromaManager
from rag_pipeline import RAGPipeline
from config.settings import CHROMA_DB_PATH

app = FastAPI(title="KT Assistant API", version="1.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance
rag_pipeline = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    success: bool
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    
    if not os.path.exists(CHROMA_DB_PATH):
        print("Warning: ChromaDB not found. Run configure.py first.")
        return
    
    print("Loading RAG pipeline...")
    embeddings = get_embeddings()
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.load_vectorstore()
    rag_pipeline = RAGPipeline(vectorstore)
    print("RAG pipeline ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "KT Assistant API",
        "status": "running",
        "rag_ready": rag_pipeline is not None
    }

@app.post("/query", response_model=QueryResponse)
async def query_kt(request: QueryRequest):
    """Query the KT knowledge base"""
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized. Run configure.py first."
        )
    
    try:
        answer = rag_pipeline.query(request.query)
        return QueryResponse(answer=answer, success=True)
    except Exception as e:
        return QueryResponse(
            answer="",
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "rag_pipeline": "ready" if rag_pipeline else "not initialized",
        "chroma_db": "exists" if os.path.exists(CHROMA_DB_PATH) else "missing"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### backend/requirements.txt
```txt
# Existing dependencies
langchain==0.1.0
langchain-ollama==0.1.0
langchain-chroma==0.1.0
langchain-community==0.0.20
chromadb==0.4.22
pypdf==4.0.0

# API dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
```

#### Run Backend
```bash
cd RAG_UsingLocalLLM/backend/src
uvicorn api:app --reload --port 8000
```

---

### STEP 2: React Frontend Setup (15 min)

#### Create React App with Vite
```bash
cd RAG_UsingLocalLLM
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### Configure Tailwind CSS

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

### STEP 3: React Components (45 min)

#### src/services/api.js
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const queryKT = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/query`, {
      query: query
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return null;
  }
};
```

#### src/components/ChatMessage.jsx
```jsx
import React from 'react';

const ChatMessage = ({ message, isUser }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-800 border border-gray-200'
        }`}
      >
        <div className="flex items-start gap-2">
          <div className="text-sm font-medium mb-1">
            {isUser ? 'You' : 'Assistant'}
          </div>
        </div>
        <div className="text-sm whitespace-pre-wrap">{message}</div>
      </div>
    </div>
  );
};

export default ChatMessage;
```

#### src/components/ChatInput.jsx
```jsx
import React, { useState } from 'react';

const ChatInput = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about KT..."
          disabled={disabled}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
```

#### src/components/ChatContainer.jsx
```jsx
import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { queryKT, checkHealth } from '../services/api';

const ChatContainer = () => {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm your KT Assistant. Ask me anything about the QA Automation knowledge base.",
      isUser: false,
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check backend health on mount
    checkHealth().then((health) => {
      if (!health || health.rag_pipeline !== 'ready') {
        setIsHealthy(false);
        setMessages((prev) => [
          ...prev,
          {
            text: "⚠️ Backend not ready. Please run configure.py first.",
            isUser: false,
          },
        ]);
      }
    });
  }, []);

  const handleSend = async (query) => {
    // Add user message
    setMessages((prev) => [...prev, { text: query, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await queryKT(query);
      
      if (response.success) {
        setMessages((prev) => [
          ...prev,
          { text: response.answer, isUser: false },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            text: `Error: ${response.error || 'Failed to get response'}`,
            isUser: false,
          },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          text: 'Failed to connect to backend. Please ensure the API is running.',
          isUser: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">KT Assistant</h1>
            <p className="text-sm text-gray-500">QA Automation Knowledge Base</p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                isHealthy ? 'bg-green-500' : 'bg-red-500'
              }`}
            />
            <span className="text-sm text-gray-600">
              {isHealthy ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg.text} isUser={msg.isUser} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 rounded-2xl px-4 py-3 border border-gray-200">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="max-w-4xl mx-auto w-full">
        <ChatInput onSend={handleSend} disabled={isLoading || !isHealthy} />
      </div>
    </div>
  );
};

export default ChatContainer;
```

#### src/App.jsx
```jsx
import React from 'react';
import ChatContainer from './components/ChatContainer';

function App() {
  return <ChatContainer />;
}

export default App;
```

#### src/main.jsx
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

### STEP 4: Run the Application (5 min)

#### Terminal 1: Start Backend
```bash
cd RAG_UsingLocalLLM/backend/src
python configure.py qa_guidelines.pdf  # If not done already
uvicorn api:app --reload --port 8000
```

#### Terminal 2: Start Frontend
```bash
cd RAG_UsingLocalLLM/frontend
npm run dev
```

#### Access Application
Open browser: `http://localhost:5173`

---

## 🎨 UI Features

### Minimalistic Design
- ✅ Clean white background
- ✅ Subtle shadows and borders
- ✅ Rounded message bubbles
- ✅ Blue accent color for user messages
- ✅ Gray for assistant messages
- ✅ Smooth animations

### User Experience
- ✅ Auto-scroll to latest message
- ✅ Loading indicator (animated dots)
- ✅ Health status indicator
- ✅ Disabled input when loading
- ✅ Error handling with user-friendly messages
- ✅ Responsive design (mobile-friendly)

---

## 🚀 Phase 3: AWS Bedrock UI

For Phase 3, the UI remains the same. Only update the backend:

### backend/src/api.py (AWS Bedrock version)
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from bedrock_rag_pipeline import BedrockRAGPipeline  # Updated import

app = FastAPI(title="KT Assistant API (AWS Bedrock)", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    success: bool
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize Bedrock RAG pipeline"""
    global rag_pipeline
    print("Loading AWS Bedrock RAG pipeline...")
    rag_pipeline = BedrockRAGPipeline()
    print("Bedrock RAG pipeline ready!")

@app.post("/query", response_model=QueryResponse)
async def query_kt(request: QueryRequest):
    """Query using AWS Bedrock"""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        answer = rag_pipeline.query(request.query)
        return QueryResponse(answer=answer, success=True)
    except Exception as e:
        return QueryResponse(answer="", success=False, error=str(e))

# Same health endpoint...
```

**Frontend stays exactly the same!** Just point to the new backend.

---

## 📦 Complete Package.json

```json
{
  "name": "kt-assistant-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.5"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.8"
  }
}
```

---

## 🧪 Testing the UI

### Test Queries
1. "What is the framework for testing?"
2. "Can we use Selenium?"
3. "What is the reporting tool?"
4. "How do I set up a React project?" (should say no info)

### Expected Behavior
- ✅ Messages appear in chat bubbles
- ✅ Loading animation shows while waiting
- ✅ Smooth scrolling to new messages
- ✅ Health indicator shows green when ready
- ✅ Error messages display gracefully

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (React)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ChatContainer                                    │  │
│  │    ├── ChatMessage (User)                        │  │
│  │    ├── ChatMessage (Assistant)                   │  │
│  │    └── ChatInput                                 │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │ HTTP POST /query
                      ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /query endpoint                                  │  │
│  │    ├── Receive query                             │  │
│  │    ├── Call RAG Pipeline                         │  │
│  │    └── Return answer                             │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  RAG Pipeline                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Query → Embed → Search → Retrieve → LLM        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Summary

### Phase 2 UI Stack
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + Ollama
- **Communication:** REST API (axios)

### Phase 3 UI Stack
- **Frontend:** Same React app (no changes!)
- **Backend:** FastAPI + AWS Bedrock
- **Communication:** Same REST API

### Time Estimate
- Backend API: 30 minutes
- React Setup: 15 minutes
- Components: 45 minutes
- Testing: 15 minutes
- **Total: ~2 hours**

---

**The UI is now production-ready with a clean, minimalistic design! 🎨**
