# Render production preparation — GHINOVA

Status: prepared locally, **not approved for deployment**. Updated 2026-11-14.
This checklist supersedes public-launch-plan.md. Keep the existing repository and
public GitHub Pages deployment unchanged. Do not push, import a Blueprint, create
services, enable billing, or deploy until Ginwa approves the exact release.

## Already implemented

- `scripts/build_static.py` builds homepage/shop and selected public assets into
  `dist/`, excluding backend, environment files and tests. Only the built
  `assistant-config.js` receives `PUBLIC_API_URL`; source configuration stays blank.
- `backend/app.py` is the production FastAPI application. `server.py` retains
  shared catalog/rendering logic and a legacy local development entry point.
- OpenAI adapter: fixed HTTPS endpoint, server-only key, strict JSON response
  contract, no tools, no redirects, bounded responses/timeouts and safe fallback.
  Product prices, URLs and availability are rendered from the catalog, not invented
  by the model. Planned services remain quote/contact requests, not working integrations.
- SQLite atomic reservations persist across restarts. UTC daily/monthly caps default
  to $2/$20. Reservations are **never refunded**, including successes and timeouts:
  deliberately conservative, not an invoice or actual-usage reconciliation system.
- Input uses a UTF-8-byte-based conservative estimate plus framing allowance,
  capped at 24,000; output is capped at 600 tokens. This is not a verified provider
  tokenizer calculation. Rate assumptions must be checked before hosted use.
- Exact-origin CORS, 8 KB request limit, two concurrent model calls, persistent
  fixed-minute rate limits, sanitized allowlisted application logs.
- Render defaults to a shared 60-request/minute global cap. It does **not** promise
  per-visitor limits. Keep proxy headers disabled until ingress identity is verified.
- `render.yaml` separates static hosting from a paid Python service with one worker
  and a 1 GB persistent disk. Automatic deployment is off.

## Local verification evidence

Existing workspace evidence, inspected without rerunning the suites:

- `outputs/render-production/tests.txt`: 27 checks passed (0.374 seconds).
  Covers catalog/site rules, build isolation, mock hosted requests/failures, quotas,
  restart persistence, CORS, input limits, rate limits and log sanitization.
- `outputs/render-production/real-model-results.json`: seven local questions,
  each HTTP 200 with `passed: true`: free resources, French pricing, coming-soon
  course, RAG explanation, malicious price/link request, planned agent, unknown offer.
- These are historical results, not proof against a pinned release commit. There is
  no saved source hash manifest. Hosted tests used mock responses, not paid inference.
- Browser rendering and frontend-to-backend browser interaction remain unverified;
  earlier browser navigation was blocked by policy. API results do not close that gate.

## Release checklist (approval required before external actions)

1. Review all uncommitted changes; preserve products, prices, checkout links, SEO,
   contact action and downloads. Select an exact release commit only with approval.
   Do not change existing Pages automation or its published artifact.
2. Confirm provider model access and request-schema support. The current adapter
   deliberately permits only `gpt-6-luna`; changing models needs code review and
   fresh tests. Confirm current rates, retention and account controls from official
   documentation before enabling calls. OpenAI coding authorization is not permission
   to activate a paid website API.
3. Review `backend/.env.example` and `deploy/static.env.example`. Never add real keys
   to files or static configuration. The app does not automatically load `.env`.
4. After explicit approval, connect the existing repository to Render. Use repository
   root for both services. Static build: `python3 scripts/build_static.py`; publish
   directory: `dist`. Leave `PUBLIC_API_URL` blank for an offline preview.
5. Backend build: `pip install -r backend/requirements.txt`. Start:

   ```sh
   uvicorn backend.app:app --host 0.0.0.0 --port "$PORT" --workers 1 --no-proxy-headers --no-access-log --limit-concurrency 32 --timeout-keep-alive 5
   ```

6. Use `/ready` as the health path. Both `/health` and `/ready` explicitly do not
   establish model availability; readiness checks the ledger, not inference.
7. Attach persistent storage at `/var/data`; set `BUDGET_DB=/var/data/usage.sqlite3`.
   Retain one service instance/worker. Do not scale SQLite across replicas.
   Set production mode, hosted endpoint/model, server-only `MODEL_API_KEY`, a random
   `RATE_HASH_KEY` of at least 32 characters, and exact HTTPS `ALLOWED_ORIGINS` without
   paths/trailing slashes. Blueprint generates the hash key; never print it.
8. Keep `CLIENT_RATE_MODE=global`. CORS is not authentication: non-browser callers
   can forge Origin. Add verified edge abuse controls if traffic requires them.
9. With a separately approved paid-test budget, evaluate real hosted responses and
   failure cases. Verify account usage against reservations and pricing. Configure
   available provider spend controls/alerts, but do not assume alerts enforce a cap.
10. After backend acceptance, set the static build's `PUBLIC_API_URL` to its HTTPS
    `/api/chat` endpoint and rebuild only the Render artifact. Test actual browser
    preflight/chat from the Render origin. No key belongs in frontend code.
11. Check desktop and mobile at 1440, 390 and 320 pixels: no overflow, readable cards,
    keyboard/focus, chat scrolling/close/clear, offline fallback, 429 and timeout.
    Verify all existing checkout destinations without buying. Test contact payload
    with local interception; inbox delivery needs a separately authorized submission.
12. Before launch, approve a concise processor/retention privacy notice. Existing
    chat notice is generic. Verify canonical URLs/domain migration separately; do
    not silently rewrite SEO to a temporary preview domain.

## Expected charges — estimates, not verified quotes

Earlier local planning recorded $7/month backend compute and $0.25/GB-month disk:
**$7.25/month illustrative fixed subtotal**, plus model usage, static-host allowances
or overages, workspace fees, taxes, domain and existing checkout/contact charges.
These prices have not been reverified in this pass. Verify Render's quote before
creating resources. A $20 application model allowance gives a planning subtotal of
$27.25, **not a guaranteed total bill ceiling**. Static hosting is not assumed
unconditionally free; verify current plan and bandwidth allowances.

Application reservation rates are $0.25/million estimated input tokens and
$1.00/million output tokens. At the configured maximum, reservation is $0.0066/call.
These are accounting assumptions, not a claim of current provider pricing. Confirm
that they cover the selected model and request overhead before opening traffic.
Never refund ambiguous requests or delete the ledger to restore budget.

Official verification targets: Render pricing and Blueprint reference, and OpenAI
model/API/pricing documentation. No live pricing or provider compatibility verified here.

## Rollback and operations

- Disable AI by rebuilding the Render static artifact with empty `PUBLIC_API_URL`.
  Shop, checkout links, contact and offline guide remain available. This is a
  separately approved deployment, not a modification to GitHub Pages.
- If inference must stop immediately, suspend the backend or revoke its dedicated
  provider key through an authorized action. Static cache rollback alone cannot
  stop direct API callers. Disk/other charges may continue; verify billing.
- Restore the prior approved static artifact and backend release. Preserve the
  ledger disk and schema; do not reset reservations during rollback. Back up SQLite
  consistently using its backup API or with writes stopped, not by copying a live
  database file without its WAL. Test restoration before any future schema migration.
- Watch sanitized status/category/duration/reserved-cost logs, 429s, 5xx, disk health
  and provider billing. Host-level logging and retention still need review.
- Optional Docker deployment is not the default. Its lock-file copy was corrected;
  image build/runtime and disk permissions remain untested.

## Remaining launch blockers

Real hosted API compatibility/pricing/quality; browser desktop/mobile and CORS
integration; contact delivery; privacy disclosure and retention review; Render
runtime/disk/Blueprint acceptance; backup restore and real hosted rollback. No public
launch, revenue, checkout transaction or deployed-client capability is claimed.
