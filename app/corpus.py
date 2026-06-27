"""Local corpus manifest, written during ingestion alongside the Actian
upsert. Actian backs nearest-neighbor search (injection, stale passes); this
manifest backs whole-corpus operations — redundancy clustering and the
before/after metrics — without round-tripping the vector store for every doc.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from app.config import settings


class ChunkRecord(BaseModel):
    chunk_id: str
    file_id: str
    file_name: str
    owner: str
    modified_time: str
    text: str
    vector: list[float]


class FileRecord(BaseModel):
    file_id: str
    file_name: str
    owner: str
    modified_time: str
    full_text: str


class CorpusManifest(BaseModel):
    files: list[FileRecord] = []
    chunks: list[ChunkRecord] = []

    def save(self, path: Path | None = None) -> None:
        path = path or Path(settings.AUDIT_CACHE_PATH).parent / "corpus_manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Path | None = None) -> "CorpusManifest":
        path = path or Path(settings.AUDIT_CACHE_PATH).parent / "corpus_manifest.json"
        if not path.exists():
            return cls()
        return cls.model_validate_json(path.read_text())
