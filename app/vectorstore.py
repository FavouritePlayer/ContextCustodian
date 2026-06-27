"""Actian VectorAI wrapper — one collection per user, named off the same
string Scalekit uses as that user's id. That shared string is the entire
isolation mechanism: there is no built-in cross-user enforcement, just the
naming convention.

API surface below confirmed against actian-vectorai-client==1.0.1 installed
locally (it's Qdrant-shaped: collections.get_or_create, points.upsert,
points.search, points.scroll_all all exist as documented).
"""
from __future__ import annotations

from actian_vectorai import (
    Distance,
    PointStruct,
    RetrievedPoint,
    ScoredPoint,
    VectorAIClient,
    VectorParams,
)

from app.config import settings

_client: VectorAIClient | None = None


def get_client() -> VectorAIClient:
    global _client
    if _client is None:
        _client = VectorAIClient(settings.VECTORAI_HOST)
        _client.connect()
    return _client


def collection_name(user_id: str) -> str:
    return f"user-{user_id}-memories"


def get_or_create_user_collection(user_id: str, dim: int = settings.EMBED_DIM) -> str:
    name = collection_name(user_id)
    get_client().collections.get_or_create(
        name,
        vectors_config=VectorParams(size=dim, distance=Distance.Cosine),
    )
    return name


def upsert_points(user_id: str, points: list[PointStruct]) -> None:
    name = get_or_create_user_collection(user_id)
    get_client().points.upsert(name, points)


def search(user_id: str, vector: list[float], limit: int = 5) -> list[ScoredPoint]:
    name = get_or_create_user_collection(user_id)
    return get_client().points.search(name, vector, limit=limit)


def nearest(user_id: str, vector: list[float], limit: int = 5) -> list[dict]:
    """Normalized neighbor list: [{"payload": {...}, "score": float}, ...]."""
    return [{"payload": hit.payload or {}, "score": hit.score} for hit in search(user_id, vector, limit)]


def scroll_all(user_id: str) -> list[RetrievedPoint]:
    """Every point in the user's collection — used as a fallback if the local
    corpus manifest (app/corpus.py) is unavailable. Not needed in the normal
    path since ingestion writes the manifest at the same time as the upsert.
    """
    name = get_or_create_user_collection(user_id)
    points: list[RetrievedPoint] = []
    for batch in get_client().points.scroll_all(name):
        points.extend(batch)
    return points
