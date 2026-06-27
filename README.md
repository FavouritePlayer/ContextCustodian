# 🧹 Context Custodian

Context compaction for an agent-first workspace. Removes the excess context other agents
would ingest — duplicate docs, stale-wrong docs, prompt-injection traps — acting **as you**,
with **your** permissions. Nothing is destroyed; everything is reversible.

See `Context_Custodian_MVP_4hr_Build.md` for the full build plan, contract, and demo script.

## Stack
- **Agent app**: FastAPI (`app/`), serves the static dashboard (`static/`)
- **Vectors**: Actian VectorAI DB (Docker, `docker-compose.yml`)
- **Act-as-user**: Scalekit SDK (`app/scalekit_client.py`)
- **LLM adjudication**: Anthropic API
- **Embeddings**: Voyage (`voyage-3`, dim 1024) — swap for OpenAI if preferred

## Setup

```bash
cp .env.example .env          # then fill in keys
bash setup.sh                 # venv + deps in the Appendix-A-safe order
```

> ⚠️ **Dependency order matters.** `scalekit-sdk-python` pins `protobuf<7.0.0`, which silently
> downgrades what `actian-vectorai-client` needs and breaks VectorAI writes (~30s later, no
> error at insert). `setup.sh` installs scalekit with `--no-deps`, then re-asserts
> `protobuf>=6.31.1` / `grpcio-status>=1.67.0`. This applies on Render too.

Verify the environment:

```bash
.venv/Scripts/python scripts/check_env.py
```

## Run Actian VectorAI (local)

```bash
docker compose up -d          # maps 6573-6575; client connects on localhost:6574
```

Get the **1M-vector trial key** (not the 5,000 Community default — writes fail silently at
the cap): <https://www.actian.com/databases/vectorai-db/community-edition/>

## Run the app

```bash
.venv/Scripts/python -m uvicorn app.main:app --reload
# http://localhost:8000  (dashboard)  ·  /audit  ·  /fix  ·  /health
```

## The one shared identity (MD §2)
`USER_ID` is used **both** as the Scalekit identifier **and** to name the Actian collection
(`user-<USER_ID>-memories`). That naming is the isolation proof — and qualifies for the
separate Actian "acts as a specific user" challenge.

## Contract (`app/schemas.py`, locked — do not drift)
- `GET /audit` → `{ findings: [Finding], metrics_before, metrics_after?, generated_at }`
  (serves `data/audit_cache.json` if present)
- `POST /fix { finding_id }` → runs `fix.action` as the user, returns updated `Finding` + new metrics

## Status
Scaffold + integrations wired. Detection passes, fix execution, fixture, and dashboard UI
are the person-split work (`TODO(person-split)` markers in `app/main.py`).
