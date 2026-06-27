"""Stale-poison quarantine.

For each doc, retrieve its nearest neighbors (same-topic candidates), then
LLM-adjudicate whether the pair asserts conflicting values for the same fact
and which one is outdated.
"""
from __future__ import annotations

import uuid

from app.anthropic_client import adjudicate
from app.corpus import CorpusManifest
from app.models import Finding, FixAction
from app.vectorstore import nearest

ADJUDICATION_PROMPT = """You are comparing two workspace documents that may describe the
same fact (e.g. a price, a date, a policy) differently.

Document A (modified {a_time}):
---
{a_text}
---

Document B (modified {b_time}):
---
{b_text}
---

Respond with strict JSON only, no markdown fence:
{{"flagged": true|false, "stale_doc": "A"|"B", "receipt": "<one sentence naming both values and which is current>"}}

Only flag true if they genuinely assert conflicting values for the same fact.
"""


def run_stale_pass(user_id: str, manifest: CorpusManifest) -> list[Finding]:
    findings: list[Finding] = []
    checked_pairs: set[frozenset[str]] = set()
    files_by_id = {f.file_id: f for f in manifest.files}

    for file in manifest.files:
        file_chunks = [c for c in manifest.chunks if c.file_id == file.file_id]
        if not file_chunks:
            continue

        for hit in nearest(user_id, file_chunks[0].vector, limit=5):
            other_file_id = hit["payload"].get("file_id")
            if not other_file_id or other_file_id == file.file_id:
                continue
            pair = frozenset({file.file_id, other_file_id})
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            other = files_by_id.get(other_file_id)
            if other is None:
                continue

            try:
                result = adjudicate(
                    ADJUDICATION_PROMPT.format(
                        a_time=file.modified_time,
                        a_text=file.full_text[:2000],
                        b_time=other.modified_time,
                        b_text=other.full_text[:2000],
                    )
                )
            except Exception:
                continue

            if not result.get("flagged"):
                continue

            stale_file = file if result.get("stale_doc") == "A" else other
            current_file = other if stale_file is file else file

            findings.append(
                Finding(
                    id=str(uuid.uuid4()),
                    pass_name="stale",
                    severity="high",
                    title=f'"{stale_file.file_name}" contradicts the current "{current_file.file_name}"',
                    receipt=result.get("receipt", ""),
                    file_ids=[stale_file.file_id, current_file.file_id],
                    fix=FixAction(action="quarantine", target_file_ids=[stale_file.file_id]),
                )
            )

    return findings
