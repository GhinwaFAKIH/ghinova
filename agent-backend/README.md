# GHINOVA website assistant

The existing static GitHub Pages site loads `assistant.js`. The separate Node API uses Vercel AI Gateway via server-side request-scoped OIDC; no API credential is exposed to visitors. The model is `google/gemini-2.5-flash-lite`, configurable with `AI_GATEWAY_MODEL`.

## Deployment

- Vercel team: `ghinova`
- Project: `ghinova-assistant` (`prj_9gpuY5zCBOXHxgSmohgn3MPbg4Gy`)
- Endpoint: `https://ghinova-assistant-ghinova.vercel.app/api/chat`
- The API deployment is READY and public access was explicitly approved by the user and enabled. Live Gateway requests return HTTP 403: a valid credit card must be added to the Vercel account to unlock free credits. No card or paid purchase was made.
- Frontend changes remain in a draft PR until model access and a real model response are verified. Do not present the assistant as live yet.
- Deploy this directory as the Vercel project root (Node 22+). No build step or dependencies required. Deployment currently uses inline source files; Git automatic deployment is not connected.
- After the account owner completes the Gateway card requirement, verify a live course reply and project-brief tool call, then merge the frontend PR. No paid plan upgrade or credit purchase was made.

## Behavior and boundaries

Official offering details are in `knowledge.json`; update them when the site offerings change. The model may prepare an inquiry via a validated tool call. The visitor explicitly reviews it in the contact form and sends it separately. No email, booking, purchase, arbitrary URL fetching or code execution tool is exposed.

Conversations stay in page memory and are transmitted to Vercel AI Gateway/model provider for answers. This application does not intentionally persist conversations; provider logging/retention policies still apply. The UI discloses processing and warns against sensitive information.

Eight requests/minute per IP per warm instance is best-effort burst protection, not a global quota. Requests have length, output-token and time limits. Before increasing traffic, add persistent rate limiting and an account budget. The origin check is not authentication and cannot block non-browser callers.

## Validation

Run `npm test` from this directory and `node --check ../assistant.js`.
Six tests cover input limits, forbidden roles, tool validation, origin rejection, CORS, missing credentials, and mocked tool-call handling. Desktop layout was visually checked in the browser. A live model response and end-to-end chat/brief interaction remain blocked by the account card requirement.
