import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_ID = os.getenv("NEO4J_ID")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

GEMINI_TEXT_MODEL = "gemini-2.5-flash"
GEMINI_EMBED_MODEL = "gemini-embedding-001"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_CHUNKS = 4

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing from your .env file")
if not (NEO4J_URI and NEO4J_ID and NEO4J_PASSWORD):
    raise RuntimeError("NEO4J_URI / NEO4J_ID / NEO4J_PASSWORD missing from your .env file")
