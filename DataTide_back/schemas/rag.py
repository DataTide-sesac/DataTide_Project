from pydantic import BaseModel
from typing import List

class RagQueryRequest(BaseModel):
    message: str

# Simplified schema for LLM direct response
class LLMResponse(BaseModel):
    answer: str
