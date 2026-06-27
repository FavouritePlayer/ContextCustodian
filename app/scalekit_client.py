"""Scalekit integration boundary — Google Drive via the AgentKit proxy.

Pattern confirmed against the official Scalekit hackathon guide and
docs.scalekit.com: one ScalekitClient, actions.get_or_create_connected_account
+ actions.get_authorization_link for the OAuth handshake (run once per
user_id via scripts/scalekit_authorize.py), then actions.request() as a
generic authenticated proxy to the provider's REST API — `path` is relative
to the connector's API base, same paths as calling the Google Drive API v3
directly, Scalekit injects the token.

list_files/read_file (Person A's ingestion path) are exercised by
scripts/scalekit_authorize.py and known-correct. list_permissions/
revoke_permission/move_file (Person B's /fix + exposure-pass territory) use
the same confirmed proxy pattern but the PATCH/DELETE call shape isn't
shown in the guide (only GET is) — smoke-test those before relying on them.

Install: see scripts/install.sh (protobuf conflict with actian-vectorai-client).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from scalekit import ScalekitClient as _ScalekitSDK

from app.config import settings


@dataclass
class WorkspaceFile:
    file_id: str
    name: str
    owner: str
    modified_time: str
    sharing: dict = field(default_factory=dict)  # {"mime_type": str, "permissions": [...]}


_sdk: _ScalekitSDK | None = None


def _get_sdk() -> _ScalekitSDK:
    global _sdk
    if _sdk is None:
        _sdk = _ScalekitSDK(
            client_id=settings.SCALEKIT_CLIENT_ID,
            client_secret=settings.SCALEKIT_CLIENT_SECRET,
            env_url=settings.SCALEKIT_ENV_URL,
        )
    return _sdk


class ScalekitClient:
    """One instance per user_id — the same string used for the Actian
    collection name (vectorstore.collection_name). Tracks two connections:
    Drive (enumeration, sharing, location — used for everything in this
    file) and Docs (kept authorized for B/future use; Drive's own
    /export endpoint already covers Google Doc content for read_file
    below, so Docs isn't load-bearing for ingestion right now)."""

    CONNECTION_NAME = settings.GOOGLEDRIVE_CONNECTION_NAME
    DOCS_CONNECTION_NAME = settings.GOOGLEDOCS_CONNECTION_NAME

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.actions = _get_sdk().actions

    def _ensure_connection_authorized(self, connection_name: str) -> str:
        response = self.actions.get_or_create_connected_account(
            connection_name=connection_name,
            identifier=self.user_id,
        )
        connected_account = response.connected_account
        if connected_account.status != "ACTIVE":
            link_response = self.actions.get_authorization_link(
                connection_name=connection_name,
                identifier=self.user_id,
            )
            return f"NOT AUTHORIZED — open this link and authorize: {link_response.link}"
        return "ACTIVE"

    def ensure_authorized(self) -> dict[str, str]:
        """Returns {connection_name: status_or_link} for both Drive and
        Docs. Run via scripts/scalekit_authorize.py before the first ingest
        for a user_id — re-run after clicking each link to confirm ACTIVE.
        """
        return {
            self.CONNECTION_NAME: self._ensure_connection_authorized(self.CONNECTION_NAME),
            self.DOCS_CONNECTION_NAME: self._ensure_connection_authorized(self.DOCS_CONNECTION_NAME),
        }

    def _request(self, path: str, method: str = "GET", params: dict | None = None) -> dict:
        return self.actions.request(
            connection_name=self.CONNECTION_NAME,
            identifier=self.user_id,
            path=path,
            method=method,
            params=params or {},
        )

    def list_files(self) -> list[WorkspaceFile]:
        """Scoped read: every non-trashed file the user can see. Owner,
        modified time, mime type, and permissions all come back in one
        files.list call — Drive includes `permissions` in the fields mask
        without a separate per-file request.
        """
        result = self._request(
            "/drive/v3/files",
            params={
                "q": "trashed = false",
                "pageSize": 1000,
                "fields": "files(id,name,mimeType,modifiedTime,owners,permissions)",
            },
        )
        files = []
        for f in result.get("files", []):
            owners = f.get("owners") or []
            files.append(
                WorkspaceFile(
                    file_id=f["id"],
                    name=f["name"],
                    owner=owners[0]["emailAddress"] if owners else "",
                    modified_time=f.get("modifiedTime", ""),
                    sharing={
                        "mime_type": f.get("mimeType"),
                        "permissions": f.get("permissions", []),
                    },
                )
            )
        return files

    def read_file(self, file_id: str) -> str:
        """Scoped read: full text content of one file. Google-native docs
        (Docs/Sheets/Slides — mimeType prefix application/vnd.google-apps.)
        need /export; everything else downloads via alt=media.
        """
        meta = self._request(f"/drive/v3/files/{file_id}", params={"fields": "mimeType"})
        mime_type = meta.get("mimeType", "")

        if mime_type.startswith("application/vnd.google-apps."):
            result = self._request(
                f"/drive/v3/files/{file_id}/export",
                params={"mimeType": "text/plain"},
            )
        else:
            result = self._request(f"/drive/v3/files/{file_id}", params={"alt": "media"})

        return result if isinstance(result, str) else result.get("text", str(result))

    def list_permissions(self, file_id: str) -> list[dict]:
        """Exposure pass input — Person B's territory."""
        result = self._request(
            f"/drive/v3/files/{file_id}/permissions",
            params={"fields": "permissions(id,type,role,emailAddress,domain)"},
        )
        return result.get("permissions", [])

    def revoke_permission(self, file_id: str, grant_id: str) -> None:
        """Fix action for exposure — Person B's /fix territory."""
        self._request(f"/drive/v3/files/{file_id}/permissions/{grant_id}", method="DELETE")

    def move_file(self, file_id: str, target_folder_id: str) -> None:
        """Fix action for quarantine/collapse — Person B's /fix territory.
        target_folder_id must be a real Drive folder ID — create /Quarantine
        and /Archive folders once and note their IDs.
        """
        meta = self._request(f"/drive/v3/files/{file_id}", params={"fields": "parents"})
        current_parents = ",".join(meta.get("parents", []))
        self._request(
            f"/drive/v3/files/{file_id}",
            method="PATCH",
            params={"addParents": target_folder_id, "removeParents": current_parents},
        )


def client_for(user_id: str = settings.DEMO_USER_ID) -> ScalekitClient:
    return ScalekitClient(user_id)
