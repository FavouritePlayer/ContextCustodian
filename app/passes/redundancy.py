"""Redundancy collapse — cluster by embedding similarity (file vector = mean
of its chunk vectors), union-find on a cosine threshold, canonical = most
recently modified member of the cluster.
"""
from __future__ import annotations

import uuid

from app.corpus import CorpusManifest
from app.models import Finding, FixAction

SIMILARITY_THRESHOLD = 0.92


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _file_vector(manifest: CorpusManifest, file_id: str) -> list[float] | None:
    vectors = [c.vector for c in manifest.chunks if c.file_id == file_id]
    if not vectors:
        return None
    dim = len(vectors[0])
    return [sum(v[i] for v in vectors) / len(vectors) for i in range(dim)]


def run_redundancy_pass(user_id: str, manifest: CorpusManifest) -> list[Finding]:
    file_ids = [f.file_id for f in manifest.files]
    vectors = {fid: v for fid in file_ids if (v := _file_vector(manifest, fid)) is not None}

    parent = {fid: fid for fid in vectors}

    def find(x: str) -> str:
        while parent[x] != x:
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        parent[find(x)] = find(y)

    ids = list(vectors.keys())
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if _cosine(vectors[ids[i]], vectors[ids[j]]) >= SIMILARITY_THRESHOLD:
                union(ids[i], ids[j])

    clusters: dict[str, list[str]] = {}
    for fid in ids:
        clusters.setdefault(find(fid), []).append(fid)

    files_by_id = {f.file_id: f for f in manifest.files}
    findings = []
    for members in clusters.values():
        if len(members) < 2:
            continue
        canonical = max(members, key=lambda fid: files_by_id[fid].modified_time)
        non_canonical = [fid for fid in members if fid != canonical]
        names = ", ".join(f'"{files_by_id[fid].file_name}"' for fid in members)

        findings.append(
            Finding(
                id=str(uuid.uuid4()),
                pass_name="redundancy",
                severity="med",
                title=f"{len(members)} near-duplicate versions of the same doc",
                receipt=f"Near-identical content across: {names}. Keeping the most recently modified as canonical.",
                file_ids=members,
                canonical_file_id=canonical,
                fix=FixAction(action="collapse", target_file_ids=non_canonical),
            )
        )

    return findings
