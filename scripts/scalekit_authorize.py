"""Run once per user_id before ingestion: creates/checks the connected
accounts for both Drive and Docs, and if not ACTIVE, prints the OAuth link
to open in a browser. Re-run after authorizing each to confirm ACTIVE.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.scalekit_client import client_for

if __name__ == "__main__":
    client = client_for(settings.DEMO_USER_ID)
    print(f"user_id: {client.user_id}")
    for connection_name, status in client.ensure_authorized().items():
        print(f"\n[{connection_name}]\n{status}")
