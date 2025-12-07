# app/models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class DocumentChunk(BaseModel):
    doc_id: str
    source: str
    page: int
    text: str


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=5)
    industry: Optional[str] = None
    competitors: Optional[List[str]] = None
    max_web_results: int = Field(default=5, ge=1, le=20)
    max_doc_chunks: int = Field(default=10, ge=1, le=50)


class DraftReport(BaseModel):
    id: str
    query: str
    draft_markdown: str
    web_results: List[WebSearchResult]
    doc_chunks: List[DocumentChunk]


class ReportFeedback(BaseModel):
    draft_id: str
    edited_markdown: str = Field(..., min_length=10)
    usefulness_score: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None


class FinalReport(BaseModel):
    id: str
    query: str
    final_markdown: str
    citations: List[str]


# LangGraph state model (Pydantic)
class ResearchState(BaseModel):
    query: str
    industry: Optional[str] = None
    competitors: Optional[List[str]] = None

    web_results: List[WebSearchResult] = Field(default_factory=list)
    doc_chunks: List[DocumentChunk] = Field(default_factory=list)

    draft_markdown: Optional[str] = None
    citations: List[str] = Field(default_factory=list)
