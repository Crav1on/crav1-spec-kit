---
name: fix-live
description: Fix a live/inner-loop failure while tests still pass, then re-prove the live path. Use when unit tests are green but a real call (HTTP, DB, proxy, container publish) fails. Stay inside the spec; do not change spec.md.
disable-model-invocation: true
icon: bug
color: red
---

# Fix live

Tests can pass while the **running** stack is wrong (unpublished ports, Aspire/SQL proxy, missing health, env). You fix that wiring and **re-hit the same live path**. You do not change the product spec to make the failure go away.

This is not `/implement-task` (new T#). This is not `/verify-spec` (full matrix). This is: **one live failure, one in-spec fix, live proof**.

## Find the spec

User @-mention, else the most recently edited tree under `docs/specs/` excluding `_template/`.

Read `spec.md`, `plan.md`, `tasks.md`, constraints/ADRs. Spec wins. Report shape: this skill’s `assets/live-fix.md`.

## Gate (no edits until this is clear)

You need all of:

1. **Symptom** — what fails live (quote logs/status).
2. **Live command** — the exact re-hit (e.g. `POST /register` against the published URL). If they omitted it, **ask** — do not invent a host/port.
3. **Spec bind** — which journey / REQ / acceptance / `T#` that live call is supposed to satisfy.

**Stop** (no fix) if:

- The live behavior is **not** in the spec (new endpoint, new actor, new guarantee). Do not add it. Tell them the spec does not include this path; `/tighten-spec` is for contract changes — this skill will not edit `spec.md`.
- The “fix” would implement a **non-goal** or reopen a rejected ADR.
- This workspace is only the SDD playbook and they did not ask to change an app here.

If tests are *claimed* green, run the repo test command once and record it. If the live command is *claimed* red, run it once and record the failure. Do not skip the before-state.

## Fix (in spec)

Change the **smallest** set of inner-loop / runtime pieces that make the **existing** spec path work:

- Container publish / port mapping
- Dev host / Aspire resource / SQL proxy / connection string
- Env files, compose, launch profiles
- Health used **only** as an inner-loop probe (compose `healthcheck`, resource wait) — not a new public product API unless that API is already in the spec

Do **not**:

- Edit `spec.md`, exports, or acceptance
- Add features, endpoints, or fields the spec does not already require
- “Fix” by weakening tests or deleting the live check
- Refactor unrelated modules

If diagnosis needs a SQL/HTTP health probe and the spec has no public health resource, prefer **operator** checks (compose, `sqlcmd`, `curl` to an existing URL) over a new `/health` product route.

## Verify the fix (required, same turn)

After the change, in this order:

1. **Live** — re-run the **same** command from the gate (same URL, method, payload intent). Must go from fail → pass (or show it still fails).
2. **Tests** — re-run the same test command as the before-state. Must still pass.
3. If they asked for an extra probe (e.g. SQL ready), run that too. Record it. It does not replace the live spec path.

Passing tests alone is **not** proof of this skill. The live re-hit is.

Do not check extra `T#` boxes unless that task’s **stated verify** was this live command and it now passes.

## Write `docs/specs/<slug>/live-fix.md`

Follow this skill’s `assets/live-fix.md` **section order** (TL;DR first). Append a dated entry if the file already exists; do not delete older entries.

Do not rewrite `spec.md`. Do not replace `verify.md`; they may run `/verify-spec` after for the full matrix.

## After (chat)

Same order as the file. TL;DR first:

- Spec bind (REQ / T# / journey)
- Before → after (live command + result)
- Tests still pass? yes/no
- Files changed (wiring only)
- Next: `/verify-spec` if they want the matrix; `/implement-task` if a T# is still unchecked; stop if live+tests are green

## Hard rules

- **Spec is frozen.** If the live path and the spec disagree, stop and say so. Do not patch the spec.
- Do not mark success without the live re-hit output.
- Prefer config/infra over code; if code must change, it only enables the already-specified behavior.
- One live incident per turn unless they batch two commands that are the same failure.
