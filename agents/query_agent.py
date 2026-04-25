import os
import google.generativeai as genai
from core.embedder import embed_query
from core.vector_store import query_db

# Configure Gemini
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# The chosen model
MODEL_NAME = "gemini-1.5-flash"

def run_query(question: str) -> dict:
    """
    Takes a user question, retrieves top 5 relevant chunks, and queries Gemini 1.5 Flash.
    Returns: dict with {"answer": answer_text, "sources": list_of_citations}
    """
    if not question.strip():
        return {"answer": "Please ask a valid question.", "sources": []}
        
    try:
        # Embed and Retrieve
        query_emb = embed_query(question)
        search_results = query_db(query_emb, n_results=5)
    except Exception as e:
        return {"answer": f"Error during retrieval: {e}", "sources": []}
        
    retrieved_chunks = search_results.get("documents", [[]])[0]
    retrieved_metadatas = search_results.get("metadatas", [[]])[0]
    
    if not retrieved_chunks:
        return {"answer": "I have no knowledge base to answer from. Please upload files first.", "sources": []}

    # Construct context and citations
    context_text = ""
    sources = []
    
    for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadatas)):
        filename = meta.get("filename", "Unknown") if meta else "Unknown"
        chunk_preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
        
        context_text += f"\n\n--- Document: {filename} ---\n{chunk}"
        sources.append(f"{filename} (Preview: {chunk_preview})")

    # Prompt Setup
    system_prompt = (
        "You are a personal knowledge assistant. Answer ONLY based on the provided context "
        "from the user's own documents. Always cite which document and chunk your answer comes from. "
        "If the answer is not in the context, say so clearly."
    )
    
    prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nQuestion:\n{question}\n\nAnswer:"

    # Call Gemini
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error calling Gemini API: {e}"
        
    return {"answer": answer, "sources": sources}
