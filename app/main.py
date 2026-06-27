"""FastAPI app — the locked /audit and /fix contract (build doc section 4).

GET /audit serves cache/audit.json (seeded with mock findings matching the
fixture in section 6) until the real pipeline is run, so the UI is never
blocked on Person A. POST /fix is Person B's territory — stubbed so the
route shape is locked.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.audit import load_cached_audit, run_audit
from app.config import settings
from app.models import AuditResponse, Finding, FixRequest

app = FastAPI(title="Context Custodian")


@app.get("/audit", response_model=AuditResponse, response_model_by_alias=True)
def get_audit() -> AuditResponse:
    cached = load_cached_audit()
    if cached is not None:
        return cached
    return run_audit(settings.DEMO_USER_ID)


@app.post("/fix", response_model=Finding, response_model_by_alias=True)
def post_fix(req: FixRequest) -> Finding:
    # Person B: look up the Finding by req.finding_id, dispatch on
    # fix.action ("quarantine" | "collapse" | "revoke") via ScalekitClient,
    # update cache/audit.json's metrics_before to reflect the new doc/token
    # count, mark fixed=True, persist, and return the updated Finding.
    raise HTTPException(status_code=501, detail="not implemented — Person B builds /fix")
