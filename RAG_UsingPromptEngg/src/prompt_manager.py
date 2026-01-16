import os
from langchain_core.prompts import PromptTemplate

def load_prompt_template(filepath):
    """Load prompt template from markdown file"""
    if not os.path.exists(filepath):
        return "Error: Prompt template file not found."
    with open(filepath, "r") as f:
        return f.read()

def get_kt_prompt_template():
    """Get the KT assistant prompt template"""
    # Use absolute path from project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    template_path = os.path.join(project_root, "prompts", "kt_assistant_prompt.md")
    
    template_content = load_prompt_template(template_path)
    return PromptTemplate(
        input_variables=["context", "question"],
        template=template_content
    )