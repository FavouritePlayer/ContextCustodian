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
