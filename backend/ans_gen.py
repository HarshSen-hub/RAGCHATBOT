from .gemini_client import client
from .config import GEMINI_TEXT_MODEL

RAG_PROMPT_TEMPLATE = """
You are an AI assistant answering questions about the user's documents.

Rules:
1. Use ONLY the information given in the context.
2. Do not make up facts.
3. If the answer is not present, reply exactly:
"I don't have enough information in the knowledge graph."

Context:
{context}

Question:
{question}

Answer:
"""

GENERAL_PROMPT_TEMPLATE = """
You are a friendly, helpful AI assistant inside a document chat app.
No relevant document context was found for this message, so just respond
naturally and conversationally — greetings, small talk, general knowledge
questions, etc. Keep it brief and warm.

Message:
{question}

Answer:
"""


def generate_answer(question: str, context: str) -> str:
    has_context = bool(context and context.strip())

    prompt = (
        RAG_PROMPT_TEMPLATE.format(context=context, question=question)
        if has_context
        else GENERAL_PROMPT_TEMPLATE.format(question=question)
    )

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
    )
    return response.text.strip()