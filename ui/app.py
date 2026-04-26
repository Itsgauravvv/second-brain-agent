import os
import shutil
import gradio as gr
from graph.pipeline import app_pipeline
from core.vector_store import get_collection

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")

def get_sidebar_info():
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return "No documents processed yet."
    try:
        results = collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])
        doc_counts = {}
        for meta in metadatas:
            if meta and "filename" in meta:
                fname = meta["filename"]
                doc_counts[fname] = doc_counts.get(fname, 0) + 1
        lines = [f"**Total Chunks in DB:** {count}\n\n**Processed Documents:**"]
        for fname, c in doc_counts.items():
            lines.append(f"- {fname} ({c} chunks)")
        return "\n".join(lines)
    except Exception as e:
        return f"Error loading state: {e}"

def handle_upload(files) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not files:
        return "No files uploaded."
    for f in files:
        try:
            filename = os.path.basename(f.name)
            target_path = os.path.join(UPLOAD_DIR, filename)
            shutil.copy(f.name, target_path)
        except Exception as e:
            return f"Error copying {filename}: {e}"
    state = app_pipeline.invoke({"mode": "ingest", "query": "", "files": [], "response": "", "insights": {}})
    return gr.update(value=get_sidebar_info())

def handle_query(message, history):
    if not message.strip():
        return "", history
    state = app_pipeline.invoke({"mode": "query", "query": message, "files": [], "response": "", "insights": {}})
    response = state.get("response", "Error getting response.")
    if "\n\nSources:\n" in response:
        parts = response.split("\n\nSources:\n")
        answer = parts[0]
        sources = parts[1]
        formatted_response = f"{answer}\n\n<details><summary><b>📂 Sources</b></summary>\n\n{sources}\n</details>"
    else:
        formatted_response = response
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": formatted_response})
    return "", history

def handle_insights():
    state = app_pipeline.invoke({"mode": "insight", "query": "", "files": [], "response": "", "insights": {}})
    insights = state.get("insights", {})
    if "error" in insights:
        err = insights["error"]
        return err, err, err
    contra = insights.get("contradictions", ["None found."])
    conn = insights.get("connections", ["None found."])
    act = insights.get("action_items", ["None found."])
    def format_list(l):
        return "\n".join([f"- {item}" for item in l])
    return format_list(contra), format_list(conn), format_list(act)

# ✅ Pure CSS dark theme - no image dependencies
custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important;
    min-height: 100vh !important;
}
.block, .panel {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
.chatbot {
    background: rgba(0,0,0,0.3) !important;
}
footer { display: none !important; }
"""

def create_ui():
    """Builds and returns the Gradio Blocks."""
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
    ).set(
        body_background_fill="#0f0c29",
        body_text_color="#ffffff",
        background_fill_primary="#1a1a2e",
        background_fill_secondary="#16213e",
        border_color_primary="#30336b",
        block_background_fill="#1a1a2e",
        block_label_text_color="#a29bfe",
        input_background_fill="#16213e",
        button_primary_background_fill="#6c5ce7",
        button_primary_text_color="#ffffff",
    )

    with gr.Blocks(title="Papyrus AI", theme=theme, css=custom_css) as demo:
        with gr.Row():
            # Sidebar
            with gr.Column(scale=1, variant="panel"):
                gr.Markdown("## 📜 Papyrus AI")
                gr.Markdown("*Your documents, now with memory.*")
                gr.Markdown("---")
                sidebar_text = gr.Markdown(get_sidebar_info())

            # Main Content
            with gr.Column(scale=4):
                with gr.Tabs():
                    with gr.Tab("💬 Chat with your Docs"):
                        file_uploader = gr.File(
                            label="Upload Documents (PDF, DOCX, TXT, MD)",
                            file_count="multiple"
                        )
                        chatbot = gr.Chatbot(
                            label="Agent Conversation",
                            type="messages",
                            height=400
                        )
                        msg = gr.Textbox(
                            label="Ask a question about your documents...",
                            placeholder="E.g., What did I write about project Phoenix?"
                        )
                        clear = gr.ClearButton([msg, chatbot])

                        file_uploader.upload(
                            fn=handle_upload,
                            inputs=[file_uploader],
                            outputs=[sidebar_text]
                        )
                        msg.submit(
                            fn=handle_query,
                            inputs=[msg, chatbot],
                            outputs=[msg, chatbot]
                        )

                    with gr.Tab("💡 Insights"):
                        gr.Markdown("Let the AI proactively review your knowledge base to find patterns, contradictions, and action items.")
                        gen_btn = gr.Button("🔍 Generate Insights", variant="primary")

                        with gr.Accordion("❌ Contradictions", open=True):
                            contra_box = gr.Markdown("Click 'Generate Insights' to start.")
                        with gr.Accordion("🔗 Connections", open=True):
                            conn_box = gr.Markdown("...")
                        with gr.Accordion("✅ Action Items", open=True):
                            act_box = gr.Markdown("...")

                        gen_btn.click(
                            fn=handle_insights,
                            inputs=[],
                            outputs=[contra_box, conn_box, act_box]
                        )

    return demo