import os
import shutil
import gradio as gr
from graph.pipeline import app_pipeline
from core.vector_store import get_collection

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")

def get_sidebar_info():
    """
    Returns a markdown string listing processed documents and chunk count.
    """
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
    """
    Handles file uploads, moves them to UPLOAD_DIR, and invokes the ingestion agent.
    Returns status message.
    """
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
            
    # Trigger Ingestion Pipeline
    state = app_pipeline.invoke({"mode": "ingest", "query": "", "files": [], "response": "", "insights": {}})
    
    # Reload sidebar
    return gr.update(value=get_sidebar_info())

def handle_query(message, history):
    """
    Handles chat querying. Expects message and returns updated history.
    Compatible with Gradio 6 message format (list of dicts).
    """
    if not message.strip():
        return "", history

    # Trigger Query Pipeline
    state = app_pipeline.invoke({"mode": "query", "query": message, "files": [], "response": "", "insights": {}})
    response = state.get("response", "Error getting response.")
    
    # Format sources as expandable block if present
    if "\n\nSources:\n" in response:
        parts = response.split("\n\nSources:\n")
        answer = parts[0]
        sources = parts[1]
        formatted_response = f"{answer}\n\n<details><summary><b>📂 Sources</b></summary>\n\n{sources}\n</details>"
    else:
        formatted_response = response

    # ✅ Gradio 6 fix: use dict format instead of tuple
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": formatted_response})

    return "", history

def handle_insights():
    """
    Triggers Insight Agent to generate the JSON and returns values for the 3 sections.
    """
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

custom_css = """
<style>
body, .gradio-container, .dark {
    background: url('/assets/app_bg.png') no-repeat center center fixed !important;
    background-size: cover !important;
    background-color: transparent !important;
}
/* Make inner containers transparent to let the background show */
.wrap, #root, .contain {
    background: transparent !important;
}
</style>
"""

def create_ui():
    """Builds and returns the Gradio Blocks."""
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
    ).set(
        body_background_fill="transparent",
        background_fill_primary="rgba(0,0,0,0.4)",
        background_fill_secondary="rgba(0,0,0,0.2)",
        border_color_primary="rgba(255,255,255,0.1)",
        body_text_color="white",
        block_background_fill="rgba(0,0,0,0.5)"
    )

    with gr.Blocks(theme=theme, title="Second Brain Agent") as demo:
        gr.HTML(custom_css)
        with gr.Row():
            # Sidebar
            with gr.Column(scale=1, variant="panel"):
                gr.Markdown("## 🧠 Second Brain Agent")
                gr.Markdown("A local, private AI assistant using LangGraph & Gemini.")
                
                sidebar_text = gr.Markdown(get_sidebar_info())
                
                gr.Markdown("---")
                upload_status = gr.Markdown("")
                
            # Main Content
            with gr.Column(scale=4):
                with gr.Tabs():
                    with gr.Tab("💬 Chat with your Docs"):
                        file_uploader = gr.File(label="Upload Documents (PDF, DOCX, TXT, MD)", file_count="multiple")
                        
                        # ✅ Gradio 6 fix: type='messages' is invalid, the new dict format is standard.
                        chatbot = gr.Chatbot(
                            label="Agent Conversation"
                        )
                        msg = gr.Textbox(
                            label="Ask a question about your documents...",
                            placeholder="E.g., What did I write about project Phoenix?"
                        )
                        clear = gr.ClearButton([msg, chatbot])
                        
                        # Events
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
                        gr.Markdown("Let the AI proactively review your knowledge base to find non-obvious patterns, contradictions, and actionable tasks.")
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