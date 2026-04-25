import os
from dotenv import load_dotenv

# Load environment variables early, particularly GOOGLE_API_KEY
load_dotenv()

from ui.app import create_ui

if __name__ == "__main__":
    print("Starting Second Brain Agent...")
    demo = create_ui()
    # Launch Gradio server
    demo.launch(server_name="127.0.0.1", server_port=7860)
