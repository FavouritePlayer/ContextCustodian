# Communications for B

_Inbox for Person B — A leaves messages here. B never writes here._

## How to use this file

1. **Ingest on start.** Whenever you (B) begin or resume a work session, read this file in full before doing anything else.
2. **Pop after reading.** Once you've read and acted on everything in the Messages section below, delete those entries so the section returns to empty. The next time you ingest, you should only ever see messages written since your last pop — never re-process something you've already handled.
3. **Reaching A.** Do not write a reply here. Append it to `COMMUNICATIONS_FOR_A.md` instead — this file only ever receives messages, it never sends them.
4. **Keep this section.** The "How to use this file" instructions above are permanent — only the Messages section below gets popped.

---

## Messages

### 2026-06-27 — from A

Spine + Person A detection engine is built and tested. You're unblocked:

- **Locked contract**: `app/models.py` (Finding/FixAction), `GET /audit` + `POST /fix` live in `app/main.py`.
- **Mock data ready now**: `cache/audit.json` is seeded with the four hero findings (injection, stale, redundancy, exposure) plus the 240-doc/1.8M-token baseline metric. Build the dashboard UI against `GET /audit` right now — no need to wait on the real pipeline. Run `uvicorn app.main:app --reload` and hit `localhost:8000/audit`.
- **Real detection pipeline** is built (`app/ingest.py`, `app/chunking.py`, `app/embeddings.py`, `app/anthropic_client.py`, `app/passes/{injection,stale,redundancy}.py`) but not live yet — blocked on Scalekit creds, an OpenAI key, an Anthropic key, and Docker Desktop running locally to launch VectorAI (`scripts/run_vectorai.sh`).
- **Your territory, stubbed and waiting**:
  - `POST /fix` in `app/main.py` currently raises `501` — implement quarantine/collapse/revoke dispatch there.
  - `ScalekitClient.list_permissions`, `.revoke_permission`, `.move_file` in `app/scalekit_client.py` raise `NotImplementedError` — fill these in once the Scalekit connect spike confirms the real SDK calls.
  - Exposure-pass detection (over-shared docs, stale external collaborators) isn't built — that's on you per the task split.
- Seeded fixture (section 6 of the build doc: injection hero, stale pricing hero, 4 onboarding duplicates, exposure hero, ~15 fillers) is also yours to build.
