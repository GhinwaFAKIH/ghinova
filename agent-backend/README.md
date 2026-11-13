# GHINOVA website assistant

The existing static GitHub Pages site loads `assistant.js`. The separate Node API uses Vercel AI Gateway via server-side OIDC; no API credential is exposed to visitors. The model is `google/gemini-2.5-flash-lite`, configurable with `AI_GATEWAY_MODEL`.

## Deployment

- Vercel team: `ghinova`
- Project: `ghinova-assistant` (`prj_9gpuY5zCBOXHxgSmohgn3MPbg4Gy`)
- Endpoint: `https://ghinova-assistant-ghinova.vercel.app/api/chat`
- The initial API deployment is READY but Vercel sign-in protection is still enabled. Public-access change was blocked by automatic approval review and requires user approval.
- Frontend changes remain in a draft PR until public access and a real model response are verified. Do not present the assistant as live yet.
- Deploy this directory as the Vercel project root (Node 22+). No build step or dependencies required. Deployment currently uses inline source files; Git automatic deployment is not connected.
- Account AI Gateway credits/access must be verified with a live request. No paid plan upgrade or credit purchase was made.

## Behavior and boundaries

Official offering details are in `knowledge.json`; update them when the site offerings change. The model may prepare an inquiry via a validated tool call. The visitor explicitly reviews it in the contact form and sends it separately. No email, booking, purchase, arbitrary URL fetching or code execution tool is exposed.

Conversations stay in page memory and are transmitted to Vercel AI Gateway/model provider for answers. This application does not intentionally persist conversations; provider logging/retention policies still apply. The UI discloses processing and warns against sensitive information.

Eight requests/minute per IP per warm instance is best-effort burst protection, not a global quota. Requests have length, output-token and time limits. Before increasing traffic, add persistent rate limiting and an account budget. The origin check is not authentication and cannot block non-browser callers.

## Validation

Run `npm test` from this directory and `node --check ../assistant.js`.
Six tests cover input limits, forbidden roles, tool validation, origin rejection, CORS, missing credentials, and mocked tool-call handling. A real deployed model response and browser QA remain to be checked after public access approval.
