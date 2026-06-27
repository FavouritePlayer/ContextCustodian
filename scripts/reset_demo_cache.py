"""Reset cache/audit.json to the golden demo snapshot (Person B step 5).

Use before each demo rehearsal so all four hero findings start unfixed.

    .venv/Scripts/python scripts/reset_demo_cache.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.audit import restore_demo_cache


def main() -> int:
    audit = restore_demo_cache()
    print(f"Restored {len(audit.findings)} findings (all fixed=false)")
    print(f"Baseline: {audit.metrics_before.doc_count} docs, "
          f"{audit.metrics_before.ingestible_tokens:,} tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
