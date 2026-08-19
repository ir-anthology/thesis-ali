from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message (natural language or SPARQL)")


class ChatResponse(BaseModel):
    type: str = Field(..., description="Response type: 'sparql', 'table', or 'error'")
    content: str = Field(..., description="Response content")
