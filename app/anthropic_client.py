"""Shared LLM-adjudication call. Each pass supplies its own prompt template
and expects a strict-JSON object back, e.g. {"flagged": bool, "receipt": str}.
"""
import json

from anthropic import Anthropic

from app.config import settings

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY not set — fill in .env before running detection passes")
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def adjudicate(prompt: str) -> dict:
    resp = _get_client().messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return json.loads(text)
