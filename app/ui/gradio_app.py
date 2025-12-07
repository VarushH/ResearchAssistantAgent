# # This calls the Flask API, displays the draft report in an editable box, takes human feedback, and finalizes the report.
# import requests
# import gradio as gr
# from pydantic import ValidationError

# from app.models import ResearchRequest, ReportFeedback

# API_BASE = "http://localhost:8080"  # For local dev; override via env in Cloud Run


# def call_create_draft(query, industry, competitors_csv):
#     competitors = (
#         [c.strip() for c in competitors_csv.split(",") if c.strip()]
#         if competitors_csv
#         else []
#     )
#     try:
#         req = ResearchRequest(
#             query=query,
#             industry=industry or None,
#             competitors=competitors or None,
#         )
#     except ValidationError as e:
#         return None, f"Validation error: {e}", ""

#     resp = requests.post(f"{API_BASE}/api/research/draft", json=req.model_dump())
#     if resp.status_code != 200:
#         return None, f"Error from API: {resp.text}", ""

#     draft = resp.json()
#     draft_id = draft["id"]
#     draft_markdown = draft["draft_markdown"]
#     return draft_id, "", draft_markdown


# def call_finalize(draft_id, edited_markdown, score, comments):
#     try:
#         fb = ReportFeedback(
#             draft_id=draft_id,
#             edited_markdown=edited_markdown,
#             usefulness_score=int(score),
#             comments=comments or None,
#         )
#     except ValidationError as e:
#         return f"Validation error: {e}", ""

#     resp = requests.post(f"{API_BASE}/api/research/finalize", json=fb.model_dump())
#     if resp.status_code != 200:
#         return f"Error from API: {resp.text}", ""

#     result = resp.json()
#     return "", result["final_markdown"]


# def build_interface():
#     with gr.Blocks(title="Market Research Assistant") as demo:
#         gr.Markdown("# Market & Competitive Research Assistant")

#         with gr.Row():
#             query = gr.Textbox(label="Research Query", lines=2)
#         with gr.Row():
#             industry = gr.Textbox(label="Industry", lines=1)
#             competitors = gr.Textbox(
#                 label="Competitors (comma-separated)", lines=1
#             )

#         draft_id_state = gr.State(value=None)

#         draft_error = gr.Markdown("", visible=True)
#         draft_box = gr.Markdown(label="Draft Report (editable below)", value="")

#         edited_box = gr.Textbox(
#             label="Edit the Draft Report (Human-in-the-loop)",
#             lines=20,
#         )

#         score = gr.Slider(
#             label="Usefulness Score",
#             minimum=1,
#             maximum=5,
#             step=1,
#             value=4,
#         )
#         comments = gr.Textbox(label="Comments / Change Requests", lines=3)

#         finalize_error = gr.Markdown("", visible=True)
#         final_report = gr.Markdown(label="Final Report", value="")

#         def on_generate(query, industry, competitors):
#             did, err, draft_md = call_create_draft(query, industry, competitors)
#             return did, err or "", draft_md, draft_md

#         gen_btn = gr.Button("Generate Draft Report")
#         gen_btn.click(
#             fn=on_generate,
#             inputs=[query, industry, competitors],
#             outputs=[draft_id_state, draft_error, draft_box, edited_box],
#         )

#         finalize_btn = gr.Button("Finalize Report")
#         finalize_btn.click(
#             fn=lambda did, edited, s, c: call_finalize(did, edited, s, c),
#             inputs=[draft_id_state, edited_box, score, comments],
#             outputs=[finalize_error, final_report],
#         )

#     return demo


# if __name__ == "__main__":
#     demo = build_interface()
#     demo.launch(server_name="0.0.0.0", server_port=7860)



# app/ui/gradio_app.py

import requests
import gradio as gr
from pydantic import ValidationError

from app.models import ResearchRequest, ReportFeedback

API_BASE = "http://localhost:8080"  # For local dev; override via env in Cloud Run


def call_create_draft(query, industry, competitors_csv):
    competitors = (
        [c.strip() for c in competitors_csv.split(",") if c.strip()]
        if competitors_csv
        else []
    )
    try:
        req = ResearchRequest(
            query=query,
            industry=industry or None,
            competitors=competitors or None,
        )
    except ValidationError as e:
        return None, f"Validation error: {e}", ""

    resp = requests.post(f"{API_BASE}/api/research/draft", json=req.model_dump())
    if resp.status_code != 200:
        return None, f"Error from API: {resp.text}", ""

    draft = resp.json()
    draft_id = draft["id"]
    draft_markdown = draft["draft_markdown"]
    # We only return the draft to fill the editable box
    return draft_id, "", draft_markdown


def call_finalize(draft_id, edited_markdown, score, comments):
    try:
        fb = ReportFeedback(
            draft_id=draft_id,
            edited_markdown=edited_markdown,
            usefulness_score=int(score),
            comments=comments or None,
        )
    except ValidationError as e:
        return f"Validation error: {e}", ""

    resp = requests.post(f"{API_BASE}/api/research/finalize", json=fb.model_dump())
    if resp.status_code != 200:
        return f"Error from API: {resp.text}", ""

    result = resp.json()
    return "", result["final_markdown"]


def build_interface():
    with gr.Blocks(title="Market Research Assistant") as demo:
        gr.Markdown("# Market & Competitive Research Assistant")

        with gr.Row():
            query = gr.Textbox(label="Research Query", lines=2)
        with gr.Row():
            industry = gr.Textbox(label="Industry", lines=1)
            competitors = gr.Textbox(
                label="Competitors (comma-separated)", lines=1
            )

        draft_id_state = gr.State(value=None)

        draft_error = gr.Markdown("", visible=True)

        # SINGLE editable textbox – no preview Markdown above
        edited_box = gr.Textbox(
            label="Draft / Edit Report (Markdown)",
            lines=20,
        )

        score = gr.Slider(
            label="Usefulness Score",
            minimum=1,
            maximum=5,
            step=1,
            value=4,
        )
        comments = gr.Textbox(label="Comments / Change Requests", lines=3)

        finalize_error = gr.Markdown("", visible=True)
        final_report = gr.Markdown(label="Final Report", value="")

        def on_generate(query, industry, competitors):
            did, err, draft_md = call_create_draft(query, industry, competitors)
            # We only fill the editable box; no preview Markdown
            return did, err or "", draft_md

        gen_btn = gr.Button("Generate Draft Report")
        gen_btn.click(
            fn=on_generate,
            inputs=[query, industry, competitors],
            outputs=[draft_id_state, draft_error, edited_box],
        )

        finalize_btn = gr.Button("Finalize Report")
        finalize_btn.click(
            fn=lambda did, edited, s, c: call_finalize(did, edited, s, c),
            inputs=[draft_id_state, edited_box, score, comments],
            outputs=[finalize_error, final_report],
            show_progress = True
            
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)