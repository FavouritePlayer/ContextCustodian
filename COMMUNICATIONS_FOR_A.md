# Communications for A

_Inbox for Person A — B leaves messages here. A never writes here._

## How to use this file

1. **Ingest on start.** Whenever you (A) begin or resume a work session, read this file in full before doing anything else.
2. **Pop after reading.** Once you've read and acted on everything in the Messages section below, delete those entries so the section returns to empty. The next time you ingest, you should only ever see messages written since your last pop — never re-process something you've already handled.
3. **Reaching B.** Do not write a reply here. Append it to `COMMUNICATIONS_FOR_B.md` instead — this file only ever receives messages, it never sends them.
4. **Keep this section.** The "How to use this file" instructions above are permanent — only the Messages section below gets popped.

---

## Messages


### 2026-06-27 — from B

Spine pulled, building against it. Two things for you (env/install is your territory, so flagging rather than editing your files):

1. **`scripts/install.sh` + `requirements.txt` will break on a clean install — confirmed locally.** Two fixes needed:
   - `--no-deps` on scalekit drops its *benign* deps too, so `import scalekit` dies with `No module named 'jwt'`. Add to `requirements.txt`: `PyJWT cryptography cffi deprecation`.
   - `pip install "protobuf>=6.31.1"` resolves to **7.x**, which violates scalekit's own `protobuf<7.0.0` pin (re-breaks it). Pin the upper bound: `"protobuf>=6.31.1,<7.0.0"` (6.31.x satisfies Actian *and* scalekit). Also re-pin `"starlette>=0.40.0,<0.42.0"` — scalekit's `mcp` dep drags starlette to 1.x and breaks FastAPI 0.115.
   - You never hit this because all scalekit calls are stubbed (`NotImplementedError`), so the SDK is never imported at runtime. It'll bite the moment the connect spike wires a real call — and on Render.
   - I'm running these exact pins in my local venv now; full stack imports clean (protobuf 6.33.6, starlette 0.41.3).

2. **Docker Desktop is up and `actian/vectorai:latest` is pulled.** `scripts/run_vectorai.sh` is ready to launch whenever creds/keys land.

3. **Minor cross-platform bug in `corpus.py` + `audit.py`:** `save()`/`load()` and `_write_cache()`/`load_cached_audit()` use `write_text`/`read_text` with no `encoding=`. On Windows (cp1252 default) any non-ASCII char (en/em dash, arrow, curly quotes) raises `UnicodeEncodeError` on save and corrupts on load. Fine on Linux/Render (utf-8 default). Suggest adding `encoding="utf-8"` to those four calls. I worked around it on my end by keeping the fixture ASCII-clean, so nothing's blocked.

4. **Seeded fixture is built (my Task 2):** `fixtures/files.json` + `fixtures/build_manifest.py`. Running the builder materializes 23 raw docs to `fixtures/docs/` and writes `cache/corpus_manifest.json` in your `CorpusManifest`/`FileRecord` schema (text only; chunks/vectors left for your `ingest.py` once keys land). `file_id`s match `cache/audit.json`'s hero findings. When Scalekit connects, these docs are what we upload to the test workspace. Real fixture metrics: 23 docs / 1,713 tokens (the 240/1.8M headline stays the whole-workspace baseline in `cache/audit.json`, unchanged).

Still blocked team-wide on: Scalekit creds, OPENAI_API_KEY, ANTHROPIC_API_KEY, Actian 1M trial key.

### 2026-06-27 — session handoff (possible tool switch to Cursor)

No messages from B yet — this is a self-handoff in case the next session on
Person A's side starts in a different tool. Read Context_Custodian_MVP_4hr_Build.md's
"LIVE STATUS" section at the top first; this is the detailed version.

**Where things stand:**
- Actian VectorAI is running locally in Docker (`docker ps` should show a
  `vectorai` container) and licensed for 1M vectors. If the container isn't
  running, `./scripts/run_vectorai.sh`. License already activated — no need
  to re-run `scripts/activate_license.sh` unless the container was recreated
  from scratch (check with `curl http://localhost:6573/licenses/status`).
- Scalekit: `.env` already has real `SCALEKIT_CLIENT_ID`/`SECRET`/`ENV_URL`
  and both connection names (`GOOGLEDRIVE_CONNECTION_NAME`,
  `GOOGLEDOCS_CONNECTION_NAME`). `app/scalekit_client.py` is fully coded
  against the real SDK (`actions.request()` proxy pattern, confirmed
  against the official Scalekit hackathon guide + docs.scalekit.com — not
  guessed).

**The one thing actually blocking progress right now:**
Both connected accounts (Drive + Docs, user_id `demo-user-1`) exist but are
NOT authorized yet. Run this and a human needs to click both links in a
browser, signing in with the Google account that owns the workspace docs:

```
source .venv/bin/activate
PYTHONPATH=. python3 scripts/scalekit_authorize.py
```

The links it prints are time-limited magic links — always get fresh ones
from this command, don't reuse old ones from a chat transcript. Re-run the
same command after clicking both links; it should print `ACTIVE` for both
`googledrive-9jPiHf7A` and `googledocs-fWAKLNcd`.

**Once both are ACTIVE, the next steps in order:**
1. `from app.ingest import ingest_workspace; ingest_workspace("demo-user-1")`
   — confirm it populates `cache/corpus_manifest.json` and the Actian
   collection (`user-demo-user-1-memories`) without errors.
2. `from app.audit import run_audit; run_audit("demo-user-1")` — sanity
   check the three detection passes (`app/passes/injection.py`,
   `stale.py`, `redundancy.py`) produce sane findings on whatever's
   actually in that Google account/Drive right now.
3. Check in with B (append to COMMUNICATIONS_FOR_B.md, or read their
   replies here if they've written back) about the seeded fixture from
   section 6 of the build doc — tuning thresholds needs planted hero docs
   (injection phrase, stale pricing pair, 4 onboarding duplicates) to
   calibrate against.
4. Once tuned, regenerate `cache/audit.json` for real and remove the mock
   data note from `app/main.py`'s docstring.

**Known gotchas already debugged so you don't have to:**
- `actian_vectorai`'s `VectorAIClient` needs an explicit `.connect()` call
  before use — not in any doc, found by trial and error. Already handled
  in `app/vectorstore.py`.
- protobuf/grpcio-status version pins in the original build doc's Appendix A
  are backwards for current PyPI versions. `scripts/install.sh` has the
  corrected install sequence — use it instead of the build doc's Appendix A
  commands.
- `.env` holds real secrets and is gitignored; `.env.example` is the tracked
  template — never put real keys in `.env.example`, it gets pushed.

**Pop this message** once you've read it and don't need it as a reference
anymore — don't leave it sitting here stale after the next agent has
internalized the state.

