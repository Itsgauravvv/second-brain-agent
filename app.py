import os
from dotenv import load_dotenv

# Load environment variables early, particularly GOOGLE_API_KEY
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import gradio as gr
import uvicorn
from ui.app import create_ui

app = FastAPI()

# Serve assets
app.mount("/assets", StaticFiles(directory="ui/assets"), name="assets")

@app.get("/")
def read_main():
    with open("ui/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    print("Starting Second Brain Agent...")
    demo = create_ui()
    
    # Mount Gradio app onto FastAPI
    app = gr.mount_gradio_app(app, demo, path="/app")
    
    # Launch server
    print("Landing Page running on http://127.0.0.1:7860")
    print("Gradio Agent running on http://127.0.0.1:7860/app")
    uvicorn.run(app, host="127.0.0.1", port=7860)
