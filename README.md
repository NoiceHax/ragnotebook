# PDFChat — RAG-Powered Document Q&A

A full RAG (Retrieval-Augmented Generation) pipeline that lets you upload any PDF and have a grounded conversation with it. Every answer is strictly sourced from the document with page-level citations — no hallucination.

## Architecture

```
User uploads PDF
       ↓
  [PDF Processor]  — PyMuPDF extracts text page-by-page
       ↓
  [Chunker]        — Overlapping character-based chunks with sentence-boundary awareness
       ↓
  [Embedder]       — NVIDIA NIM API (nv-embedqa-e5-v5) generates dense embeddings
       ↓
  [Vector Store]   — ChromaDB stores embeddings with page/section metadata
       ↓
  User asks a question
       ↓
  [Retriever]      — Query embedded via NIM, top-K chunks retrieved from ChromaDB
       ↓
  [Generator]      — NVIDIA NIM LLM (Llama 3.3 70B) generates grounded answer
       ↓
  Answer + Citations returned to user
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 + Vite + Tailwind CSS 4 |
| **Backend** | Python + FastAPI |
| **PDF Extraction** | PyMuPDF (fitz) |
| **Embeddings** | sentence-transformers — `all-MiniLM-L6-v2` (384-dim dense vectors, runs locally) |
| **Vector Database** | ChromaDB (persistent, HNSW cosine similarity) |
| **LLM Generation** | NVIDIA NIM API — `meta/llama-3.1-8b-instruct` |
| **Chunking** | Character-based overlapping chunks (800 chars, 200 overlap) with sentence-boundary detection |

## RAG Pipeline — Detailed

### 1. Ingestion
- User uploads a PDF via drag-and-drop or file picker
- File is validated (type, size, magic bytes) and saved to disk

### 2. Chunking Strategy
- **Character-based overlapping chunks**: Each page's text is split into chunks of up to 800 characters with 200-character overlap
- **Sentence-boundary awareness**: Chunks prefer to break at sentence endings (`. `) or newlines to avoid mid-sentence splits
- **Page metadata preserved**: Each chunk retains its source page number for accurate citations
- **Section detection**: Headings are detected via patterns (numbered headings, ALL CAPS, Title Case) and attached as metadata

### 3. Embedding
- Chunks are embedded locally using sentence-transformers `all-MiniLM-L6-v2` model
- Produces 384-dimensional dense vectors
- Embeddings are normalized for cosine similarity

### 4. Storage
- Embeddings + metadata are stored in **ChromaDB** (persistent on disk)
- Each document gets its own collection for clean isolation
- HNSW index with cosine similarity for fast retrieval

### 5. Retrieval
- User's question is embedded with the same model (query mode)
- Top-5 most similar chunks are retrieved from ChromaDB
- Results include page numbers and sections for citation

### 6. Generation
- Retrieved chunks are formatted into a grounded system prompt
- NVIDIA NIM's Llama 3.1 8B Instruct generates the answer
- Strict grounding rules enforce citation and refusal behavior
- If the answer isn't in the document, the system refuses to answer

## Features

- 📄 **Page-level citations** — Every answer cites exact pages
- 🛡️ **Zero hallucination** — Refuses if the answer isn't in the PDF
- 💬 **Multi-turn chat** — Maintains conversation context across questions
- 📖 **Side-by-side PDF viewer** — Click citations to view the referenced section
- 🌐 **Multilingual support** — Auto-detect, English, Hindi, Hinglish
- 🎨 **Modern dark UI** — Glassmorphism, animations, responsive design

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- NVIDIA NIM API key ([get one here](https://build.nvidia.com))

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# Configure API key
copy .env.example .env
# Edit .env and add your NVIDIA_API_KEY

python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload and process a PDF |
| `POST` | `/api/chat` | Ask a question about the PDF |
| `DELETE` | `/api/document/{id}` | Delete a processed document |
| `GET` | `/api/document/{id}/pdf` | Serve the uploaded PDF |

## Project Structure

```
pdfagent/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration & env vars
│   ├── pdf_processor.py      # PDF extraction & chunking
│   ├── vector_store.py       # ChromaDB + NVIDIA NIM embeddings
│   ├── chat_engine.py        # NVIDIA NIM LLM + grounding logic
│   ├── models.py             # Pydantic request/response schemas
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx           # Main application
│       ├── api.js            # API client
│       ├── index.css          # Global styles
│       └── components/
│           ├── PDFUploader.jsx
│           ├── ChatMessage.jsx
│           ├── ChatInput.jsx
│           ├── TypingIndicator.jsx
│           ├── PDFViewer.jsx
│           └── LanguageSelector.jsx
└── README.md
```
