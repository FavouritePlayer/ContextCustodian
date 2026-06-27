import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DEMO_USER_ID = os.environ.get("DEMO_USER_ID", "demo-user-1")

    SCALEKIT_CLIENT_ID = os.environ.get("SCALEKIT_CLIENT_ID", "")
    SCALEKIT_CLIENT_SECRET = os.environ.get("SCALEKIT_CLIENT_SECRET", "")
    SCALEKIT_ENV_URL = os.environ.get("SCALEKIT_ENV_URL", "")
    GOOGLEDRIVE_CONNECTION_NAME = os.environ.get("GOOGLEDRIVE_CONNECTION_NAME", "googledrive")
    GOOGLEDOCS_CONNECTION_NAME = os.environ.get("GOOGLEDOCS_CONNECTION_NAME", "googledocs")

    VECTORAI_HOST = os.environ.get("VECTORAI_HOST", "localhost:6574")

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
    EMBED_DIM = int(os.environ.get("EMBED_DIM", "1536"))

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    AUDIT_CACHE_PATH = os.environ.get("AUDIT_CACHE_PATH", "cache/audit.json")

    # demo — always mock cache | live — real workspace when keys set | auto — live if keys set else demo
    AUDIT_MODE = os.environ.get("AUDIT_MODE", "auto").strip().lower()
    if AUDIT_MODE not in ("demo", "live", "auto"):
        AUDIT_MODE = "auto"

    # Sidebar / topbar display name (defaults to DEMO_USER_ID)
    WORKSPACE_LABEL = os.environ.get("WORKSPACE_LABEL", "")

    QUARANTINE_FOLDER_ID = os.environ.get("QUARANTINE_FOLDER_ID", "")
    ARCHIVE_FOLDER_ID = os.environ.get("ARCHIVE_FOLDER_ID", "")


settings = Settings()
