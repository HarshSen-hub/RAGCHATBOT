
import uuid
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .gemini_client import generate_json, embed_text
from .db import driver

EXTRACTION_PROMPT_TEMPLATE = """
You are an expert knowledge assistant for graph extraction.
Extract all important entities and relationships from the text below.

Return ONLY valid JSON in exactly this shape, nothing else:
{{
  "entities": [
    {{"name": "", "type": ""}}
  ],
  "relationships": [
    {{"source": "", "relationship": "", "target": ""}}
  ]
}}

Text:
{chunk}
"""


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    if not text.strip():
        raise ValueError(
            "No extractable text found in this PDF. "
            "It may be a scanned/image-only PDF that needs OCR."
        )
    return text


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_text(text)


def extract_graph_from_chunk(chunk: str) -> dict:
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(chunk=chunk)
    data = generate_json(prompt)
    data.setdefault("entities", [])
    data.setdefault("relationships", [])
    return data


def save_entities_and_relationships(data: dict):
    with driver.session() as session:
        for entity in data.get("entities", []):
            name = entity.get("name")
            etype = entity.get("type", "")
            if not name:
                continue
            session.run(
                """
                MERGE (e:Entity {name: $name})
                SET e.type = $type
                """,
                name=name,
                type=etype,
            )

        for rel in data.get("relationships", []):
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("relationship", "RELATED_TO")
            if not source or not target:
                continue
            session.run(
                """
                MERGE (a:Entity {name: $source})
                MERGE (b:Entity {name: $target})
                MERGE (a)-[r:RELATED_TO]->(b)
                SET r.type = $rel_type
                """,
                source=source,
                target=target,
                rel_type=rel_type,
            )


def save_chunk(chunk_text_value: str, entity_names: list):
    """Stores a chunk as its own node with an embedding, linked to the
    entities that were extracted from it (used to compute seed_entities /
    graph_triples relevance later, and to support vector search)."""
    chunk_id = str(uuid.uuid4())
    embedding = embed_text(chunk_text_value)

    with driver.session() as session:
        session.run(
            """
            CREATE (c:Chunk {id: $id, text: $text, embedding: $embedding})
            """,
            id=chunk_id,
            text=chunk_text_value,
            embedding=embedding,
        )
        for name in entity_names:
            session.run(
                """
                MATCH (c:Chunk {id: $chunk_id})
                MATCH (e:Entity {name: $name})
                MERGE (c)-[:MENTIONS]->(e)
                """,
                chunk_id=chunk_id,
                name=name,
            )
    return chunk_id


def ingest_pdf(path: str) -> dict:
    """Full pipeline. Returns a summary dict."""
    text = extract_text_from_pdf(path)
    chunks = chunk_text(text)

    total_entities = 0
    total_relationships = 0
    failed_chunks = 0

    for chunk in chunks:
        try:
            data = extract_graph_from_chunk(chunk)
        except ValueError:
             
             
            failed_chunks += 1
            continue

        save_entities_and_relationships(data)
        entity_names = [e["name"] for e in data.get("entities", []) if e.get("name")]
        save_chunk(chunk, entity_names)


        total_entities += len(data.get("entities", []))
        total_relationships += len(data.get("relationships", []))

    return {
    "chunks_processed": len(chunks),
    "chunks_failed": failed_chunks,
    "entities_extracted": total_entities,
    "relationships_extracted": total_relationships,
    }
