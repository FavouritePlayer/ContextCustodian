# Demo script (Person B step 5)

4-minute stage script for Context Custodian. **B drives.** Analysis is pre-cached —
the only live call on stage should be **Fix as me** (and say that out loud).

Replace `YOUR_RENDER_URL` with the public URL from Render (`context-custodian` service).

---

## Before you walk on stage

1. Open `YOUR_RENDER_URL` in a clean browser tab (or localhost for rehearsal).
2. Click **Reset demo** (top right) — restores all four hero findings to unfixed.
3. Confirm the headline reads **1.8M tokens · 240 docs** and the source tag says **pre-cached**.
4. Have Scalekit OAuth ACTIVE if you want live **· as you** fixes (not **· index only**).
5. Record a fallback clip (see [Fallback recording](#fallback-recording)) and keep the file/link handy.

Quick reset from terminal (same as the button):

```bash
.venv/Scripts/python scripts/reset_demo_cache.py
```

---

## The thesis line (memorize)

> "A workspace used to be for humans to browse. Now agents live in it and ingest all of it — so every junk doc is a tax on every agent that reads the space. This workspace was **240 docs and 1.8M ingestible tokens**. After Custodian: **90 docs, 600K tokens**, zero information lost, every removal reversible."

**Compaction definition (if a judge probes):** we reduce the *agent-ingestible surface* — de-index, quarantine, archive-with-pointer — not summarize or rewrite. Lossless and reversible by construction.

---

## Minute-by-minute (4:00 total)

| Time | Beat | What to do / say |
|------|------|------------------|
| **0:00** | Thesis + messy workspace | "Meridian Labs' Drive — 240 docs, 1.8 million tokens any agent would ingest." Point at the hero numbers. |
| **0:45** | Load audit | Dashboard already loaded from **pre-cached** audit (no spinner, no model wait). Walk the four passes in the sidebar: Injection, Stale, Redundancy, Exposure. |
| **1:15** | **Injection hero** | Open the injection card. Read the receipt (the attack string). "This doc would hijack any agent that reads it. **Quarantining it as you.**" Click **Fix as me**. Point at the tag: **· as you** (live Drive) vs **· index only** (honest fallback). |
| **2:15** | **Stale hero** | "2023 pricing still live — an agent would quote **$99** instead of **$149**." Quarantine the stale doc. Watch the token bar move. |
| **3:00** | **Redundancy hero** | "Four copies of onboarding. Keep the canonical, collapse the rest with pointers." Click collapse. Token number drops again. |
| **3:30** | Close on metric | "240 docs and 1.8M tokens → 90 and 600K projected after fixes. Nothing deleted — quarantine, archive, revoke — **all done as me** with my permissions." |
| **3:50** | Buffer | Optional: Exposure / Cap Table revoke if the judge cares about permissions. |

---

## Act-as-the-user beat (say explicitly)

Every fix runs through **Scalekit** with the user's OAuth token. Name it when you click:

- "This is Scalekit — I'm acting as **demo-user-1**, not as a service account."
- Actian collection is `user-demo-user-1-memories` — same id string, isolation proof.

---

## If something breaks on stage

| Problem | Fallback |
|---------|----------|
| Render slow / cold start | "Analysis is pre-cached" — **Reload audit**; numbers appear instantly. |
| `/audit` fails | Dashboard loads **offline fallback** JSON automatically. |
| Fix returns **· index only** | "Index updated now; Drive move pending OAuth — the receipt and metric still hold." Still demoable. |
| Total outage | Play your **pre-recorded fallback clip** (below). |

---

## Fallback recording

Record once while everything works (~4 min following this script):

1. **Tool:** OBS, Loom, or QuickTime — 1920×1080, capture browser + mic.
2. **URL:** `YOUR_RENDER_URL` after **Reset demo**.
3. **Must show:** thesis numbers → four finding cards → at least one **Fix as me** click → before/after token bar.
4. **Save as:** `demo/fallback-demo.mp4` (gitignore large binaries) or upload to Drive/Loom and paste the link in `demo/FALLBACK_LINK.txt`.

Template for the link file:

```
# Paste your fallback clip URL here (Loom, Drive, YouTube unlisted, etc.)
https://
```

---

## Rehearsal checklist

- [ ] Reset demo → four unfixed findings
- [ ] Injection → Fix as me → bar moves
- [ ] Stale → Fix as me
- [ ] Redundancy → Fix as me → largest token drop
- [ ] Undo works on at least one card
- [ ] Fallback clip recorded and link saved
- [ ] Run script twice back-to-back with reset between

---

## API reference (for debugging)

| Endpoint | Purpose |
|----------|---------|
| `GET /audit` | Pre-cached findings (`X-Custodian-Audit-Source: cache`) |
| `POST /audit/reset` | Restore golden snapshot |
| `POST /fix` | Fix as user (`X-Custodian-Fix-Mode: workspace` or `index`) |
| `POST /undo` | Reverse a fix |
| `GET /health` | Render health check |

Golden snapshot: `cache/audit.demo.json` → copied to `cache/audit.json` on reset.
