# Second Brain Agent

A personal knowledge management AI system that lets users upload their own documents (PDFs, .txt, .md, .docx) and chat with them. It also proactively generates insights like contradictions, connections, and action items from the knowledge base.

## Architecture

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
| ChromaDB (Vector DB)  |<--->| Gemini 1.5 Flash (via python SDK)                    |
+-----------------------+     +------------------------------------------------------+
```

## Setup Instructions

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

## Usage

### Chat with your Docs Tab
- **Upload File**: Drop your PDF, TXT, MD, or DOCX files here. They will be parsed, chunked, and embedded into the local vector DB automatically.
- **Chatbox**: Ask questions about your uploaded documents. The AI will retrieve the most relevant sections and answer your query, citing its sources.

### Insights Tab
- Click **Generate Insights** to have the AI review your entire knowledge base and discover:
  - **Contradictions**: Areas where documents might disagree.
  - **Connections**: Hidden links and relationships between concepts.
  - **Action Items**: Tasks or TODOs found in your notes.
