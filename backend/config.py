"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Groq API ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# --- Gemini API ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# --- Model Configuration ---
GENERATION_MODEL: str = "llama-3.3-70b-versatile"

# --- Embedding Configuration ---
# Using Google Gemini for free, instant embeddings
EMBEDDING_MODEL: str = "models/gemini-embedding-001"

# --- Chunking Configuration ---
CHUNK_SIZE: int = 800        # characters per chunk
CHUNK_OVERLAP: int = 200     # overlap between consecutive chunks
TOP_K_RESULTS: int = 5       # number of relevant chunks to retrieve per query

# --- ChromaDB ---
CHROMA_DIR: str = os.path.join(os.path.dirname(__file__), "chroma_db")

# --- Upload Configuration ---
UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "uploads")
MAX_FILE_SIZE_MB: int = 50

# --- CORS ---
FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# --- Server ---
HOST: str = "0.0.0.0"
PORT: int = 8000
