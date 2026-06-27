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

QUARANTINE_FOLDER = "/Quarantine"   # injection / stale: de-index, move out of the ingestible surface
ARCHIVE_FOLDER = "/Archive"         # redundancy: keep canonical, archive the rest with a pointer


def apply_fix(finding: Finding, user_id: str) -> str:
    """Run finding.fix.action as the user. Returns "workspace" if the live Scalekit
    action ran, or "index" if Scalekit isn't wired yet (audit/index updated only).
    Real errors propagate; only the not-yet-implemented stubs fall back to "index"."""
    sk = client_for(user_id)
    action = finding.fix.action
    targets = finding.fix.target_file_ids
    try:
        if action in ("quarantine", "collapse"):
            folder = QUARANTINE_FOLDER if action == "quarantine" else ARCHIVE_FOLDER
            for file_id in targets:
                sk.move_file(file_id, folder)        # reversible: a move, never a delete
        elif action == "revoke":
            for file_id in targets:
                for grant in sk.list_permissions(file_id):
                    sk.revoke_permission(file_id, grant["id"])
        else:
            raise ValueError(f"unknown fix action: {action!r}")
        return "workspace"
    except NotImplementedError:
        return "index"   # connect spike pending — see app/scalekit_client.py stubs


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
