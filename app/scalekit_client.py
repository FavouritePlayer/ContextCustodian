"""Scalekit integration boundary.

Everything else in this codebase talks to Scalekit only through the methods
below. The exact scalekit-sdk-python call shapes are NOT confirmed yet — the
AgentKit guide is a Notion page that needs a browser, so fill in the method
bodies during the 0:35 connect spike (or with a mentor on-site). Until then
this raises NotImplementedError on purpose rather than guessing at an API
surface, so a wrong call doesn't fail silently later.

Install: see scripts/install.sh (protobuf conflict with actian-vectorai-client).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.config import settings


@dataclass
class WorkspaceFile:
    file_id: str
    name: str
    owner: str
    modified_time: str
    sharing: dict = field(default_factory=dict)  # e.g. {"anyone_with_link": bool, "external_collaborators": [...]}


class ScalekitClient:
    """One instance per user_id — the same string used for the Actian
    collection name (vectorstore.collection_name)."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._token = None  # TODO(connect spike): exchange + cache a per-user token

    def list_files(self) -> list[WorkspaceFile]:
        """Scoped read: every file the user can see, with sharing metadata.
        Used by app.ingest to build the corpus.
        """
        raise NotImplementedError("wire up after the 0:35 Scalekit connect spike")

    def read_file(self, file_id: str) -> str:
        """Scoped read: full text content of one file."""
        raise NotImplementedError("wire up after the 0:35 Scalekit connect spike")

    def list_permissions(self, file_id: str) -> list[dict]:
        """Exposure pass input — not in Person A's scope, stub for Person B."""
        raise NotImplementedError("Person B: exposure pass")

    def revoke_permission(self, file_id: str, grant_id: str) -> None:
        """Fix action for exposure — Person B builds this in POST /fix."""
        raise NotImplementedError("Person B: /fix revoke action")

    def move_file(self, file_id: str, target_folder: str) -> None:
        """Fix action for quarantine/collapse — Person B builds this in POST /fix."""
        raise NotImplementedError("Person B: /fix quarantine/collapse action")


def client_for(user_id: str = settings.DEMO_USER_ID) -> ScalekitClient:
    return ScalekitClient(user_id)
