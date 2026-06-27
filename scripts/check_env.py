"""Local smoke test (B's helper, not tracked): imports resolve, protobuf is in the
6.31.x sweet spot, and A's app modules load. Run after scripts/install.sh.

    .venv/Scripts/python scripts/check_env.py
"""
import sys
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

# Running a script puts scripts/ on sys.path, not the repo root — add the root so `app` imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def v(pkg: str) -> str:
    try:
        return version(pkg)
    except PackageNotFoundError:
        return "MISSING"


def main() -> int:
    print("== package versions ==")
    for p in ["fastapi", "starlette", "uvicorn", "anthropic", "openai", "tiktoken",
              "actian-vectorai-client", "scalekit-sdk-python", "protobuf", "grpcio-status"]:
        print(f"  {p:28} {v(p)}")

    print("\n== protobuf window check (>=6.31.1 for Actian, <7.0.0 for scalekit) ==")
    pb = v("protobuf")
    parts = tuple(int(x) for x in pb.split(".")[:2]) if pb != "MISSING" else (0, 0)
    ok = (6, 31) <= parts < (7, 0)
    print(f"  protobuf {pb} in [6.31, 7.0) ? {'OK' if ok else 'FAIL'}")

    print("\n== imports (A's spine) ==")
    try:
        import actian_vectorai  # noqa: F401
        from scalekit.client import ScalekitClient  # noqa: F401
        import anthropic, openai, tiktoken  # noqa: F401
        from app.main import app  # noqa: F401
        from app import config, models, scalekit_client, vectorstore, embeddings, anthropic_client  # noqa: F401
        print("  all imports OK")
    except Exception as e:
        print(f"  IMPORT FAILED: {e}")
        return 1

    print("\n== config (A's Settings) ==")
    from app.config import settings
    print(f"  DEMO_USER_ID   = {settings.DEMO_USER_ID}")
    print(f"  VECTORAI_HOST  = {settings.VECTORAI_HOST}")
    print(f"  EMBED_MODEL    = {settings.EMBED_MODEL} (dim {settings.EMBED_DIM})")
    print(f"  AUDIT_CACHE    = {settings.AUDIT_CACHE_PATH}")
    missing = [k for k in ("SCALEKIT_CLIENT_ID", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")
               if not getattr(settings, k, "")]
    print(f"  missing keys   = {missing or 'none'}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
