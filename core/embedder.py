from sentence_transformers import SentenceTransformer

# Initialize the embedding model once globally to avoid reloading it multiple times
# all-MiniLM-L6-v2 is lightweight and runs locally very well.
_model = None

def get_bge_model():
    """Loads and caches the SentenceTransformer model."""
    global _model
    if _model is None:
        # Note: BGE is good, but based on requirements using all-MiniLM-L6-v2
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of strings.
    Returns a list of dense vector embeddings.
    """
    if not texts:
        return []
    model = get_bge_model()
    # Using tolist() to convert from numpy arrays to standard python lists (required by Chroma)
    embeddings = model.encode(texts).tolist()
    return embeddings

def embed_query(query: str) -> list[float]:
    """
    Generates an embedding for a single query string.
    """
    model = get_bge_model()
    # encode() returns a single vector if passed a string
    embedding = model.encode(query).tolist()
    return embedding
