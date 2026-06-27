"""Fix dispatch (Person B's territory).

POST /fix runs a finding's fix action AS the user via Scalekit, then marks the
finding fixed in the cached audit. The Scalekit act-as-user calls
(move_file / revoke_permission) are still stubs (NotImplementedError) until the
0:35 connect spike + creds land, so apply_fix attempts them and reports back
whether the live workspace action ran ("workspace") or only the audit index was
updated ("index"). No overclaiming: the UI shows which actually happened.
"""
from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models import AuditResponse, Finding
from app.scalekit_client import client_for

QUARANTINE_FOLDER_ID = settings.QUARANTINE_FOLDER_ID
ARCHIVE_FOLDER_ID = settings.ARCHIVE_FOLDER_ID


def apply_fix(finding: Finding, user_id: str) -> str:
    """Run finding.fix.action as the user via Scalekit. Returns:
      "workspace" — the live Drive action actually ran, or
      "index"     — audit/index updated only (Scalekit not configured here, the
                    connected account isn't authorized, the mock cache's file_ids
                    aren't real Drive ids, or a destination folder id isn't set).
    A's Scalekit calls are real now but go live only once .env has creds + the
    account is ACTIVE + cache/audit.json holds real Drive file_ids. Until then we
    degrade to index mode so the demo stays honest (the UI labels it accordingly)."""
    if not settings.SCALEKIT_CLIENT_ID:
        return "index"   # Scalekit not configured on this machine

    action = finding.fix.action
    targets = finding.fix.target_file_ids
    try:
        sk = client_for(user_id)
        if action in ("quarantine", "collapse"):
            folder_id = QUARANTINE_FOLDER_ID if action == "quarantine" else ARCHIVE_FOLDER_ID
            if not folder_id:
                return "index"                       # destination folder not configured yet
            for file_id in targets:
                sk.move_file(file_id, folder_id)     # reversible: a move, never a delete
        elif action == "revoke":
            for file_id in targets:
                for grant in sk.list_permissions(file_id):
                    if grant.get("type") == "anyone":  # revoke the public link (safe, unambiguous)
                        sk.revoke_permission(file_id, grant["id"])
                    # per-user external revocation is refined in the exposure pass (Task 5)
        else:
            raise ValueError(f"unknown fix action: {action!r}")
        return "workspace"
    except Exception as e:  # not-authorized / fake mock ids / unconfirmed PATCH-DELETE shape
        print(f"[fix] live Scalekit action fell back to index mode: {e!r}")
        return "index"


def persist_audit(audit: AuditResponse) -> None:
    """Write the audit back to the cache. encoding= is explicit so non-ASCII content
    round-trips on Windows (A's helpers omit it — flagged in COMMUNICATIONS_FOR_A)."""
    path = Path(settings.AUDIT_CACHE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(audit.model_dump_json(by_alias=True, indent=2), encoding="utf-8")


def set_fixed(finding_id: str, fixed: bool, user_id: str) -> tuple[Finding, str]:
    """Load the cached audit, flip one finding's fixed state, persist, and return
    (finding, mode). Raises KeyError if the finding id isn't in the cache."""
    from app.audit import load_cached_audit

    audit = load_cached_audit()
    if audit is None:
        raise FileNotFoundError("no cached audit to fix against")
    finding = next((f for f in audit.findings if f.id == finding_id), None)
    if finding is None:
        raise KeyError(finding_id)

    mode = "reverted"
    if fixed and not finding.fixed:
        mode = apply_fix(finding, user_id)
    finding.fixed = fixed
    persist_audit(audit)
    return finding, mode
