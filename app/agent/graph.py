# Single-agent graph with web search and doc retrieval, producing a draft report.
from typing import Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from app.models import ResearchState, ResearchRequest
from app.tools.web_search import web_search
from app.tools.doc_store import query_docs
from app.report.generator import generate_draft_report
from app.config import settings



llm = ChatGoogleGenerativeAI(model= settings.gemini_model_name, api_key=settings.gemini_api_key,temperature=0.3)


def node_web_search(state: ResearchState) -> Dict[str, Any]:
    results = web_search(state.query, max_results=5)
    return {"web_results": results}


def node_doc_search(state: ResearchState) -> Dict[str, Any]:
    chunks = query_docs(state.query, n_results=10)
    return {"doc_chunks": chunks}


def node_report_generation(state: ResearchState) -> Dict[str, Any]:
    updated_state = generate_draft_report(state)
    return {
        "draft_markdown": updated_state.draft_markdown,
        "citations": updated_state.citations,
    }


# Build graph
_graph_builder = StateGraph(ResearchState)

_graph_builder.add_node("web_search", node_web_search)
_graph_builder.add_node("doc_search", node_doc_search)
_graph_builder.add_node("report_generation", node_report_generation)

_graph_builder.add_edge(START, "web_search")
# Parallel-ish pattern: web_search → doc_search → report_generation
_graph_builder.add_edge("web_search", "doc_search")
_graph_builder.add_edge("doc_search", "report_generation")
_graph_builder.add_edge("report_generation", END)

agent_app = _graph_builder.compile()


def run_research(req: ResearchRequest) -> ResearchState:
    initial_state = ResearchState(
        query=req.query,
        industry=req.industry,
        competitors=req.competitors or [],
    )

    raw_state = agent_app.invoke(initial_state)

    # LangGraph may return a dict instead of a ResearchState instance
    if isinstance(raw_state, dict):
        # Defensive: ensure citations are plain strings
        if "citations" in raw_state and raw_state["citations"] is not None:
            raw_state["citations"] = [str(c) for c in raw_state["citations"]]
        return ResearchState(**raw_state)

    # If it’s already a ResearchState, just return it
    return raw_state
