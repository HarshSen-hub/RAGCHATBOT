
import math
from .config import TOP_K_CHUNKS
from .gemini_client import generate_json, embed_text
from .db import driver

ENTITY_EXTRACTION_PROMPT_TEMPLATE = """
Extract only the important entities (people, companies, products, places,
concepts) mentioned in this question.

Return ONLY valid JSON in exactly this shape, nothing else:
{{"entities": ["", ""]}}

Question:
{question}
"""


def extract_question_entities(question: str) -> list:
    prompt = ENTITY_EXTRACTION_PROMPT_TEMPLATE.format(question=question)
    data = generate_json(prompt)
    return data.get("entities", [])


def retrieve_graph_triples(entities: list) -> list:
    """Given seed entity names, return connected triples from Neo4j."""
    if not entities:
        return []

    query = """
    MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
    WHERE a.name IN $entities OR b.name IN $entities
    RETURN a.name AS source, r.type AS relation, b.name AS target
    LIMIT 50
    """
    with driver.session() as session:
        result = session.run(query, entities=entities)
        return result.data()


def _cosine_similarity(vec_a, vec_b) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_similar_chunks(question: str, top_k: int = TOP_K_CHUNKS) -> list:
    """Embeds the question and does cosine-similarity search over all
    stored chunk embeddings. Returns top_k chunks with scores.

    Note: this pulls all chunk embeddings into Python and scores them
    locally, which is fine for small/medium document sets. For large
    corpora, switch to Neo4j's native vector index
    (db.index.vector.queryNodes) instead.
    """
    question_embedding = embed_text(question)

    with driver.session() as session:
        result = session.run("MATCH (c:Chunk) RETURN c.id AS id, c.text AS text, c.embedding AS embedding")
        rows = result.data()

    scored = []
    for row in rows:
        score = _cosine_similarity(question_embedding, row["embedding"])
        scored.append({"chunk_id": row["id"], "text": row["text"], "score": score})

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_k]
