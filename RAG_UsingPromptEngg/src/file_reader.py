import os
from langchain_community.document_loaders import PyPDFLoader

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return project_root

def read_kt_file(filepath):
    """Read knowledge transfer file content"""
    if not os.path.exists(filepath):
        return "Error: File not found."
    with open(filepath, "r") as f:
        return f.read()

def load_kt_context():
    """Load the KT manual context"""
    # Use absolute path from project root    
    kt_file_path = os.path.join(get_project_root(), "documents", "kt_manual.md")
    
    return read_kt_file(kt_file_path)

def load_pdf_text():
    # Use absolute path from project root    
    pdf_file_path = os.path.join(get_project_root(), "documents", "qa_guidelines.pdf")
    
    loader = PyPDFLoader(pdf_file_path)
    # .load() returns a list of "Document" objects (one per page)
    pages = loader.load()
    
    # Combine all pages into one big string for our "Manual" context
    full_text = "\n".join([page.page_content for page in pages])
    return full_text