# Deploying to Render (Person B step 4)

Two services: **VectorAI** (private Docker) + **Context Custodian** (public Python web app).

The mock-audit demo works without Actian license activation or OpenAI keys — `GET /audit` serves committed `cache/audit.json`. Add keys when Person A runs the real ingest pipeline.

## 1. Claim credits

<https://credits-portal-mmdm.onrender.com/claim/hack-day-sf-scalekit-2026>

## 2. Apply the Blueprint

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect this repo (`ContextCustodian-1`, branch `demo`)
3. Render reads `render.yaml` and creates:
   - `vectorai` — private service (`actian/vectorai:latest` + 1 GB disk)
   - `context-custodian` — public web service (FastAPI)
4. Click **Apply**

Both services must stay in the **same region** (`oregon` in the blueprint) so the private network works.

## 3. Set environment variables

After the blueprint syncs, open **context-custodian** → **Environment** and fill in the secrets (marked `sync: false` in `render.yaml`):

| Variable | Required for demo | Notes |
|----------|-------------------|-------|
| `SCALEKIT_CLIENT_ID` | For live "Fix as me" | From Scalekit dashboard |
| `SCALEKIT_CLIENT_SECRET` | For live fixes | |
| `SCALEKIT_ENV_URL` | For live fixes | e.g. `https://….scalekit.dev` |
| `GOOGLEDRIVE_CONNECTION_NAME` | For live fixes | Full name with suffix, e.g. `googledrive-9jPiHf7A` |
| `GOOGLEDOCS_CONNECTION_NAME` | For live fixes | Full name with suffix |
| `ANTHROPIC_API_KEY` | Real audit only | Mock cache works without it |
| `OPENAI_API_KEY` | Real ingest only | Mock cache works without it |
| `QUARANTINE_FOLDER_ID` | Live quarantine | Google Drive folder ID for `/Quarantine` |
| `ARCHIVE_FOLDER_ID` | Live collapse | Google Drive folder ID for `/Archive` |

On the **vectorai** service (optional):

| Variable | Notes |
|----------|-------|
| `ACTIAN_PRODUCT_KEY` | 1M-vector trial key — activates on first deploy via `afterFirstDeployCommand`. Without it you stay on the 5k Community cap. |

Redeploy after setting secrets.

## 4. Verify

Public URL (from **context-custodian** → top of page):

- `https://<your-service>.onrender.com/` — dashboard
- `https://<your-service>.onrender.com/audit` — mock findings JSON

You should see four hero findings and the 240 doc / 1.8M token baseline.

## 5. Optional — activate Actian license manually

If you add `ACTIAN_PRODUCT_KEY` after first deploy, open a **Shell** on the `vectorai` service and run:

```bash
curl -X POST "http://localhost:6573/licenses/add" \
  -H "Content-Type: application/json" \
  -d "{\"product_key\":\"YOUR_KEY_HERE\"}"
curl "http://localhost:6573/licenses/status"
```

Expect `"state": "licensed"` (or similar) and `max_vectors` in the millions.

## 6. Demo rehearsal (step 5)

See **`DEMO.md`** for the 4-minute script. Before presenting:

- Click **Reset demo** on the dashboard (or run `python scripts/reset_demo_cache.py`)
- Confirm `X-Custodian-Audit-Source: cache` on `GET /audit`
- Record a fallback clip and save the link in `demo/FALLBACK_LINK.txt`

## 7. Scalekit OAuth (for live fixes on Render)

Connected accounts must be `ACTIVE`. Run locally (magic links are time-limited):

```bash
source .venv/bin/activate
PYTHONPATH=. python scripts/scalekit_authorize.py
```

Click both links, re-run until both connections show `ACTIVE`. OAuth tokens are stored in Scalekit's cloud — the Render app picks them up via the same `SCALEKIT_*` creds.

## Architecture

```
Internet
   │
   ▼
context-custodian (web, public)
   │  GET /audit  → cache/audit.json (mock until A regenerates)
   │  POST /fix   → Scalekit (live) or index-only fallback
   │
   └── private network ──► vectorai:6574 (pserv, NOT public)
                              actian/vectorai:latest
                              disk: /var/lib/actian-vectorai
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails on `import scalekit` / `jwt` | `render_build.sh` installs scalekit deps — check build logs |
| Actian writes fail silently | protobuf pin — see `scripts/render_build.sh`; or hit 5k cap — add trial key |
| `connection not found` from Scalekit | Fix `GOOGLEDRIVE_CONNECTION_NAME` / `GOOGLEDOCS_CONNECTION_NAME` to full dashboard names |
| Fix runs in "index" mode only | OAuth not ACTIVE, or missing folder IDs, or mock `file_id`s in cache |
| VectorAI data lost on redeploy | Confirm disk mounted at `/var/lib/actian-vectorai` on pserv |

## Updating the blueprint

Push changes to `render.yaml`, then **Blueprint** → **Manual sync** in the Dashboard.
