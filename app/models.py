"""The locked contract (build doc section 4). Both A and B code against this —
do not change field names or the /audit, /fix shapes without re-syncing.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FixAction(BaseModel):
    action: Literal["quarantine", "collapse", "revoke"]
    target_file_ids: list[str]


class Finding(BaseModel):
    id: str
    pass_name: Literal["injection", "stale", "redundancy", "exposure"] = Field(alias="pass")
    severity: Literal["high", "med", "low"]
    title: str
    receipt: str
    file_ids: list[str]
    canonical_file_id: str | None = None  # redundancy only
    fix: FixAction
    fixed: bool = False

    model_config = {"populate_by_name": True}


class Metrics(BaseModel):
    doc_count: int
    ingestible_tokens: int


class AuditResponse(BaseModel):
    findings: list[Finding]
    metrics_before: Metrics
    generated_at: str


class FixRequest(BaseModel):
    finding_id: str
