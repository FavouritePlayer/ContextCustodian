"""Orchestrates ingestion + all detection passes into the /audit contract,
and writes the cached JSON so the demo never depends on a live re-run.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.corpus import CorpusManifest
from app.ingest import ingest_workspace
from app.metrics import compute_metrics
from app.models import AuditResponse
from app.passes.injection import run_injection_pass
from app.passes.redundancy import run_redundancy_pass
from app.passes.stale import run_stale_pass


def run_audit(user_id: str, manifest: CorpusManifest | None = None) -> AuditResponse:
    manifest = manifest or ingest_workspace(user_id)

    findings = []
    findings += run_injection_pass(user_id, manifest)
    findings += run_stale_pass(user_id, manifest)
    findings += run_redundancy_pass(user_id, manifest)

    response = AuditResponse(
        findings=findings,
        metrics_before=compute_metrics(manifest),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    _write_cache(response)
    return response


def demo_cache_path() -> Path:
    return Path(settings.AUDIT_CACHE_PATH).parent / "audit.demo.json"


def load_cached_audit() -> AuditResponse | None:
    path = Path(settings.AUDIT_CACHE_PATH)
    if not path.exists():
        return None
    return AuditResponse.model_validate_json(path.read_text(encoding="utf-8"))


def restore_demo_cache() -> AuditResponse:
    """Reset the live cache to the committed golden snapshot (all findings unfixed)."""
    src = demo_cache_path()
    dst = Path(settings.AUDIT_CACHE_PATH)
    if not src.exists():
        raise FileNotFoundError(f"golden demo cache missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    dst.write_text(text, encoding="utf-8")
    return AuditResponse.model_validate_json(text)


def _write_cache(response: AuditResponse) -> None:
    path = Path(settings.AUDIT_CACHE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
