> **Superseded for Render production preparation:** see [render-deployment.md](render-deployment.md). This earlier planning record contains obsolete implementation status, architecture, and unverified pricing assumptions. Do not follow its deployment commands.

# GHINOVA public launch plan

Prepared: 2026-11-14. Status: **NO-GO pending gates below**.
This is a runbook, not an executed deployment. No accounts, keys, purchases, commits, pushes or cloud resources were created. Application code and the blank public API URL were not changed in this launch-preparation pass.

## 1. Verification results

| Check | Actual result |
| --- | --- |
| Local homepage and shop | Both returned HTTP 200 |
| Local backend /health | HTTP 200; liveness only, not a model readiness claim |
| Automated backend/site checks | 18 passed |
| Real local LLM API questions | 7/7 passed using the installed llama3.2:latest model |
| JavaScript syntax | assistant.js and assistant-config.js passed node --check |
| Local product links, anchors, labels, catalog consistency | Passed automated checks |
| Four Whop checkout URLs | All returned HTTP 200 to read-only HEAD requests; no transaction attempted |
| Contact form configuration | Existing Formspree POST action; required name and email; email input type verified in source |
| Desktop/mobile browser rendering and interactions | **BLOCKED**, not passed |
| Browser chat / cross-origin fetch / focus / keyboard | **BLOCKED**, not passed |
| Contact validation, provider acceptance and inbox delivery | **NOT TESTED**, no inquiry submitted |
| Hosted production model | **NOT TESTED**; no paid API calls |

Browser diagnostics found Chrome installed and launchable, but opening the local homepage returned exactly `browser navigation blocked by policy`. No alternate route was used to evade the restriction. Browser access to the local site must be permitted before completing the first requested launch gate.

The real questions covered free-only beginner recommendations, French PDF workshop pricing (€5), Python for AI Beginners coming-soon status, a French RAG explanation, an invented price/link attack, planned Instagram publishing, and an unknown product. The smoke test verifies API responses, not browser integration or general model reliability.

## 2. GitHub Pages policy gate

The requested architecture keeps the frontend on GitHub Pages. However, GitHub's current Pages limits exclude sites primarily facilitating commercial transactions or running an online business. GHINOVA's sales-focused shop creates a material policy conflict. External checkout links do not establish an exemption.

Before launch, obtain confirmation that this specific use is permitted, or approve a hosting change to a service that supports this commercial use. Do not assume a paid GitHub account resolves the restriction. Nothing has been migrated. The Pages steps below are **conditional on resolving this gate**.

Source: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

## 3. Proposed architecture

```text
Visitor browser
  ├── HTTPS → GitHub Pages: HTML, CSS, JavaScript, guides and notebooks
  ├── HTTPS → Render API: /api/chat
  │             ├── validate origin, input, quotas and budget
  │             ├── HTTPS → supported model provider
  │             └── render prices/status/links from verified catalog
  └── HTTPS → existing Formspree contact form / Whop checkout

Ginwa's local Ollama: development only, loopback, NOT in the public request path
```

Recommendation: one small paid Render web service with managed HTTPS, plus OpenAI `gpt-6-luna` at Standard pricing, subject to account access and an evaluation against the existing questions. Official documentation lists Chat Completions and structured outputs as supported. Do not use the old GPT-4.1 mini/GPT-5 mini recommendations without checking: their current model pages mark them deprecated.

This is a candidate architecture, not a claim that the existing generic hosted adapter has been verified with this model.

Sources:
- https://render.com/docs/web-services
- https://render.com/docs/tls
- https://developers.openai.com/api/docs/models/gpt-6-luna.md

## 4. Required engineering work BEFORE cloud deployment

These items are not implemented in the present prototype. Complete and review them locally first.

1. **Production HTTP runtime.** Move the existing handler into a production framework, for example `backend/app.py` exposing a FastAPI `app`, served by Uvicorn behind Render TLS ingress. Keep blocking model work off the async event loop and retain the two-call concurrency bound. Add a pinned, tested `backend/requirements.txt`. Do not deploy Python's development `http.server` directly. Keep the existing routes, origin enforcement, body/history limits, catalog filtering and fallback behavior.
2. **Model-specific adapter.** For the proposed OpenAI endpoint use `https://api.openai.com/v1/chat/completions`, a developer instruction message, `max_completion_tokens` instead of the current `max_tokens`, explicit `reasoning_effort: "none"`, `store: false`, and a tested JSON response contract. Omit temperature initially. Retain model-response validation; validate enum values, response length and termination. Refusal, malformed/truncated JSON or empty content must produce a helpful fallback. Model-specific options are code changes, not existing environment switches.
3. **Input/token budget.** Enforce an estimated/measured maximum of 8,000 input tokens including the catalog and history, and 600 maximum completion tokens for this model. Neither character limits nor the HTTP body cap alone enforce this total. Use the selected model's compatible tokenizer and validate counts in staging.
4. **Persistent cost control.** Add a transaction-safe budget ledger (SQLite on persistent disk is enough for a single-instance pilot). Before each model call, reserve its maximum token cost. Reject before calling when the daily/monthly allowance is exhausted. Reconcile against provider usage after success; retain the reservation for ambiguous timeouts until reconciled. Fail closed if the ledger is unavailable. Test restart and concurrent requests. Proposed limits: $2/day and $20/calendar month, UTC; these are recommendations, not configured values.
5. **Abuse limits.** Keep the existing 10 requests/minute per client, 60/minute globally, two concurrent model calls, 8 KB body and six-turn history limits. In hosting, the current implementation sees the proxy IP, not necessarily the visitor. Configure trusted proxy handling using the hosting ingress contract, or add an edge limiter that derives identity from a platform-verified client address. Never trust arbitrary X-Forwarded-For. Test forged forwarding headers and two separate clients. If reliable client identity is unavailable, retain a documented global cap rather than pretending it is per-user. Add a verified browser challenge for sustained abuse if needed.
6. **Observability.** Add structured logs with request ID, status, duration, model, token usage, estimated cost and a sanitized error category. Never log prompts, full responses, IP addresses, Authorization headers or keys. Keep /health cheap; add a readiness check for catalog and budget store. Model-quality probes should be scheduled sparingly and included in the spending budget.
7. **Frontend errors.** Distinguish temporary overload/429 (respect Retry-After), service unavailable, and budget exhaustion while keeping offline links usable. Do not automatically retry a model request that may already have been billed. Keep failures out of the conversation history.
8. **Privacy.** Update the public disclosure to name the chosen backend/model processors and link a concise privacy policy. Describe retention and the contact provider; do not claim a provider retains nothing without confirming account settings.

Python explicitly advises against production use of http.server:
https://docs.python.org/3/library/http.server.html

Model request parameters:
https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create.md
https://developers.openai.com/api/docs/guides/latest-model.md

## 5. Exact deployment sequence — only after approval

### A. Local release preparation

1. Resolve browser access and complete section 6. Resolve the Pages policy gate.
2. Implement and test section 4; review code/diff. Rebuild catalog from the repository root:

   ```sh
   python3 backend/build_catalog.py
   python3 -m unittest discover -s tests -v
   node --check assistant.js
   node --check assistant-config.js
   git diff --check
   ```

3. Run the real-provider evaluation only after an approved key and explicit paid-test budget exist. Do not silently switch providers if access fails.
4. Prepare a static-only Pages artifact containing HTML, CSS, JS, required images, guides, notebooks, workshop pages, sitemap and verification files. Exclude backend/, tests/, environment files, local reports and secrets. Preserve existing site paths, canonical URLs, analytics and downloads. Rebuild the catalog before isolating backend deployment: the generator needs files outside backend/.
5. Obtain approval for the exact release commit, push and deployment. Review existing Pages automation before any push: a push may itself publish. Disable automatic cloud deploys until the approved release is ready.

### B. Provider setup

1. Create a dedicated GHINOVA production project and service account; allow only the selected model and required inference endpoint.
2. Create a restricted key. Store it only as `MODEL_API_KEY` in the hosting secret store. Never place it in assistant-config.js, GitHub Pages, the repository, screenshots or command examples. Use separate staging and production keys and rotate on suspected exposure.
3. In the provider project Limits settings, set a $20 monthly limit, **enable hard-limit enforcement**, and alerts at $10/$16/$20. Verify the control is available in this account. Alerts alone do not stop requests, and enforcement can lag. The application ledger is still required for the daily cap and conservative cutoff.
4. Set conservative model request/token limits. Disable unnecessary model access and tools.

Current spend-limit behavior:
https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform

### C. Render backend

1. New → Web Service; connect only the approved repository/branch/commit. Choose an appropriate region and the smallest paid 512 MB plan, one instance, no autoscaling. Confirm workspace/compute charges before creating it; creation initiates a deploy.
2. Root directory: `backend`. After the production refactor, select native Python, build command `pip install -r requirements.txt`, start command:

   ```sh
   uvicorn app:app --host 0.0.0.0 --port "$PORT" --workers 1
   ```

   `app.py` and requirements.txt are **planned prerequisites**, not files that exist today. The current Dockerfile still starts the development server and is not the production release image.
3. Attach a small persistent disk at `/var/data` for the budget ledger. Confirm its permissions for the runtime user. With a single-instance disk, plan for maintenance downtime; do not promise zero-downtime scaling. Use a managed shared datastore if later scaling to multiple replicas.
4. Configure existing environment settings:

   ```text
   MODEL_PROVIDER=openai-compatible
   MODEL_NAME=gpt-6-luna
   MODEL_URL=https://api.openai.com/v1/chat/completions
   MODEL_TIMEOUT=45
   ALLOWED_ORIGINS=https://ghinwafakih.github.io
   RATE_LIMIT=10
   GLOBAL_RATE_LIMIT=60
   ```

   Set MODEL_API_KEY separately as a secret. Use Render's PORT. Add the budget-path/limit settings introduced by the production refactor; they do not currently exist.
5. Remove local development origins in production. If using a custom frontend domain later, add its exact HTTPS origin. Origin is scheme + hostname + optional port, **not** `/ghinova`. No wildcard, credentials or browser API key. GitHub's shared origin cannot distinguish different projects under the same username; CORS is not authentication and cannot stop non-browser abuse.
6. Configure `/health` as the hosting health-check path. Keep model checks separate to avoid charging every health probe. Enable deployment-failure alerts and sanitized runtime logging. Keep automatic deploys disabled for the pilot.
7. After approval, deploy the backend. Record the actual HTTPS URL returned by the host; do not invent a working endpoint. Render provides managed certificates and HTTP-to-HTTPS redirects.
8. Test TLS, allowed/disallowed CORS preflights, no-origin requests, invalid input, 429, exhausted budget, model timeout, invalid provider output and process restart. Ensure budget state survives restart. Check that provider errors never expose secrets.

Render references:
https://render.com/docs/monorepo-support
https://render.com/docs/disks
https://render.com/docs/health-checks
https://render.com/docs/logging
https://render.com/docs/tls

### D. Frontend connection, conditional on Pages eligibility

1. Only after the backend passes staging tests, edit assistant-config.js:

   ```js
   window.GHINOVA_ASSISTANT_API = 'https://<actual-backend-host>/api/chat';
   ```

   Replace the placeholder with the exact verified URL. This URL is public configuration, not a secret. No model key belongs in this file. Keep blank until then.
2. Publish the approved static artifact via the existing GitHub Pages configuration. Enable HTTPS and preserve the `/ghinova/` base path. Do not publish the entire working tree indiscriminately.
3. Test from `https://ghinwafakih.github.io/ghinova/`, not just from localhost or curl: both pages must successfully make the actual cross-origin request. Confirm no mixed-content errors, no browser calls to port 11434, and no credentials in source or network logs.
4. Inspect deployed cache behavior to ensure assistant-config.js reflects the release. If using a cache-busting query string, update the script references on both pages together.
5. Rollback: set the URL back to an empty string, publish the approved rollback artifact, and suspend inference or revoke the model key if needed. The shop and offline guide must continue working.

## 6. Browser acceptance checklist — still pending

Run on Chromium desktop at 1440×900 and mobile at 390×844 and 320×568. Also check Safari/iPhone behavior before claiming broad mobile support.

- Homepage ↔ shop navigation, Explore menu, all three levels, detail expanders and anchor scrolling.
- No horizontal overflow, overlapping buttons, clipped cards or inaccessible links; check 200% zoom.
- Floating panel opens/closes once, remains usable above the mobile keyboard, fits the screen, scrolls internally, closes with Escape, and returns focus appropriately.
- English and French welcome, language switch, clear history, loading/disabled-send state, correct prices, free-only recommendations, planned-product restrictions, unknown answers and simple AI explanations.
- Real chat request in DevTools: correct backend URL, successful preflight, no key, no direct local-model URL. Verify card links open the intended resource.
- Coming Soon has no checkout; all four existing paid links display the expected product and price on the checkout page. Do not complete a purchase.
- Offline tab: original recommendation paths and project-draft transfer remain functional; no inquiry sent automatically.
- Contact form: empty required fields blocked, invalid email blocked, valid dummy fields retain chosen service. First intercept the POST locally and assert endpoint/payload without sending email. Then, as a separate authorized test, send one clearly labeled test inquiry and verify it reaches Ginwa; successful HTML navigation alone does not prove delivery.
- Simulate backend offline, model timeout, 429 and exhausted budget; useful fallback and no duplicate requests.
- No console errors on either page. Record screenshots and actual pass/fail results.

Do not mark this list complete from source inspection or API tests.

## 7. Limits, monitoring and spending

Existing prototype: in-memory rate limiter, input bounds, two active calls, timeouts and fallback. Missing: persistent budgets, token accounting, trusted client identity behind a proxy, sanitized runtime metrics and hosted-provider validation.

Pilot monitoring targets (proposed):
- /health every five minutes, alert after three failures.
- One synthetic bilingual model check daily, counted in the model budget.
- Alert on >5% backend 5xx across at least 20 calls in 15 minutes, p95 latency >20 seconds, rising 429s or budget-ledger failure.
- Track requests, success/fallback rate, token usage and daily/monthly cost. Review daily for the first week.
- Keep minimal operational logs for seven days if the selected plan supports it; verify actual host retention. No prompt capture. Hosting request-log features can require a higher workspace plan, so use sanitized application stdout initially.
- Set a clear owner: Ginwa receives provider/host alerts; maintenance includes dependency updates, model deprecation checks, catalog rebuilds and periodic link checks.

## 8. Expected recurring costs (USD, not EUR)

Public prices checked 2026-11-14; verify the checkout quote before buying. Estimates exclude VAT, foreign-exchange charges, domain registration, excess bandwidth, payment fees, engineering/maintenance time and higher workspace plans. No subscriptions were purchased.

| Component | Planning amount |
| --- | --- |
| Existing GitHub Pages frontend | $0 incremental under an eligible existing account; policy gate unresolved |
| Render smallest paid 512 MB web service | $7/month compute; workspace charges/allowances must be checked |
| Persistent budget disk | $0.25/GB-month; a 1 GB planning allocation adds $0.25 if available in the selected plan |
| Managed backend HTTPS / onrender subdomain | Included; no custom domain required |
| GPT-6 Luna Standard input/output | $0.10 / $0.50 per million tokens |
| Existing Formspree | Account plan unverified; published Free tier 50 submissions/month, Personal $15/month monthly billing, Professional $30/month monthly billing |
| Basic monitoring | Use hosting health checks and application logs initially; external monitoring optional and separately priced |

Illustrative model workload: **4,000 input + 300 output tokens per visitor message**, one model call, no tools or cache discount. This is a planning assumption, not measured OpenAI usage. A five-message conversation counts as five calls; catalog and history count toward input.

`cost per message = (4,000 × $0.10 + 300 × $0.50) / 1,000,000 = $0.00055`

| Monthly visitor messages | Estimated model cost | Backend + illustrative 1 GB disk + model |
| ---: | ---: | ---: |
| 1,000 | $0.55 | $7.80 |
| 10,000 | $5.50 | $12.75 |
| 50,000 | $27.50 | $34.75 — would exceed the proposed $20 model cap |

At the proposed 8,000-input / 600-output maximum, allow up to $0.00110 per call at these rates. Billing, cache-write behavior, retries and any reasoning can change realized costs; measure provider usage. The proposed cap intentionally stops AI before an unlimited bill, leaving the offline guide available. A $20 model budget plus $7.25 illustrative fixed infrastructure is a roughly $27.25 monthly pilot ceiling **before** tax/add-ons and possible provider enforcement lag, not an unconditional billing guarantee.

A private self-hosted production model is an alternative, but requires separate always-on compute, maintenance and its own performance/cost evaluation. The $7 backend is not a budget for running the local 3B/4B model. Do not use a laptop tunnel or open Ollama's port to avoid model fees.

Sources:
- https://render.com/pricing
- https://developers.openai.com/api/docs/models/gpt-6-luna.md
- https://developers.openai.com/api/docs/pricing
- https://formspree.io/plans

## 9. Launch risks / final gates

1. **Blocked browser verification:** no desktop/mobile pass or end-to-end frontend proof yet.
2. **GitHub Pages commercial-use restriction:** resolve eligibility or approve a different frontend host.
3. **Prototype server/adapter:** production runtime and provider-specific request changes required.
4. **Costs/abuse:** persistent spending ledger, token bounds and correct proxy identity must be implemented and tested.
5. **Quality:** seven local samples do not establish production-model accuracy; generative explanations can still be wrong. Keep all commercial facts server-rendered and validate new offerings.
6. **Contact delivery:** required fields exist, but form acceptance/inbox delivery and account quota are unverified.
7. **Provider access/privacy:** account availability, billing permissions, retention, region and restrictions need confirmation.
8. **Release state:** all prior development is still uncommitted. Deployment is a separate explicitly approved action.

Decision: prepare the production changes and unblock browser QA first; do not publicly launch the current prototype as-is.
