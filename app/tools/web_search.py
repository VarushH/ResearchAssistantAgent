# # app/tools/web_search.py
# from typing import List
# # from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_tavily import TavilySearch
# from app.config import settings
# from app.models import WebSearchResult


# def get_tavily_tool() -> TavilySearch:
#     # Tavily API key comes from settings / env
#     return TavilySearch(
#         max_results=5,
#         search_engine="tavily",
#         tavily_api_key=settings.tavily_api_key,
#     )


# def web_search(query: str, max_results: int = 5) -> List[WebSearchResult]:
#     tool = get_tavily_tool()
#     raw_results = tool.invoke({"query": query, "max_results": max_results})
#     # raw_results is usually a list of dicts
#     results: List[WebSearchResult] = []
#     for r in raw_results[:max_results]:
#         results.append(
#             WebSearchResult(
#                 title=r.get("title", "Untitled"),
#                 url=r.get("url", "https://example.com"),
#                 snippet=r.get("content", "")[:500],
#             )
#         )
#     return results


# app/tools/web_search.py
from typing import List

from tavily import TavilyClient

from app.config import settings
from app.models import WebSearchResult


# Initialize Tavily client once
_tavily_client = TavilyClient(api_key=settings.tavily_api_key)


def web_search(query: str, max_results: int = 5) -> List[WebSearchResult]:
    """
    Runs a Tavily web search and returns normalized WebSearchResult objects.
    Uses tavily-python directly instead of LangChain's TavilySearchResults tool.
    """

    # Tavily search API:
    # https://docs.tavily.com/docs/tavily-api/search
    # Typical response: {"results": [ { "title": ..., "url": ..., "content": ... }, ... ] }
    res = _tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",  # or "advanced" if you like
        include_answer=False,  # we only want raw results, we'll do our own summarization
    )

    raw_results = res.get("results", []) or []

    results: List[WebSearchResult] = []
    for r in raw_results[:max_results]:
        results.append(
            WebSearchResult(
                title=r.get("title", "Untitled"),
                url=r.get("url", "https://example.com"),
                snippet=(r.get("content") or "")[:500],
            )
        )

    return results
