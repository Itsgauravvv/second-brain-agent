import os
from dotenv import load_dotenv

# Load environment variables early, particularly GOOGLE_API_KEY
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gradio as gr
import uvicorn
from ui.app import create_ui

app = FastAPI()

@app.get("/")
def read_main():
    with open("ui/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    print("Starting Papyrus AI...")
    demo = create_ui()
    
    # Mount Gradio app onto FastAPI
    app = gr.mount_gradio_app(app, demo, path="/app")
    
    print("Landing Page running on http://0.0.0.0:7860")
    print("Gradio Agent running on http://0.0.0.0:7860/app")
    
    # ✅ Changed 127.0.0.1 to 0.0.0.0 for HuggingFace
    uvicorn.run(app, host="0.0.0.0", port=7860)