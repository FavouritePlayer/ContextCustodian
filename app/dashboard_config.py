"""Dashboard / audit mode — demo vs live workspace based on environment."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.config import settings

AuditMode = Literal["demo", "live", "auto"]
EffectiveMode = Literal["demo", "live"]

_LIVE_KEYS = (
    "SCALEKIT_CLIENT_ID",
    "SCALEKIT_CLIENT_SECRET",
    "SCALEKIT_ENV_URL",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def live_pipeline_missing() -> list[str]:
    return [k for k in _LIVE_KEYS if not getattr(settings, k, "")]


def live_pipeline_ready() -> bool:
    return not live_pipeline_missing()


def effective_audit_mode() -> EffectiveMode:
    """Resolved mode: live when configured (auto/live), else demo."""
    mode = settings.AUDIT_MODE
    if mode == "demo":
        return "demo"
    return "live" if live_pipeline_ready() else "demo"


class DashboardConfig(BaseModel):
    user_id: str
    workspace_label: str
    audit_mode: AuditMode
    effective_mode: EffectiveMode
    live_ready: bool
    missing_for_live: list[str]
    can_reset_demo: bool
    can_run_live_audit: bool
    scalekit_configured: bool
    drive_connection: str
    docs_connection: str


def get_dashboard_config() -> DashboardConfig:
    ready = live_pipeline_ready()
    effective = effective_audit_mode()
    label = settings.WORKSPACE_LABEL.strip() or settings.DEMO_USER_ID
    return DashboardConfig(
        user_id=settings.DEMO_USER_ID,
        workspace_label=label,
        audit_mode=settings.AUDIT_MODE,
        effective_mode=effective,
        live_ready=ready,
        missing_for_live=live_pipeline_missing(),
        can_reset_demo=effective == "demo" or settings.AUDIT_MODE == "demo",
        can_run_live_audit=ready,
        scalekit_configured=bool(settings.SCALEKIT_CLIENT_ID),
        drive_connection=settings.GOOGLEDRIVE_CONNECTION_NAME,
        docs_connection=settings.GOOGLEDOCS_CONNECTION_NAME,
    )
