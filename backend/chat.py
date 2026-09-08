from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from .retrieval import (
    extract_question_entities,
    retrieve_graph_triples,
    retrieve_similar_chunks,
)

from .context_build import build_context
from .ans_gen import generate_answer

router = APIRouter(tags=["Chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        seed_entities = extract_question_entities(question)
        graph_triples = retrieve_graph_triples(seed_entities)
        similar_chunks = retrieve_similar_chunks(question)

        context = build_context(graph_triples, similar_chunks)
        answer = generate_answer(question, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat pipeline failed: {e}")

    return {
        "answer": answer,
        "seed_entities": seed_entities,
        "graph_triples": [
            {"source": t["source"], "relation": t["relation"], "target": t["target"]}
            for t in graph_triples
        ],
        "chunks_used": [
            {"chunk_id": c["chunk_id"], "score": c["score"], "text": c["text"]}
            for c in similar_chunks
        ],
    }
