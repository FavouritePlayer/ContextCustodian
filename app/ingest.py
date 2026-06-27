"""Scoped read -> chunk -> embed -> upsert into the user's Actian collection,
recording everything in the local manifest at the same time.
"""
from __future__ import annotations

from actian_vectorai import PointStruct

from app.chunking import chunk_text
from app.corpus import ChunkRecord, CorpusManifest, FileRecord
from app.embeddings import embed_texts
from app.scalekit_client import client_for
from app.vectorstore import upsert_points


def ingest_workspace(user_id: str) -> CorpusManifest:
    scalekit = client_for(user_id)
    files = scalekit.list_files()

    manifest = CorpusManifest()
    next_id = 0

    for f in files:
        text = scalekit.read_file(f.file_id)
        manifest.files.append(
            FileRecord(
                file_id=f.file_id,
                file_name=f.name,
                owner=f.owner,
                modified_time=f.modified_time,
                full_text=text,
            )
        )

        chunks = chunk_text(text)
        if not chunks:
            continue
        vectors = embed_texts(chunks)

        points = []
        for chunk, vector in zip(chunks, vectors):
            chunk_id = f"{f.file_id}-{next_id}"
            next_id += 1
            manifest.chunks.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    file_id=f.file_id,
                    file_name=f.name,
                    owner=f.owner,
                    modified_time=f.modified_time,
                    text=chunk,
                    vector=vector,
                )
            )
            # Actian point ids must be int/uuid-shaped; chunk_id (string) is
            # carried in the payload instead so it round-trips through search.
            point_id = abs(hash(chunk_id)) % (10**12)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk_id,
                        "file_id": f.file_id,
                        "file_name": f.name,
                        "owner": f.owner,
                        "modified_time": f.modified_time,
                        "text": chunk,
                    },
                )
            )

        upsert_points(user_id, points)

    manifest.save()
    return manifest
