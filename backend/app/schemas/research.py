from typing import List, Optional
from pydantic import BaseModel

class Paper(BaseModel):
    source: str
    title: str
    abstract: str
    authors: List[str]
    published_date: Optional[str] = None
    pdf_url: Optional[str] = None
    external_id: str

class ResearchRequest(BaseModel):
    query: str
    max_results: int = 5

class ResearchResponse(BaseModel):
    papers: List[Paper]
