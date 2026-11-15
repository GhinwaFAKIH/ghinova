> **Production entry point:** `backend.app:app` served by Uvicorn. See [Render deployment checklist](../docs/render-deployment.md) for current configuration and limits. The instructions below describe the legacy development server (`server.py`), not the production service.

# GHINOVA website assistant

A separate Python HTTP API for the static website. No Python packages are required.
The frontend does **not** contain a model key. GitHub Pages cannot run this backend.

## Local development (no paid API)

From the repository root:

```sh
python3 backend/build_catalog.py
python3 backend/server.py
```

In another terminal:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/index.html` or `shop.html` and choose **Ask GHINOVA · AI**.
On localhost only, the frontend defaults to `http://127.0.0.1:8787/api/chat`.
The API defaults to the already-installed `llama3.2:latest` model at
`http://127.0.0.1:11434/api/chat`. No models are downloaded by this project.
`MODEL_NAME` can select another installed model. Keep Ollama on loopback.

The original guided recommendations and inquiry builder are retained in the
**Offline guide** tab on the homepage. The shop links to this same guide. The guide
is labeled offline; its predefined responses are not presented as AI answers.
AI conversation exists in page memory only and is cleared on reload or Clear.
Questions and the last six messages are sent to the backend/model when AI is used.
The API does not log prompts. A future hosted provider may have its own retention policy.

## Knowledge and grounding

`build_catalog.py` extracts published offers from shop JSON-LD, planned cards,
verified local guide/download paths, and the existing training prices/links.
Rebuild `catalog.json` whenever website offers change; the regression test detects drift.
Listed means present on the website, **not** that a checkout was independently live-tested.

The LLM selects catalog IDs and explains AI concepts. The server—not the model—
renders product names, prices, status and URLs. Unknown IDs are discarded. Coming-soon
and planned-service records cannot return purchase/download links. Generative prose
is restricted to educational explanations and filtered for commercial claims and URLs.
AI explanations and recommendations can still be mistaken; they should be evaluated
before public launch. The assistant does not submit forms, buy products or publish posts.

## Configuration

| Variable | Default / purpose |
| --- | --- |
| `BIND_HOST` | `127.0.0.1`; use `0.0.0.0` only in an isolated hosting container behind TLS ingress |
| `PORT` | `8787` |
| `ALLOWED_ORIGINS` | `http://127.0.0.1:8765,http://localhost:8765`; exact comma-separated origins, no paths |
| `MODEL_PROVIDER` | `ollama` or `openai-compatible` |
| `MODEL_NAME` | `llama3.2:latest`; choose explicitly for a hosted provider |
| `MODEL_URL` | Loopback Ollama `/api/chat`, or a separately configured HTTPS chat-completions endpoint |
| `MODEL_API_KEY` | Server-only secret for a hosted compatible provider; never frontend configuration |
| `MODEL_TIMEOUT` | `60` seconds |
| `RATE_LIMIT` | `10` requests/minute per direct connection IP |
| `GLOBAL_RATE_LIMIT` | `60` requests/minute total per process |

Provider mode changes are explicit. The server never falls back to a paid provider.
Hosted-provider compatibility is implemented but **not tested with a paid service**.

## Separate deployment — instructions only, nothing deployed

1. Host the `backend/` directory on a Python-capable service, with TLS termination.
   The included Dockerfile is optional; its build has not been executed here.
2. Choose either a model running privately on that hosting machine or an approved
   HTTPS model provider. Never tunnel or expose the user's local Ollama server.
   Supply credentials through the host's secret manager, not Git or JavaScript.
3. Set `ALLOWED_ORIGINS=https://ghinwafakih.github.io` (plus any verified custom origin).
   CORS origins do not include `/ghinova`. Set the model variables explicitly.
4. Run one process initially. Place it behind a reverse proxy with HTTPS, a request
   body limit of 8 KB, connection/time limits, and per-client edge rate limiting.
   Only the reverse proxy should reach the app port. Do not expose Python's HTTP
   server directly to the internet. CORS is not authentication or bot protection.
5. Set the public HTTPS `/api/chat` URL in `assistant-config.js` **only after** the
   deployed endpoint is verified. A blank URL intentionally enables only the
   offline fallback on the public site; it never calls the user's laptop.
6. Test from the actual GitHub Pages origin: English/French questions, precise
   prices, planned offerings, unknown products, keyboard/mobile use, failures,
   rate limits, and malicious input. Check the hosting provider's logging and
   retention settings before launch. Do not claim live operation before this.

Security limits: bounded inputs/history, exact-origin allowlist, no cookies,
no model tools, no user-selectable upstream URL, no redirects to arbitrary hosts,
model timeout, two concurrent model calls, sixteen connection threads, bounded
per-IP rate buckets, and global rate limiting. No forwarded IP headers are trusted.
Behind a proxy the app intentionally sees the proxy IP, so its rate cap is shared;
use edge per-client limits. For multiple processes/replicas, add a shared limiter
and upstream usage budget. Current in-memory counters reset on restart.

## Tests

```sh
python3 -m unittest discover -s tests -v
node --check assistant.js
node --check assistant-config.js
# Opt-in: real local Ollama requests, with the backend running:
python3 tests/real_model_smoke.py
```

`/health` checks the API process only and explicitly does not assert model readiness.
