from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    context_documents: Optional[List[int]] = None # 참조할 문서 ID 리스트

class ChatResponse(BaseModel):
    company_id: int
    query: str
    response: str
    chat_id: int
    created_at: datetime
    document_references: List[DocumentReference]

class ChatHistory(BaseModel):
    id: int
    company_id: int
    query: str
    response: str
    created_at: datetime
    feedback: Optional[ChatFeedback] = None
    is_bookmarked: bool = False

class ChatFeedback(BaseModel):
    rating: int
    comment: Optional[str] = None
    is_accurate: bool
    needs_improvement: Optional[str] = None

class DocumentReference(BaseModel):
    document_id: int
    document_type: str
    title: str
    relevance_score: float
    referenced_content: str
