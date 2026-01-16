import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion.embedder import get_embeddings
from vectorstore.chroma_manager import ChromaManager
from rag_pipeline import RAGPipeline


@pytest.fixture(scope="module")
def qa_chain():
    """Initialize RAG pipeline once for all tests"""
    embeddings = get_embeddings()
    chroma_manager = ChromaManager(embeddings)
    vectorstore = chroma_manager.load_vectorstore()
    return RAGPipeline(vectorstore)


# Define test cases: query + expected keyword(s) in the answer
test_cases = [
    ("What is the framework used for testing?", "Playwright"),
    ("Which language is used for writing tests?", "TypeScript"),
    ("What runtime is required?", "NodeJS"),
    ("Is unit testing covered in this KT?", "not covered"),
    ("Can we use Selenium for automation?", "prohibited"),
    ("What reporting tool is used?", "Allure"),
    ("How long are reports retained?", "30 days"),
    ("How does GitHub Copilot help in QA automation?", "Copilot"),
    ("How do I initialize Playwright in the project?", "npm init playwright"),
    ("How should test data be managed?", "JSON"),
]


@pytest.mark.parametrize("query,expected", test_cases)
def test_rag_answers(qa_chain, query, expected):
    """Test RAG responses contain expected keywords"""
    response = qa_chain.query(query)
    assert expected.lower() in response.lower(), f"Query: {query} | Response: {response}"


def test_rag_fallback(qa_chain):
    """Test fallback response for out-of-scope questions"""
    query = "What CI/CD tool is used?"
    response = qa_chain.query(query)
    # Check if response indicates lack of information
    fallback_indicators = ["don't know", "not mentioned", "no information", "cannot find"]
    assert any(indicator in response.lower() for indicator in fallback_indicators), \
        f"Expected fallback response for: {query} | Got: {response}"
