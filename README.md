# 🧠 Papyrus AI

Papyrus AI is a local, private AI assistant that transforms your static documents into a living knowledge base. Powered by Google Gemini and LangGraph, it lets you chat with your own files, uncover contradictions across your notes, and extract action items — all without your data ever leaving your machine.

## ✨ Features

- **Immersive 3D UI**: Fully responsive frontend featuring an interactive WebGL Spline 3D background, premium glassmorphism, and a sleek dark-mode aesthetic.
- **Multi-format Support**: Upload PDFs, Word docs, plain text, or Markdown files.
- **Chat with your Docs**: Ask natural language questions and get precise answers with source citations from your own documents.
- **AI-Powered Insights**: Discover non-obvious connections between your notes, spot contradictions, and surface forgotten action items automatically.
- **100% Private & Local**: Your documents never leave your machine. Powered by ChromaDB vector search and local sentence-transformers.
- **FastAPI Backend**: Robust routing serving a static marketing landing page and seamlessly mounting the Gradio interface at `/app`.

## 🛠️ Tech Stack

- **LLM**: Google Gemini 2.5 Flash (via `google-genai` SDK)
- **Vector DB**: ChromaDB (Local & persistent)
- **Orchestration**: LangGraph (Multi-agent router)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Backend**: FastAPI & Uvicorn
- **UI**: Gradio & Spline 3D (Vanilla JS Integration)

## ⚙️ Architecture

```text
+-----------------------+      +-------------------+      +---------------------+
|        UI (Gradio)    |<---->|  LangGraph Router |<---->|   Agent Nodes        |
+-----------------------+      +-------------------+      +---------------------+
           |                             |                          |
           |   +-------------------+     |                          |
           +-->| data/uploads/     |-----+                          |
               +-------------------+                                |
                                                                    v
+---------------------+     +------------------+     +-------------------------------+
| Ingestion Agent     |     | Query Agent      |     | Insight Agent                 |
| (embeds & stores chunks) | (retrieves chunks)  |     | (extracts JSON insights)     |
+---------------------+     +------------------+     +-------------------------------+
           |                          |                           |
           v                          v                           v
+-----------------------+     +------------------------------------------------------+
| ChromaDB (Vector DB)  |<--->| Gemini 2.5 Flash (via python SDK)                    |
+-----------------------+     +------------------------------------------------------+
```

## 🚀 Setup Instructions

1. **Install Dependencies**
   Requires Python 3.10+.
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   Copy the example `.env` file and add your Google Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env and insert your GOOGLE_API_KEY
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

## 💬 Usage

1. **Visit the Landing Page**: Open `http://127.0.0.1:7860` to view the interactive 3D site.
2. **Launch the Agent**: Click the "Launch App" button to access the `/app` interface.
3. **Chat with your Docs**: Drop your PDF, TXT, MD, or DOCX files. They will be parsed, chunked, and embedded into the local vector DB automatically. Ask questions and the AI will retrieve the most relevant sections to answer your query.
4. **Generate Insights**: Have the AI review your entire knowledge base to discover contradictions, connections, and action items.

---
**Developer**: Gaurav Joshi
