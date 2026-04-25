import os
import time
from core.file_parser import parse_file
from core.embedder import embed_texts
from core.vector_store import add_chunks_to_db, get_processed_files

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")

def run_ingestion() -> dict:
    """
    Watches the data/uploads/ folder for new files.
    Parses each file, chunks it, embeds it, and stores it in ChromaDB.
    Returns: dict of {filename: success/failure status}
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    already_processed = get_processed_files()
    results = {}
    
    files_in_dir = [f for f in os.listdir(UPLOAD_DIR) if not f.startswith('.')]
    
    for filename in files_in_dir:
        if filename in already_processed:
            continue
            
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Only process files, skip directories
        if not os.path.isfile(file_path):
            continue
            
        try:
            # 1. Parse and chunk
            chunks = parse_file(file_path)
            if not chunks:
                results[filename] = "Skipped or empty"
                continue
                
            # 2. Embed
            embeddings = embed_texts(chunks)
            if len(chunks) != len(embeddings):
                 results[filename] = "Error: Embedding count mismatch"
                 continue
                 
            # 3. Store
            # Generating unique IDs for each chunk: {filename}_chunk{i}
            timestamp = time.time()
            ids = [f"{filename}_chunk{i}" for i in range(len(chunks))]
            metadata = [{"filename": filename, "chunk_index": i, "timestamp": timestamp} for i in range(len(chunks))]
            
            add_chunks_to_db(chunks, embeddings, metadata, ids)
            results[filename] = "Success"
            
        except Exception as e:
            results[filename] = f"Failed: {str(e)}"
            print(f"Error processing {filename}: {e}")
            
    return results
