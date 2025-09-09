from pydantic import BaseModel
from typing import List

class RagQueryRequest(BaseModel):
    message: str

class SourceDocument(BaseModel):
    source: str
    content: str

class RagQueryResponse(BaseModel):
    query: str
    answer: str
    source_documents: List[SourceDocument]
