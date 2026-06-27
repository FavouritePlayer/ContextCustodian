"""FastAPI app — the locked /audit and /fix contract (build doc section 4).

GET /audit serves cache/audit.json (seeded with mock findings matching the
fixture in section 6) until the real pipeline is run, so the UI is never
blocked on Person A. POST /fix is Person B's territory — stubbed so the
route shape is locked.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.audit import load_cached_audit, run_audit
from app.config import settings
from app.fixes import set_fixed
from app.models import AuditResponse, Finding, FixRequest

app = FastAPI(title="Context Custodian")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/audit", response_model=AuditResponse, response_model_by_alias=True)
def get_audit() -> AuditResponse:
    cached = load_cached_audit()
    if cached is not None:
        return cached
    return run_audit(settings.DEMO_USER_ID)


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
