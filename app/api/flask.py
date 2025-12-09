# This exposes endpoints:

# 1. POST /api/research/draft – generate draft report
# 2. POST /api/research/finalize – apply Gradio feedback and produce final report
# 3. GET /metrics – Prometheus endpoint

from uuid import uuid4
from typing import Callable, Type, Tuple

from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter,Histogram

from app.config import settings
from app.models import ResearchRequest, DraftReport, ReportFeedback, FinalReport
from app.agent.graph import run_research, llm
from app.tools.doc_store import sync_local_docs
import os

app = Flask(__name__)
metrics = PrometheusMetrics(app, path="/metrics",group_by="endpoint")

DOCUMENT_FOLDER = "data/documents" 

# Basic custom metrics (extra if needed)
metrics.info("app_info", "Research Assistant", version="1.0.0")

REQUEST_DRAFT_COUNTER = Counter(
    "research_draft_requests_total",
    "Number of draft generation requests"
)

REQUEST_FINALIZE_COUNTER = Counter(
    "research_finalize_requests_total",
    "Number of finalize requests"
)

LLM_LATENCY_HISTOGRAM = Histogram(
    "llm_finalize_latency_seconds",
    "Time spent in LLM finalize step"
)

def initialize_document_index():

    # Index exists → skip
    if os.path.exists("./chroma_db") and len(os.listdir("./chroma_db")) > 0:
        print("Chroma index detected. Skipping indexing...")
        return
    
    # If no index, build it once
    print("No index found. Indexing documents from:", DOCUMENT_FOLDER)
    sync_local_docs(DOCUMENT_FOLDER)
    print("Index created successfully.")


def validate_body(model: Type[BaseModel]) -> Tuple[BaseModel, int]:
    """Utility for Pydantic validation of JSON request bodies."""
    try:
        data = request.get_json(force=True)
    except Exception:
        raise ValidationError("Invalid JSON", model=model)  # type: ignore[arg-type]

    try:
        obj = model.model_validate(data)
    except ValidationError as e:
        # Re-raise to be handled by error handler
        raise e
    return obj, 200


@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
    return jsonify({"error": "ValidationError", "details": e.errors()}), 400


@app.route("/healthz", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "environment": settings.environment})


@app.route("/api/research/draft", methods=["POST"])
def create_draft():
    REQUEST_DRAFT_COUNTER.inc()
    req_obj, _ = validate_body(ResearchRequest)
    state = run_research(req_obj)
    draft_id = str(uuid4())

    draft = DraftReport(
        id=draft_id,
        query=state.query,
        draft_markdown=state.draft_markdown or "",
        web_results=state.web_results,
        doc_chunks=state.doc_chunks,
    )
    # In a real system, store draft in DB/cache with id
    return jsonify(draft.model_dump(mode="json")), 200


# @app.route("/api/research/finalize", methods=["POST"])
# def finalize_report():
#     REQUEST_FINALIZE_COUNTER.inc()

#     feedback_obj, _ = validate_body(ReportFeedback)

#     # Treat edited_markdown as the current draft (may or may not be manually edited)
#     draft_text = feedback_obj.edited_markdown
#     comments = feedback_obj.comments or ""
#     score = feedback_obj.usefulness_score

#     # Use the LLM to revise the draft based on human feedback
#     system_prompt = (
#         "You are a senior market research analyst. "
#         "You will revise the draft report to incorporate human feedback, "
#         "while keeping structure clear, factual, and well formatted in Markdown."
#     )

#     user_prompt = f"""
#     Here is the current draft report (Markdown):

#     ---
#     {draft_text}
#     ---

#     Human feedback / requested changes:
#     {comments}

#     Usefulness score given by the human (1–5): {score}

#     Task:
#     - Improve and rewrite the report to address the feedback.
#     - Preserve useful content, but reorganize / expand / fix it as needed.
#     - Keep the output as a single, clean Markdown document.
#     - Do NOT include any meta-discussion about the fact this is a revision.
#     """
#     with LLM_LATENCY_HISTOGRAM.time():
#         completion = llm.invoke(
#             [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ]
#         )
#     revised_markdown = completion.content

#     final = FinalReport(
#         id=feedback_obj.draft_id,
#         query="(see draft metadata in your DB)",
#         final_markdown=revised_markdown,
#         citations=[],  # you can reattach citations from stored draft if you persist them
#     )

#     return jsonify(final.model_dump(mode="json")), 200



@app.route("/api/research/finalize", methods=["POST"])
def finalize_report():
    REQUEST_FINALIZE_COUNTER.inc()
    feedback_obj, _ = validate_body(ReportFeedback)

    # In a real system, you’d reload DraftReport by id.
    # Here we trust the edited_markdown from Gradio as the final content.
    final_id = feedback_obj.draft_id

    final = FinalReport(
        id=final_id,
        query="(see draft metadata in your DB)",  # placeholder
        final_markdown=feedback_obj.edited_markdown,
        citations=[],  # could re-attach from stored draft
    )
    # Persist final report, feedback metrics, etc.
    return jsonify(final.model_dump()), 200


def create_app() -> Flask:
    initialize_document_index()
    return app


if __name__ == "__main__":
    app.run(host=settings.flask_host, port=settings.flask_port, debug=settings.flask_debug)
