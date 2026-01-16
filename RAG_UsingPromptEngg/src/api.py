from fastapi import FastAPI
from pydantic import BaseModel
from kt_associate import KTAssociate

app = FastAPI(title="KT Assistant API", version="1.0.0")
assistant = KTAssociate()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    status: str = "success"

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask the KT assistant a question"""
    try:
        answer = assistant.ask(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        return QueryResponse(answer=f"Error: {str(e)}", status="error")


@app.post("/asknew", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask the KT assistant a question"""
    try:
        answer = assistant.ask_pdf_assistant(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        return QueryResponse(answer=f"Error: {str(e)}", status="error")
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)