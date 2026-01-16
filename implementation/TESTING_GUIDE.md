# Testing Guide: RAG Application

## 🎯 Testing Strategy

```
┌─────────────────────────────────────────────────────┐
│              Testing Pyramid                        │
│                                                     │
│                    /\                               │
│                   /  \  E2E Tests (5%)              │
│                  /────\                             │
│                 /      \  Integration Tests (25%)   │
│                /────────\                           │
│               /          \  Unit Tests (70%)        │
│              /────────────\                         │
└─────────────────────────────────────────────────────┘
```

---

## 1. Unit Tests

### Backend Unit Tests

**tests/test_chunker.py:**
```python
import pytest
from src.ingestion.chunker import chunk_documents
from langchain.schema import Document

def test_chunk_documents_basic():
    """Test basic chunking functionality"""
    docs = [Document(page_content="A" * 1000)]
    chunks = chunk_documents(docs)
    
    assert len(chunks) > 0
    assert all(len(chunk.page_content) <= 500 for chunk in chunks)

def test_chunk_documents_overlap():
    """Test chunk overlap"""
    docs = [Document(page_content="Hello World " * 100)]
    chunks = chunk_documents(docs)
    
    # Check overlap exists
    if len(chunks) > 1:
        assert chunks[0].page_content[-10:] in chunks[1].page_content

def test_chunk_documents_empty():
    """Test empty document handling"""
    docs = []
    chunks = chunk_documents(docs)
    assert len(chunks) == 0

def test_chunk_documents_metadata():
    """Test metadata preservation"""
    docs = [Document(
        page_content="Test content",
        metadata={"source": "test.pdf", "page": 1}
    )]
    chunks = chunk_documents(docs)
    
    assert chunks[0].metadata["source"] == "test.pdf"
    assert chunks[0].metadata["page"] == 1
```

**tests/test_retriever.py:**
```python
import pytest
from unittest.mock import Mock, MagicMock
from src.retrieval.retriever import Retriever

@pytest.fixture
def mock_vectorstore():
    """Create mock vectorstore"""
    vectorstore = Mock()
    vectorstore.as_retriever = Mock(return_value=Mock())
    return vectorstore

def test_retriever_initialization(mock_vectorstore):
    """Test retriever initialization"""
    retriever = Retriever(mock_vectorstore)
    assert retriever.vectorstore == mock_vectorstore
    assert retriever.retriever is not None

def test_retrieve_returns_documents(mock_vectorstore):
    """Test retrieve returns documents"""
    mock_docs = [
        Mock(page_content="Doc 1"),
        Mock(page_content="Doc 2")
    ]
    mock_vectorstore.as_retriever().invoke.return_value = mock_docs
    
    retriever = Retriever(mock_vectorstore)
    results = retriever.retrieve("test query")
    
    assert len(results) == 2
    assert results[0].page_content == "Doc 1"

def test_format_context():
    """Test context formatting"""
    retriever = Retriever(Mock())
    docs = [
        Mock(page_content="First chunk"),
        Mock(page_content="Second chunk")
    ]
    
    context = retriever.format_context(docs)
    assert "First chunk" in context
    assert "Second chunk" in context
    assert "\n\n" in context

def test_format_context_empty():
    """Test empty context handling"""
    retriever = Retriever(Mock())
    context = retriever.format_context([])
    assert context is None
```

**tests/test_rag_pipeline.py:**
```python
import pytest
from unittest.mock import Mock, patch
from src.rag_pipeline import RAGPipeline

@pytest.fixture
def mock_vectorstore():
    return Mock()

@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content="Test answer"))
    return llm

def test_rag_pipeline_initialization(mock_vectorstore):
    """Test RAG pipeline initialization"""
    rag = RAGPipeline(mock_vectorstore)
    assert rag.retriever is not None
    assert rag.llm is not None

@patch('src.rag_pipeline.Retriever')
@patch('src.rag_pipeline.get_llm')
def test_query_success(mock_get_llm, mock_retriever_class, mock_vectorstore):
    """Test successful query"""
    # Setup mocks
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [Mock(page_content="Context")]
    mock_retriever.format_context.return_value = "Context"
    mock_retriever_class.return_value = mock_retriever
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Answer")
    mock_get_llm.return_value = mock_llm
    
    # Test
    rag = RAGPipeline(mock_vectorstore)
    answer = rag.query("What is Playwright?")
    
    assert answer == "Answer"
    mock_retriever.retrieve.assert_called_once()
    mock_llm.invoke.assert_called_once()

def test_query_no_context(mock_vectorstore):
    """Test query with no context found"""
    with patch('src.rag_pipeline.Retriever') as mock_retriever_class:
        mock_retriever = Mock()
        mock_retriever.retrieve.return_value = []
        mock_retriever.format_context.return_value = None
        mock_retriever_class.return_value = mock_retriever
        
        rag = RAGPipeline(mock_vectorstore)
        answer = rag.query("Unknown question")
        
        assert "don't have information" in answer.lower()
```

### Frontend Unit Tests

**frontend/src/components/__tests__/MessageList.test.jsx:**
```javascript
import { render, screen } from '@testing-library/react';
import MessageList from '../MessageList';

describe('MessageList', () => {
  test('renders messages correctly', () => {
    const messages = [
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hi there!' }
    ];
    
    render(<MessageList messages={messages} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  test('displays response time', () => {
    const messages = [
      { role: 'assistant', content: 'Answer', responseTime: 2.5 }
    ];
    
    render(<MessageList messages={messages} />);
    
    expect(screen.getByText('2.5s')).toBeInTheDocument();
  });

  test('renders empty list', () => {
    const { container } = render(<MessageList messages={[]} />);
    expect(container.querySelector('.message')).toBeNull();
  });
});
```

**frontend/src/services/__tests__/api.test.js:**
```javascript
import axios from 'axios';
import { queryKnowledgeBase, checkHealth } from '../api';

jest.mock('axios');

describe('API Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('queryKnowledgeBase success', async () => {
    const mockResponse = {
      data: {
        answer: 'Test answer',
        response_time: 1.5,
        sources_count: 3
      }
    };
    axios.create().post.mockResolvedValue(mockResponse);

    const result = await queryKnowledgeBase('Test question');
    
    expect(result.answer).toBe('Test answer');
    expect(result.response_time).toBe(1.5);
  });

  test('queryKnowledgeBase error', async () => {
    axios.create().post.mockRejectedValue({
      response: { data: { detail: 'Error message' } }
    });

    await expect(queryKnowledgeBase('Test')).rejects.toBe('Error message');
  });

  test('checkHealth success', async () => {
    const mockResponse = {
      data: { status: 'healthy', rag_initialized: true }
    };
    axios.create().get.mockResolvedValue(mockResponse);

    const result = await checkHealth();
    
    expect(result.status).toBe('healthy');
    expect(result.rag_initialized).toBe(true);
  });
});
```

### Run Unit Tests

```bash
# Backend
cd backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend
cd frontend
npm test -- --coverage
```

---

## 2. Integration Tests

### Backend Integration Tests

**tests/integration/test_api_endpoints.py:**
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_query_endpoint_success():
    """Test query endpoint with valid input"""
    response = client.post(
        "/api/query",
        json={"question": "What is Playwright?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "response_time" in data
    assert "sources_count" in data

def test_query_endpoint_empty_question():
    """Test query endpoint with empty question"""
    response = client.post(
        "/api/query",
        json={"question": ""}
    )
    assert response.status_code == 400

def test_query_endpoint_greeting():
    """Test greeting handling"""
    response = client.post(
        "/api/query",
        json={"question": "hello"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Hello" in data["answer"]
    assert data["response_time"] == 0.0

def test_query_endpoint_invalid_json():
    """Test invalid JSON handling"""
    response = client.post(
        "/api/query",
        data="invalid json"
    )
    assert response.status_code == 422

@pytest.mark.skipif(
    not os.getenv("RUN_SLOW_TESTS"),
    reason="Slow test, requires AWS credentials"
)
def test_query_endpoint_real_kb():
    """Test with real Knowledge Base (slow)"""
    response = client.post(
        "/api/query",
        json={"question": "What is the testing framework?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Playwright" in data["answer"]
```

**tests/integration/test_knowledge_base.py:**
```python
import pytest
import boto3
from src.aws.knowledge_base_client import KnowledgeBaseClient

@pytest.fixture
def kb_client():
    return KnowledgeBaseClient()

@pytest.mark.integration
def test_retrieve_and_generate(kb_client):
    """Test Knowledge Base retrieve and generate"""
    result = kb_client.retrieve_and_generate("What is Playwright?")
    
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert "citations" in result

@pytest.mark.integration
def test_retrieve_only(kb_client):
    """Test Knowledge Base retrieve only"""
    results = kb_client.retrieve_only("testing framework", max_results=3)
    
    assert len(results) <= 3
    assert all("content" in r for r in results)

@pytest.mark.integration
def test_invalid_query(kb_client):
    """Test error handling for invalid query"""
    with pytest.raises(Exception):
        kb_client.retrieve_and_generate("")
```

### Frontend Integration Tests

**frontend/src/__tests__/integration/ChatFlow.test.jsx:**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../../components/ChatInterface';
import * as api from '../../services/api';

jest.mock('../../services/api');

describe('Chat Flow Integration', () => {
  beforeEach(() => {
    api.checkHealth.mockResolvedValue({ status: 'ready' });
  });

  test('complete chat flow', async () => {
    api.queryKnowledgeBase.mockResolvedValue({
      answer: 'Playwright is a testing framework',
      response_time: 1.5,
      sources_count: 3
    });

    render(<ChatInterface />);

    // Wait for health check
    await waitFor(() => {
      expect(screen.getByText(/Ready/)).toBeInTheDocument();
    });

    // Type question
    const input = screen.getByPlaceholderText(/Ask a question/);
    fireEvent.change(input, { target: { value: 'What is Playwright?' } });

    // Submit
    const button = screen.getByText('Send');
    fireEvent.click(button);

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText(/Playwright is a testing framework/)).toBeInTheDocument();
    });

    // Check response time displayed
    expect(screen.getByText('1.5s')).toBeInTheDocument();
  });

  test('error handling', async () => {
    api.queryKnowledgeBase.mockRejectedValue('Network error');

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Ask a question/);
    fireEvent.change(input, { target: { value: 'Test' } });
    
    const button = screen.getByText('Send');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/)).toBeInTheDocument();
    });
  });
});
```

### Run Integration Tests

```bash
# Backend (with AWS credentials)
export RUN_SLOW_TESTS=1
pytest tests/integration/ -v -m integration

# Frontend
npm test -- --testPathPattern=integration
```

---

## 3. End-to-End Tests

### Using Playwright

**e2e/tests/chat.spec.js:**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('RAG Chat Application', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should load chat interface', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('KT Assistant');
    await expect(page.locator('.status')).toContainText('Ready');
  });

  test('should send message and receive response', async ({ page }) => {
    // Type question
    await page.fill('input[type="text"]', 'What is Playwright?');
    
    // Click send
    await page.click('button:has-text("Send")');
    
    // Wait for response
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 10000 });
    
    // Check response contains expected text
    const response = await page.locator('.message.assistant').textContent();
    expect(response).toContain('testing');
  });

  test('should handle greeting', async ({ page }) => {
    await page.fill('input[type="text"]', 'hello');
    await page.click('button:has-text("Send")');
    
    await expect(page.locator('.message.assistant')).toContainText('Hello!');
  });

  test('should display response time', async ({ page }) => {
    await page.fill('input[type="text"]', 'What is TypeScript?');
    await page.click('button:has-text("Send")');
    
    await expect(page.locator('.response-time')).toBeVisible({ timeout: 10000 });
  });

  test('should handle multiple messages', async ({ page }) => {
    // First message
    await page.fill('input[type="text"]', 'What is Playwright?');
    await page.click('button:has-text("Send")');
    await page.waitForSelector('.message.assistant');
    
    // Second message
    await page.fill('input[type="text"]', 'What is TypeScript?');
    await page.click('button:has-text("Send")');
    await page.waitForSelector('.message.assistant:nth-child(4)');
    
    // Check both responses exist
    const messages = await page.locator('.message').count();
    expect(messages).toBeGreaterThanOrEqual(4);
  });
});
```

**playwright.config.js:**
```javascript
module.exports = {
  testDir: './e2e/tests',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' },
    },
  ],
};
```

### Run E2E Tests

```bash
# Install Playwright
npm install -D @playwright/test
npx playwright install

# Run tests
npx playwright test

# Run with UI
npx playwright test --ui

# Generate report
npx playwright show-report
```

---

## 4. Load Testing

### Using Locust

**locustfile.py:**
```python
from locust import HttpUser, task, between

class RAGUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def query_knowledge_base(self):
        """Test query endpoint"""
        questions = [
            "What is Playwright?",
            "Which language is used for testing?",
            "What is the reporting tool?",
            "How to initialize Playwright?",
        ]
        
        question = self.environment.parsed_options.question or questions[0]
        
        self.client.post(
            "/api/query",
            json={"question": question},
            name="/api/query"
        )
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/api/health")

    def on_start(self):
        """Called when user starts"""
        # Check if service is ready
        response = self.client.get("/api/health")
        if response.status_code != 200:
            raise Exception("Service not ready")
```

### Run Load Tests

```bash
# Install Locust
pip install locust

# Run with web UI
locust -f locustfile.py --host=http://localhost:8000

# Run headless
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless

# Generate report
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless \
  --html report.html
```

### Using Apache Bench

```bash
# Simple load test
ab -n 1000 -c 10 -p query.json -T application/json \
  http://localhost:8000/api/query

# query.json
{
  "question": "What is Playwright?"
}
```

### Using k6

**load-test.js:**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 10 },  // Ramp up
    { duration: '3m', target: 50 },  // Stay at 50 users
    { duration: '1m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95% under 3s
    http_req_failed: ['rate<0.1'],     // <10% errors
  },
};

export default function () {
  const payload = JSON.stringify({
    question: 'What is Playwright?',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post('http://localhost:8000/api/query', payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 3s': (r) => r.timings.duration < 3000,
    'has answer': (r) => JSON.parse(r.body).answer !== undefined,
  });

  sleep(1);
}
```

**Run k6:**
```bash
k6 run load-test.js
```

---

## 5. Performance Testing

### Response Time Benchmarks

**tests/performance/test_response_time.py:**
```python
import pytest
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_query_response_time():
    """Test query response time is under 5 seconds"""
    start = time.time()
    
    response = client.post(
        "/api/query",
        json={"question": "What is Playwright?"}
    )
    
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 5.0, f"Response took {duration}s, expected < 5s"

def test_health_response_time():
    """Test health check is fast"""
    start = time.time()
    response = client.get("/api/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.1, f"Health check took {duration}s"

@pytest.mark.parametrize("question", [
    "What is Playwright?",
    "Which language is used?",
    "What is the reporting tool?",
])
def test_multiple_queries_performance(question):
    """Test performance across different queries"""
    start = time.time()
    response = client.post("/api/query", json={"question": question})
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 5.0
```

### Memory Profiling

**tests/performance/test_memory.py:**
```python
import pytest
import tracemalloc
from src.rag_pipeline import RAGPipeline

def test_memory_usage():
    """Test memory usage doesn't exceed limits"""
    tracemalloc.start()
    
    # Simulate multiple queries
    for i in range(100):
        # Your query logic here
        pass
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Assert peak memory < 500MB
    assert peak < 500 * 1024 * 1024, f"Peak memory: {peak / 1024 / 1024}MB"
```

---

## 6. Test Coverage

### Generate Coverage Reports

```bash
# Backend coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Frontend coverage
npm test -- --coverage --watchAll=false

# View report
open coverage/lcov-report/index.html
```

### Coverage Goals

```
Unit Tests:        > 80%
Integration Tests: > 60%
Overall:           > 70%
```

---

## 7. CI/CD Testing

### GitHub Actions Test Workflow

**.github/workflows/test.yml:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=src
      
      - name: Run integration tests
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          cd backend
          pytest tests/integration/ -v -m integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: sleep 30
      
      - name: Run E2E tests
        run: npx playwright test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 🎯 Testing Checklist

### Before Deployment
- [ ] All unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Load tests completed (target: 100 concurrent users)
- [ ] Performance benchmarks met (<3s response time)
- [ ] Security tests passed
- [ ] No memory leaks detected

### Continuous Testing
- [ ] CI/CD pipeline configured
- [ ] Automated tests on every commit
- [ ] Coverage reports generated
- [ ] Performance monitoring enabled
- [ ] Alerts configured for failures

---

## 📊 Test Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Unit Test Coverage | >80% | - |
| Integration Coverage | >60% | - |
| E2E Pass Rate | 100% | - |
| Response Time (p95) | <3s | - |
| Error Rate | <1% | - |
| Concurrent Users | 100+ | - |

---

**All guides complete!** 🎉 Ready to build and deploy your RAG application!
