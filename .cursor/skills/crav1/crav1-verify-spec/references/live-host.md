# Live host refresh (before evidence)

Use this when verify evidence hits a **running** process, not only in-process tests.

Examples: Aspire AppHost + an API resource, `docker compose`, a published URL, `npm run dev`, a browser against localhost.

## When to refresh

Refresh **before** running that evidence if **any** of these are true:

- Product code or config for that service changed since the host last started (typical after `/crav1-implement-task` or a fix)
- The last request still looks like the **old** API (stale route, old contract, old HTML)
- Aspire / compose / the dashboard shows the resource as unhealthy, not started, or on an old revision

Do **not** refresh for unit/integration tests that start the app **inside the test process** unless those tests themselves require an external host.

## How (smallest step that loads the new bits)

Read `AGENTS.md`, repo README, and `plan.md` first. Use the command they name.

Order of preference:

1. **Documented restart** — e.g. restart the Aspire resource, `dotnet run` on the AppHost, compose `up --build` for the service you changed, the documented watch/reload command.
2. **Health wait** — poll the documented health URL, Aspire resource state, or compose `healthy` until ready or a short timeout (about 60s unless the repo says otherwise).
3. **Then** run the verify evidence (HTTP, UI, SQL) against the **current** URL/port from the dashboard or docs. Do not assume yesterday’s port.

Aspire-specific: changing the API project does not always hot-reload the running resource. Prefer restarting **that resource** (or the AppHost if that is what the repo documents). Do not invent a new public API or a second host to “make verify easier.”

## If you cannot refresh

Do **not** mark **pass**. Mark **untested** / **claimed done, unverified**. In chat, say exactly what they must do (example: “Restart `apiservice` in the Aspire dashboard, then reply `ready`”).

In `/crav1-complete-task` / `/crav1-complete-tasks`, that is a **gate**: wait for `ready` or `stop`. Do not keep verifying against a stale host.

## Record

In `verify.md` **Commands run**, include:

- What you refreshed (or “no live host; in-process tests only”)
- The wait/health command and outcome
- Then the evidence commands
