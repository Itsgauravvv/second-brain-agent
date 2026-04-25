import os
import fitz  # PyMuPDF
import docx
import tiktoken

def get_tokenizer():
    """Returns a tiktoken tokenizer. We use cl100k_base which is standard for modern LLMs."""
    return tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Chunks text into sizes of roughly `chunk_size` tokens with `overlap` tokens overlap.
    """
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(text)
    
    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        # Advance by chunk_size minus overlap
        i += chunk_size - overlap
        
    return chunks

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
    return text

def parse_docx(file_path: str) -> str:
    """Extracts text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error parsing DOCX {file_path}: {e}")
    return text

def parse_txt_md(file_path: str) -> str:
    """Extracts text from plain text or markdown files."""
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error parsing text file {file_path}: {e}")
    return text

def parse_file(file_path: str) -> list[str]:
    """
    Parses a file based on its extension, extracts text, and returns a list of chunks.
    Raises ValueError for unsupported file types.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == ".pdf":
        text = parse_pdf(file_path)
    elif ext == ".docx":
        text = parse_docx(file_path)
    elif ext in [".txt", ".md"]:
        text = parse_txt_md(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
        
    if not text.strip():
        return []
        
    return chunk_text(text, chunk_size=500, overlap=50)
