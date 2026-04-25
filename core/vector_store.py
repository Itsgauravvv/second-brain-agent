import os
import chromadb
from chromadb.config import Settings

# Persistent directory for Vector DB
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
COLLECTION_NAME = "second_brain"

def get_db_client():
    """Initializes and returns the ChromaDB client pointing to the persistent directory."""
    if not os.path.exists(CHROMA_DIR):
        os.makedirs(CHROMA_DIR, exist_ok=True)
    
    # We use chromadb.PersistentClient for persistent storage
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client

def get_collection():
    """Gets or creates the 'second_brain' collection."""
    client = get_db_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)

def add_chunks_to_db(chunks: list[str], embeddings: list[list[float]], metadata: list[dict], ids: list[str]):
    """
    Adds document chunks with their embeddings and metadata to ChromaDB.
    """
    if not chunks:
        return
    
    collection = get_collection()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadata,
        ids=ids
    )

def query_db(query_embedding: list[float], n_results: int = 5) -> dict:
    """
    Queries ChromaDB for the top 'n_results' most similar chunks to the query embedding.
    Returns the raw ChromaDB results dictionary.
    """
    collection = get_collection()
    
    # If the collection is empty, simply return an empty result format
    if collection.count() == 0:
        return {"documents": [[]], "metadatas": [[]]}
        
    # Ensure we don't request more results than exist in the DB
    results_limit = min(n_results, collection.count())
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=results_limit
    )
    return results

def get_all_chunks(limit: int = 50) -> dict:
    """
    Retrieves all chunks from the database up to a certain limit (useful for Insight Agent).
    Returns a dictionary of documents and metadata.
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
         return {"documents": [], "metadatas": []}
         
    limit = min(limit, count)
    results = collection.peek(limit=limit)
    return results

def get_processed_files() -> set:
    """
    Retrieves a set of all unique filenames that have already been processed into the DB.
    We determine this via the metadata.
    """
    collection = get_collection()
    if collection.count() == 0:
        return set()
        
    # We retrieve all items' metadata using peek or get. But since the number of items
    # might be large, it's safer to get all metadata items
    # (In a production system you would maintain a separate state DB for processed files)
    try:
        results = collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])
        files = set()
        for meta in metadatas:
            if meta and "filename" in meta:
                files.add(meta["filename"])
        return files
    except Exception as e:
         print(f"Error getting processed files: {e}")
         return set()
