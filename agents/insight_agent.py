import os
import json
import random
import re
from google import genai
from google.genai import types
from core.vector_store import get_all_chunks

MODEL_NAME = "gemini-2.5-flash"
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

def run_insights() -> dict:
    """
    Retrieves all (or up to 50) chunks and prompts Gemini 1.5 Flash to extract:
    Contradictions, Connections, and Action Items.
    Returns: parsed JSON dict with these 3 keys.
    """
    try:
        results = get_all_chunks(limit=100) # get a decent amount of chunks
    except Exception as e:
        return {"error": f"Error retrieving chunks: {e}"}
        
    chunks = results.get("documents", [])
    
    if not chunks:
        return {
            "contradictions": ["No documents found."],
            "connections": ["No documents found."],
            "action_items": ["No documents found."]
        }
        
    # If we have too many chunks, we sample 50 as requested to fit prompt window nicely
    # (Gemini Flash has ~1M token context, but we keep it small to avoid confusion & cost)
    if len(chunks) > 50:
         sampled_chunks = random.sample(chunks, 50)
    else:
         sampled_chunks = chunks
         
    context_text = "\n\n---\n\n".join(sampled_chunks)

    system_prompt = (
        "You are an analytical assistant reviewing a person's personal knowledge base. "
        "From the provided document chunks, identify and return exactly:\n"
        "1. CONTRADICTIONS: 2-3 cases where different documents say conflicting things\n"
        "2. CONNECTIONS: 2-3 non-obvious links between ideas across different documents\n"
        "3. ACTION ITEMS: up to 5 todos, deadlines, or tasks mentioned anywhere in the notes\n"
        "Format your response strictly as JSON with keys: 'contradictions', 'connections', 'action_items'. "
        "Each key should map to a list of strings."
    )
    
    prompt = f"{system_prompt}\n\nDocument Chunks:\n{context_text}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        text = response.text
        
        # safely parse JSON
        # In case the model wrapped it in markdown code blocks
        clean_json = re.sub(r'```json|```', '', text).strip()
        data = json.loads(clean_json)
        
        # Ensure keys exist
        data.setdefault("contradictions", [])
        data.setdefault("connections", [])
        data.setdefault("action_items", [])
        
        return data
        
    except json.JSONDecodeError as decode_err:
        return {"error": f"Failed to parse JSON response: {decode_err}\nRaw output: {text}"}
    except Exception as e:
        return {"error": f"Error calling Gemini API: {e}"}
