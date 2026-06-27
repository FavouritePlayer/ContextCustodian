"""Build the seeded fixture (MD §6).

Reads fixtures/files.json (the source of truth), then:
  1. materializes each doc as a real text file under fixtures/docs/  (uploadable to
     Drive/Notion later for the live Scalekit-read pipeline), and
  2. emits cache/corpus_manifest.json in A's CorpusManifest/FileRecord schema, so
     offline operations (before/after metrics, POST /fix) work with no creds.

The manifest carries text only (A's FileRecord shape); 'sharing'/'folder' stay in
files.json for the exposure pass (Task 5). Chunks/vectors are left empty — those need
embeddings + Actian and are produced by A's app/ingest.py once keys land.

Run:  .venv/Scripts/python fixtures/build_manifest.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.corpus import CorpusManifest, FileRecord       # noqa: E402
from app.metrics import compute_metrics                  # noqa: E402
from app.chunking import count_tokens                    # noqa: E402

FIXTURE = ROOT / "fixtures" / "files.json"
DOCS_DIR = ROOT / "fixtures" / "docs"

# A's corpus.save()/load() use write_text/read_text without encoding= , so on Windows
# (cp1252 default) any non-ASCII char breaks the round-trip. Normalize fixture output to
# ASCII so the manifest is portable through A's code as-is. (Flagged to A separately.)
_ASCII = {"–": "-", "—": "-", "→": "->", "‘": "'", "’": "'",
          "“": '"', "”": '"', "…": "...", "·": "|", "•": "-"}


def ascii_clean(s: str) -> str:
    for k, v in _ASCII.items():
        s = s.replace(k, v)
    return s.encode("ascii", "ignore").decode("ascii")


def build() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    files = data["files"]
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for f in files:
        body = ascii_clean("\n".join(f["body"]))
        (DOCS_DIR / f["file_name"]).write_text(body, encoding="utf-8")   # materialize raw doc
        records.append(FileRecord(
            file_id=f["file_id"],
            file_name=f["file_name"],
            owner=f["owner"],
            modified_time=f["modified_time"],
            full_text=body,
        ))

    manifest = CorpusManifest(files=records)
    manifest.save()                                                      # -> cache/corpus_manifest.json
    metrics = compute_metrics(manifest)

    # ---- report ----
    heroes = [f for f in files if f.get("hero")]
    exposure = [f for f in files if f["sharing"].get("anyone_with_link") or f["sharing"].get("external_collaborators")]
    print(f"Built {len(records)} docs from {FIXTURE.name}")
    print(f"  raw docs   -> {DOCS_DIR.relative_to(ROOT)}/ ({len(records)} files)")
    print(f"  manifest   -> cache/corpus_manifest.json")
    print(f"\nFixture metrics (real, from tiktoken): {metrics.doc_count} docs | {metrics.ingestible_tokens:,} tokens")
    print(f"(Headline 240 docs / 1.8M tokens stays the whole-workspace baseline in cache/audit.json.)")

    print("\nPlanted heroes:")
    for f in heroes:
        toks = count_tokens("\n".join(f["body"]))
        print(f"  [{f['hero']:<20}] {f['file_id']:<18} {f['file_name']:<28} {toks:>4} tok")

    print("\nExposure-pass candidates (for Task 5):")
    for f in exposure:
        bits = []
        if f["sharing"].get("anyone_with_link"):
            bits.append(f"anyone-with-link since {f['sharing'].get('link_shared_since','?')}")
        if f["sharing"].get("external_collaborators"):
            bits.append("external: " + ", ".join(f["sharing"]["external_collaborators"]))
        print(f"  {f['file_id']:<18} {f['file_name']:<22} ({f['folder']}) - {'; '.join(bits)}")


if __name__ == "__main__":
    build()
