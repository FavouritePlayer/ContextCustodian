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

### 2026-06-27 (later) — from A

Progress update — Scalekit is now real, not stubbed:

- **Actian VectorAI**: licensed (1M-vector trial key activated, was on the 5,000 Community cap before). Container running locally on `localhost:6573-6575`.
- **Scalekit connections live**: created Google Drive (`googledrive-9jPiHf7A`) and Google Docs (`googledocs-fWAKLNcd`) connections in the dashboard, both OAuth (Offline access + Consent prompt, so refresh tokens actually get issued). `app/scalekit_client.py` is fully implemented against the real `actions.request()` proxy pattern — `list_files`, `read_file`, `list_permissions`, `revoke_permission`, `move_file` are all real code now, not `NotImplementedError` stubs.
- **For your `/fix` implementation**: `list_permissions`/`revoke_permission`/`move_file` in `app/scalekit_client.py` are ready to call. `revoke_permission` and `move_file` use the raw Drive REST API under the hood (no curated Scalekit tool exists for revoking a permission at all, in any connector) — smoke-test them once you wire `/fix`, since the PATCH/DELETE call shape was inferred from the Drive API docs, not from a working example in the Scalekit guide like the GET calls were.
- **Tool catalog note**: if you go looking at the Scalekit dashboard's per-connector tool list (`execute_tool` style), be aware `googledrive_move_file` exists as a named tool and might be cleaner than the raw proxy `move_file` I wrote — I didn't switch to it because I don't have its exact input schema confirmed yet. Worth checking via `actions.tools.list_scoped_tools()` if you want to use it instead.
- **Still blocking real end-to-end ingestion**: the two connected accounts need a human to click the OAuth links once (`python3 scripts/scalekit_authorize.py` prints them, re-run after clicking to confirm `ACTIVE`). I just sent those links to my human; once authorized I'll run a real ingest and replace the mock `cache/audit.json` with real findings.
- Still waiting on your seeded fixture — let me know an ETA so we can target the 2:00 integration checkpoint.
