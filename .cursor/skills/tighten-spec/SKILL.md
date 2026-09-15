---
name: tighten-spec
description: Iterate an existing spec from critique, answers, or new constraints. Use when a spec.md already exists and the user wants it sharper, smaller, or more testable. Do not write application code.
disable-model-invocation: true
icon: book-open
color: cyan
---

# Tighten spec

You refine a spec in place. The spec is the source of truth; chat is commentary.

## Find the spec

Use the spec the user @-mentions. Otherwise the most recently edited file under `docs/specs/` excluding `_template/`. If several, ask which slug.

## Each turn

1. Summarize what changed in their latest message (2–4 bullets).
2. Patch `spec.md` (and only the spec, unless they also asked to update tasks).
3. Show a short diff-style recap: **Added / Removed / Still open**.
4. Point at any acceptance criterion that is still not falsifiable. Rewrite those.

## Hard rules

- Prefer **cutting scope** over adding features.
- If they introduce architecture or stack, put it in a `## Constraints` section — do not let it replace user journeys.
- Preserve existing architecture and patterns **only when a real codebase exists** and the spec does not call for change. On a greenfield spark, there is nothing to preserve.
- Never “fix” the idea by expanding v0.
- Do not start Plan Mode or write code unless they explicitly ask.

## When the spec is tight enough

Say so when all of these are true:

- One primary user
- v0 vs later is explicit
- Non-goals are written
- Happy, fail, and empty paths exist
- Every acceptance line is a yes/no check
- Open questions are listed, not buried

Then tell them: accept the spec, new chat, Plan Mode (`Shift+Tab`), `@` the spec, build a plan. Optionally ask the `spec-reviewer` subagent for a critique first.
