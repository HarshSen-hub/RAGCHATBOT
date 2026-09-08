
# CBGRAPH — GraphRAG AI PDF Assistant

CBGRAPH is a full-stack **GraphRAG** (Graph + Retrieval-Augmented Generation) chatbot that lets you upload PDF documents, automatically builds a **knowledge graph** from their content, and answers questions using a hybrid of graph retrieval and semantic vector search — grounded through **Google Gemini**.

Upload a PDF → the system extracts entities and relationships into **Neo4j**, generates embeddings for each chunk, and stores everything in the graph. When you ask a question, it retrieves relevant graph triples *and* semantically similar chunks, combines them into context, and asks Gemini to generate a grounded, source-backed answer.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Reference](#api-reference)
- [Backend Modules](#backend-modules)
- [Frontend](#frontend)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## How It Works

```
PDF
 │
 ▼
Upload through React UI
 │
 ▼
FastAPI backend
 │
 ▼
Extract PDF text (pypdf)
 │
 ▼
Split into chunks (LangChain RecursiveCharacterTextSplitter)
 │
 ▼
Gemini extracts entities + relationships
 │
 ▼
Store entities/relationships in Neo4j
 │
 ▼
Generate embeddings for chunks (Gemini)
 │
 ▼
Store chunks + embeddings in Neo4j
 │
 ▼
User asks question in React Chat UI
 │
 ▼
FastAPI /chat endpoint
 │
 ▼
Gemini extracts important entities from the question
 │
 ▼
Neo4j graph retrieval (RELATED_TO triples)
 │
 ▼
Question embedding + cosine similarity search over stored chunks
 │
 ▼
Combine graph triples + document chunks into context
 │
 ▼
Gemini generates a grounded answer
 │
 ▼
FastAPI returns answer + retrieval metadata
 │
 ▼
React displays the answer and its sources
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite (JavaScript/JSX) |
| Backend | Python + FastAPI + Uvicorn |
| LLM | Google Gemini (`gemini-2.5-flash`) |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| Graph Database | Neo4j |
| PDF Parsing | pypdf |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Vector Retrieval | Gemini embeddings + cosine similarity (computed in Python) |
| Config | `.env` + `python-dotenv` |

> **Note:** This project does **not** use LlamaIndex, Ollama, LangChain agents, OpenAI, Pinecone, or Chroma. Vector retrieval is done with a simple in-memory cosine similarity comparison over embeddings stored directly in Neo4j.

---

## Project Structure

```
CBGRAPH/
│
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entrypoint, CORS, router registration
│   ├── chat.py            # POST /chat — question answering pipeline
│   ├── upload.py          # POST /upload — PDF upload & ingestion trigger
│   ├── ingest.py           # PDF → chunks → entities/relationships → Neo4j
│   ├── retrieval.py        # Graph + vector retrieval logic
│   ├── context_build.py    # Combines graph + chunk context for the LLM
│   ├── ans_gen.py          # Final grounded answer generation via Gemini
│   ├── gemini_client.py    # Gemini API wrapper (generate_json, embed_text)
│   ├── db.py               # Neo4j driver, connection, DB utilities
│   ├── config.py           # Environment variable loading & model config
│   └── ...
│
├── ui/
│   ├── package.json
│   ├── package-lock.json
│   ├── src/
│   └── ...
│
├── .env
├── sample.pdf
├── venv/
└── ...
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js + npm
- Neo4j Desktop (or a running Neo4j instance)
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/CBGRAPH.git
cd CBGRAPH
```

### 2. Backend setup

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd ui
npm install
cd ..
```

### 4. Configure environment variables

Create a `.env` file in the project root (see [Environment Variables](#environment-variables) below).

### 5. Start Neo4j

Launch your Neo4j database instance (e.g. via Neo4j Desktop) and ensure it's reachable at the URI configured in `.env`.

---

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key

NEO4J_URI=bolt://localhost:7687
NEO4J_ID=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

These are loaded and validated in `backend/config.py`, which also defines model and chunking settings:

```python
GEMINI_TEXT_MODEL = "gemini-2.5-flash"
GEMINI_EMBED_MODEL = "gemini-embedding-001"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_CHUNKS = 4
```

> ⚠️ Never commit your `.env` file or expose your API keys/passwords.

---

## Running the Project

Three components need to be running simultaneously.

### 1. Neo4j

Start your Neo4j database (via Neo4j Desktop or your preferred method).

### 2. Backend

```bash
cd CBGRAPH
source backend/venv/bin/activate
uvicorn backend.main:app --reload
```

- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd CBGRAPH/ui
npm run dev
```

- Frontend: `http://localhost:5173`

---

## API Reference

Currently exposed endpoints:

### `GET /`
Health check / root endpoint.

### `POST /upload`
Uploads a PDF and triggers ingestion into the knowledge graph.

**Accepts:** `multipart/form-data` with a PDF `UploadFile`

**Response:**
```json
{
  "message": "...",
  "filename": "...",
  "chunks_processed": 0,
  "chunks_failed": 0,
  "entities_extracted": 0,
  "relationships_extracted": 0
}
```

### `POST /chat`
Answers a question using hybrid graph + vector retrieval.

**Request body:**
```json
{
  "question": "string",
  "history": [
    { "role": "user", "content": "string" }
  ]
}
```
> `history` is currently accepted but not yet used meaningfully in answer generation.

**Response:**
```json
{
  "answer": "...",
  "seed_entities": ["..."],
  "graph_triples": [
    { "source": "...", "relation": "...", "target": "..." }
  ],
  "chunks_used": [
    { "chunk_id": "...", "score": 0.0, "text": "..." }
  ]
}
```

> **Not yet implemented:** `GET /documents`, `GET /knowledge-graph`, `GET /dashboard-stats`, `GET /document/{id}` — these are planned but do not currently exist.

---

## Backend Modules

| File | Responsibility |
|---|---|
| `config.py` | Loads and validates env vars; defines model names and chunking parameters |
| `db.py` | Neo4j driver setup (`GraphDatabase.driver`), `close_driver()`, `clear_database()` |
| `gemini_client.py` | Wraps the Google GenAI client — `generate_json(prompt)` and `embed_text(text)` |
| `ingest.py` | Full PDF ingestion pipeline: extract → chunk → extract entities/relationships → store in Neo4j → embed → link chunks to entities |
| `retrieval.py` | `extract_question_entities()`, `retrieve_graph_triples()`, `_cosine_similarity()`, `retrieve_similar_chunks()` |
| `context_build.py` | Merges graph triples and retrieved chunks into a single context string for the LLM |
| `ans_gen.py` | `generate_answer(question, context)` — calls Gemini with a grounding prompt that instructs it to only use the provided context |
| `chat.py` | Defines `POST /chat` and orchestrates the full retrieval → context → generation pipeline |
| `upload.py` | Defines `POST /upload`, saves the PDF, and calls `ingest_pdf()` |
| `main.py` | FastAPI app instance, CORS config (`http://localhost:5173`), router registration |

### Knowledge Graph Schema

**Entities:**
```
(:Entity {name: string, type: string})
```

**Relationships:**
```
(:Entity)-[:RELATED_TO {type: string}]->(:Entity)
```

**Chunks:**
```
(:Chunk {id: string, text: string, embedding: [float]})
(:Chunk)-[:MENTIONS]->(:Entity)
```

---

## Frontend

A React/Vite single-page app called **GraphRAG AI — PDF Assistant**, with a sidebar for:

- **Dashboard** — document counts, chunking/embedding/graph status, quick actions
- **Upload PDFs** — drag-and-drop / file picker upload
- **Documents** — document management view
- **Chat** — ask questions, view answers, sources, and document metadata
- **Knowledge Graph** — graph visualization (planned)
- **Settings**

The Chat UI includes a document selector, message history, source citations, quick actions (*Summarize this document*, *Explain this page*, *Generate quiz*, *Key concepts*), and recent-documents panel.

> Some frontend sections (Documents, Knowledge Graph, Dashboard) currently use static/mock data pending dedicated backend endpoints.

---

## Known Limitations

- **Page-level citations** are not yet fully implemented — PDF text is extracted as a whole before chunking, so page numbers aren't preserved through the pipeline yet.
- **Chat history** is accepted by the `/chat` endpoint but not yet used to inform answer generation.
- **Vector search** loads all chunk embeddings into Python and computes cosine similarity locally — fine for small/medium datasets, but not optimized for scale.
- Only `/upload` and `/chat` exist today — Documents, Knowledge Graph, and Dashboard APIs are not yet built.
- Frontend-to-backend integration for Chat and Upload is the current focus area.

---

## Roadmap

1. Connect Chat UI to `POST /chat` with dynamic answer/source rendering
2. Connect Upload UI to `POST /upload` with live progress/result feedback
3. Build `GET /documents` and connect the Documents view
4. Build a Knowledge Graph API + visualization
5. Build `GET /dashboard-stats` for real dashboard metrics
6. Implement true page-level citation tracking
7. Use conversation history meaningfully in answer generation
8. Support multiple documents per session
9. Migrate vector search to Neo4j's native vector index for scale
10. General UI/UX polish

---

## License

This project is currently unlicensed / for personal and portfolio use. Add a license file if you plan to open-source it.
