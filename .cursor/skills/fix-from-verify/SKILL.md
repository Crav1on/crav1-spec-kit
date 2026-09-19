---
name: fix-from-verify
description: Fix one gap reported by /verify-spec (failed, missing, unverified, or not implemented), stay inside the spec, then re-run that row’s evidence. Use after verify-spec. Do not edit spec.md.
disable-model-invocation: true
icon: bug
color: red
---

# Fix from verify

You run this **after `/verify-spec`**. The problem is whatever `verify.md` (or the last verify TL;DR) already listed. You fix **one** gap, in spec, then re-prove **that** row. Inner-loop/live failures (ports, proxies, SQL) are one kind of gap — not the only kind.

Do not change `spec.md`. Do not invent product behavior to get a green matrix.

## Find the work

Spec folder: user @-mention, else most recently edited `docs/specs/` tree excluding `_template/`.

Read, in order:

1. `verify.md` (required if it exists). Chat TL;DR from the last `/verify-spec` in this thread counts as the same source.
2. `spec.md`, `tasks.md`, `plan.md` — spec wins.
3. Report shape: this skill’s `assets/fix-log.md`.

If `verify.md` is missing and they did not paste a verify TL;DR, **stop**. Next: `/verify-spec`. Do not guess gaps from vibes.

## Pick one gap (no edits yet)

Gaps come from the verify TL;DR buckets:

| Verify says | What you may do |
| --- | --- |
| **Implemented, verify failed** | Fix implementation or wiring so the **existing** evidence can pass |
| **Claimed done, unverified** | Run the evidence. If it fails, treat as verify-failed. If it cannot run (no host, unpublished port), that **is** the gap — fix inner-loop so the evidence can run, then run it |
| **Not implemented** | Implement that `T#` the same way `/implement-task` would (one task, its verify line) |
| **Acceptance with no task** | **Do not** add requirements. Stop: `/plan-from-spec` to add a task, or `/tighten-spec` if the line should leave the spec. This skill does not grow the spec |

If they named `T#`, `A#`, or `G#`, that is the gap. Else take the first in this order: verify failed → claimed/unverified → not implemented. List the rest as remaining.

If several failed rows share one cause (e.g. SQL proxy down), say so, still **record** them as one incident, and re-run **each** named evidence after the fix.

**Stop** (no fix) if:

- Closing the gap needs behavior **not** in the spec
- It would implement a **non-goal** or reopen a rejected ADR
- Playbook-only workspace and they did not ask to change an app here

Confirm the before-state: re-run that row’s evidence (or the live command they / verify.md named) once. Quote the failure. Do not skip.

## Fix (in spec)

Smallest change that makes **this** verify row pass:

- Product code for a failed/not-implemented `T#` already in `tasks.md`
- Tests or UI checks that **cover existing** acceptance (new test OK; new acceptance not OK)
- Inner-loop wiring when evidence could not run or failed for connectivity: publish/ports, Aspire/SQL proxy, env, compose waits, operator health probes — not a new public API unless the spec already has it

Do **not**:

- Edit `spec.md`, exports, or acceptance text
- Delete or weaken the failing check to go green
- Refactor unrelated files
- Add endpoints, fields, or actors the spec does not require

## Verify the fix (required, same turn)

1. Re-run **the same evidence** for this gap (test name, UI path, or live HTTP/DB command from verify.md / the user). Fail → pass, or report still failing.
2. If you changed app or config, re-run the repo test command. Must still pass.
3. Extra probes (SQL ready, etc.) are optional **add-ons**. They do not replace the verify row.

Passing tests alone is not enough when the gap was live/untested. The **row’s evidence** is enough when the gap was a failing test.

Update `tasks.md` `[x]` only if that task’s stated verify now passes.

## Write `docs/specs/<slug>/fix-log.md`

Follow this skill’s `assets/fix-log.md` (TL;DR first). **Append** a dated entry if the file exists.

Optionally patch **only this row** in `verify.md` if that file exists (status/evidence). Do not restage the whole matrix — tell them to run `/verify-spec` for a fresh full report.

Do not rewrite `spec.md`.

If an older `live-fix.md` exists, you may append a one-line pointer to the new `fix-log.md` entry. Prefer `fix-log.md` going forward.

## After (chat)

TL;DR first:

- Which verify bucket / id you fixed
- Before → after (the **same** evidence)
- Tests still pass? (if you ran them)
- Files changed
- Remaining ids from verify TL;DR
- Next: `/fix-from-verify` for the next id, or `/verify-spec` to refresh the matrix

## Hard rules

- **Spec is frozen.** Disagreement with the spec → stop, do not patch the spec.
- One gap per turn unless they named a shared cause and listed the ids.
- Do not mark success without re-running that gap’s evidence.
