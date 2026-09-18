---
name: verify-spec
description: Map every v0 acceptance line to tests or UI checks and report pass, fail, or missing. Use after implementation or when the user wants proof against spec.md. Do not add product features.
disable-model-invocation: true
icon: beaker
color: orange
---

# Verify spec

You prove the **running system** (or current tree) against `spec.md`. You do not add features. You do not “fix” the spec to match the code.

## Find the spec

User @-mention, else the most recently edited tree under `docs/specs/` excluding `_template/`.

Read `spec.md` acceptance (and EARS/BDD export if present — spec.md still wins). Read `tasks.md` if it exists. Skim tests and the files `plan.md` said would be touched.

## Build the matrix (no product edits yet)

Every v0 acceptance checkbox / REQ that is in scope gets one row:

| Id | Acceptance (quote) | Evidence | Result |
| --- | --- | --- | --- |
| A1 | … | test or command or UI path, or **missing** | pass / fail / untested / missing |

**Evidence** must be something a stranger could rerun. “Looks fine” is not evidence.

Then:

1. Run the documented test/lint commands from `AGENTS.md` or the repo README when they exist. Record the command and outcome.
2. For UI acceptance, use the browser if available; otherwise mark **untested** and say why.
3. Map `tasks.md` rows: checked but failing verify → defect; unchecked but acceptance already proven → note it.

Write `docs/specs/<slug>/verify.md` with the matrix, commands run, and a short **gaps** list (`G1`, `G2`, …). Do not rewrite `spec.md`.

## Results

- **pass** — evidence ran and matched the acceptance line
- **fail** — evidence ran and contradicted it
- **untested** — could not run (no command, no browser)
- **missing** — no test, no task, no UI path covers it

## After the report

Output:

- Path to `verify.md`
- Counts: pass / fail / untested / missing
- Next:
  - missing or fail on a known `T#` → `/implement-task T#`
  - acceptance that was never a task → `/plan-from-spec` (add a task) or `/tighten-spec` if the line should die
  - all pass → spec is demoable; they can ship / PR

Do not start implementing in this turn unless they already named a `T#` to fix.

## Hard rules

- Do not invent new acceptance. Do not expand v0.
- Do not mark pass without a command, test name, or exercised UI path.
- If the code is right and the spec is wrong, say so and send `/tighten-spec` — do not silently edit the spec.
- If this workspace has no application to run, report **untested** with that reason; do not scaffold an app to get a green matrix.
