
import json
from google import genai
from .config import GOOGLE_API_KEY, GEMINI_TEXT_MODEL, GEMINI_EMBED_MODEL

client = genai.Client(api_key=GOOGLE_API_KEY)


def _clean_json_text(raw: str) -> str:
    text = raw.strip()
    text = text.replace("```json", "").replace("```", "")
    return text.strip()


def generate_json(prompt: str, retries: int = 1):
    """
    Sends `prompt` to Gemini and parses the response as JSON.
    Retries once (with a stricter reminder) if parsing fails.
    Raises ValueError if it still can't parse after retries.
    """
    last_error = None
    attempt_prompt = prompt

    for attempt in range(retries + 1):
        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=attempt_prompt,
        )
        cleaned = _clean_json_text(response.text or "")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            last_error = e
            attempt_prompt = (
                prompt
                + "\n\nIMPORTANT: Your last response was not valid JSON. "
                  "Return ONLY valid JSON, no markdown fences, no explanations."
            )

    raise ValueError(f"Gemini did not return valid JSON after {retries + 1} attempts: {last_error}")


def embed_text(text: str):
    """Returns an embedding vector (list of floats) for the given text."""
    result = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=text,
    )
    embedding_obj = result.embeddings[0]
    return list(embedding_obj.values)
