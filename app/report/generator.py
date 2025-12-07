# This converts state into a structured Markdown report.
from typing import List
from textwrap import dedent

from app.models import ResearchState, WebSearchResult, DocumentChunk


def _format_web_results(results: List[WebSearchResult]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"{i}. **{r.title}**\n   - {r.snippet}\n   - [{r.url}]({r.url})")
    return "\n".join(lines)


def _format_doc_chunks(chunks: List[DocumentChunk]) -> str:
    lines = []
    for i, c in enumerate(chunks, start=1):
        lines.append(
            f"{i}. Source: `{c.source}`, page {c.page}\n\n"
            f"   > {c.text.replace('\n', ' ')[:500]}..."
        )
    return "\n".join(lines)


def generate_draft_report(state: ResearchState) -> ResearchState:
    web_section = _format_web_results(state.web_results) or "No web data."
    doc_section = _format_doc_chunks(state.doc_chunks) or "No internal docs data."

    industry = state.industry or "Not specified"
    competitors = ", ".join(state.competitors or []) or "Not specified"

    draft = dedent(
        f"""
        # Market Research Report

        ## Query
        {state.query}

        - Industry: {industry}
        - Competitors: {competitors}

        ---

        ## 1. High-Level Market Overview

        Summarize the overall market landscape for **{industry}**,
        including size, growth trends, and major dynamics.

        ## 2. Competitive Landscape

        Describe the positioning and strategies of key competitors:
        {competitors or "Not specified"}.

        ## 3. Web Research Findings

        {web_section}

        ## 4. Internal Document Insights

        {doc_section}

        ## 5. Synthesis & Recommendations

        Provide actionable recommendations based on the combined web
        and internal document insights.

        ---
        """
    ).strip()

    citations = [str(r.url) for r in state.web_results] + [
        str(c.source) for c in state.doc_chunks
    ]

    state.draft_markdown = draft
    state.citations = citations
    return state
