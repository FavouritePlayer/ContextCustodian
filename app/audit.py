"""Orchestrates ingestion + all detection passes into the /audit contract,
and writes the cached JSON so the demo never depends on a live re-run.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from app.config import settings
from app.corpus import CorpusManifest
from app.dashboard_config import effective_audit_mode, live_pipeline_ready
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
    _write_cache(response, source="live")
    return response


def _meta_path() -> Path:
    return Path(settings.AUDIT_CACHE_PATH).parent / "audit.meta.json"


def read_cache_meta() -> dict:
    path = _meta_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_cache_meta(source: str) -> None:
    path = _meta_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"source": source}, indent=2), encoding="utf-8")


def is_demo_cache() -> bool:
    meta = read_cache_meta()
    if meta.get("source") == "demo":
        return True
    if meta.get("source") == "live":
        return False
    cached = load_cached_audit()
    demo = load_demo_audit()
    if cached is None or demo is None:
        return False
    return _audit_payload(cached) == _audit_payload(demo)


def _audit_payload(audit: AuditResponse) -> str:
    data = audit.model_dump(by_alias=True)
    data.pop("generated_at", None)
    for f in data.get("findings", []):
        f.pop("fixed", None)
    return json.dumps(data, sort_keys=True)


def load_demo_audit() -> AuditResponse | None:
    path = demo_cache_path()
    if not path.exists():
        return None
    return AuditResponse.model_validate_json(path.read_text(encoding="utf-8"))


def load_demo_audit_or_raise() -> AuditResponse:
    audit = load_demo_audit()
    if audit is None:
        raise FileNotFoundError(f"golden demo cache missing: {demo_cache_path()}")
    return audit


def resolve_get_audit(user_id: str) -> tuple[AuditResponse, str, bool]:
    """Return (audit, source_header, needs_live_run).

    source_header is cache | live | demo.
    needs_live_run is True when live mode is active but only demo data is available.
    """
    if effective_audit_mode() == "demo":
        cached = load_cached_audit()
        if cached is not None:
            return cached, "cache", False
        return load_demo_audit_or_raise(), "demo", False

    cached = load_cached_audit()
    if cached is not None and not is_demo_cache():
        return cached, "cache", False

    if not live_pipeline_ready():
        if cached is not None:
            return cached, "cache", True
        demo = load_demo_audit()
        if demo is not None:
            return demo, "demo", True
        raise FileNotFoundError("no audit cache and live pipeline not configured")

    # Live/auto + keys set, but cache is still the demo snapshot — caller should run live.
    if cached is not None:
        return cached, "demo", True

    return run_audit(user_id), "live", False


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
    write_cache_meta("demo")
    return AuditResponse.model_validate_json(text)


def _write_cache(response: AuditResponse, *, source: str = "live") -> None:
    path = Path(settings.AUDIT_CACHE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
    write_cache_meta(source)
