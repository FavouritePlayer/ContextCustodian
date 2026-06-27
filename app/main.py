"""FastAPI app — the locked /audit and /fix contract (build doc section 4).

GET /audit serves cached or demo data depending on AUDIT_MODE and configured keys.
POST /audit/run ingests the real workspace when Scalekit + model keys are set.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.audit import resolve_get_audit, restore_demo_cache, run_audit
from app.config import settings
from app.dashboard_config import get_dashboard_config, live_pipeline_ready
from app.fixes import set_fixed
from app.models import AuditResponse, Finding, FixRequest

app = FastAPI(title="Context Custodian")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health")
def health() -> dict[str, object]:
    cache = Path(settings.AUDIT_CACHE_PATH)
    cfg = get_dashboard_config()
    return {
        "status": "ok",
        "audit_cache_present": cache.exists(),
        "demo_user_id": settings.DEMO_USER_ID,
        "audit_mode": cfg.audit_mode,
        "effective_mode": cfg.effective_mode,
        "live_ready": cfg.live_ready,
    }


@app.get("/config")
def get_config() -> dict:
    return get_dashboard_config().model_dump()


@app.get("/audit", response_model=AuditResponse, response_model_by_alias=True)
def get_audit(response: Response) -> AuditResponse:
    try:
        audit, source, needs_live = resolve_get_audit(settings.DEMO_USER_ID)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    response.headers["X-Custodian-Audit-Source"] = source
    if needs_live:
        response.headers["X-Custodian-Needs-Live-Run"] = "true"
    return audit


@app.post("/audit/run", response_model=AuditResponse, response_model_by_alias=True)
def run_live_audit(response: Response) -> AuditResponse:
    """Ingest the connected workspace and run all detection passes."""
    if not live_pipeline_ready():
        missing = get_dashboard_config().missing_for_live
        raise HTTPException(
            status_code=503,
            detail=f"live audit unavailable — set: {', '.join(missing)}",
        )
    try:
        audit = run_audit(settings.DEMO_USER_ID)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"live audit failed: {e}") from e
    response.headers["X-Custodian-Audit-Source"] = "live"
    return audit


@app.post("/audit/reset", response_model=AuditResponse, response_model_by_alias=True)
def reset_audit(response: Response) -> AuditResponse:
    """Restore the golden demo cache — demo rehearsals only."""
    cfg = get_dashboard_config()
    if not cfg.can_reset_demo:
        raise HTTPException(
            status_code=403,
            detail="reset disabled in live mode — set AUDIT_MODE=demo or remove live keys",
        )
    try:
        audit = restore_demo_cache()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    response.headers["X-Custodian-Audit-Source"] = "demo"
    return audit


@app.post("/fix", response_model=Finding, response_model_by_alias=True)
def post_fix(req: FixRequest, response: Response) -> Finding:
    """Run the finding's fix action as the user and mark it fixed in the cache.
    metrics_before is left as the immutable baseline; the UI derives the "after"
    number from fixed findings. X-Custodian-Fix-Mode reports whether the live
    Scalekit action ran ("workspace") or only the audit index updated ("index")."""
    try:
        finding, mode = set_fixed(req.finding_id, True, settings.DEMO_USER_ID)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"no finding {req.finding_id!r}")
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="no cached audit available to fix against")
    response.headers["X-Custodian-Fix-Mode"] = mode
    return finding


@app.post("/undo", response_model=Finding, response_model_by_alias=True)
def post_undo(req: FixRequest, response: Response) -> Finding:
    """Reverse a fix — every action is reversible by construction. Marks the
    finding unfixed and persists. (Additive to the locked contract; B-owned.)"""
    try:
        finding, mode = set_fixed(req.finding_id, False, settings.DEMO_USER_ID)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"no finding {req.finding_id!r}")
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="no cached audit available")
    response.headers["X-Custodian-Fix-Mode"] = mode
    return finding


# --- Dashboard (Person B): serve the compaction UI from the same public service ---
if STATIC_DIR.exists():
    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
