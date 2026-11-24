# CRAV1 style

Match this shape. Prefer live `git log` when it is available; use these rules when it is not.

## Summary

- One line, sentence case, no trailing period.
- Start with a verb: `Add`, `Adds`, `Implement`, `Update`, `Fix`, `Suppress`, `Decouple`, and similar.
- Name the outcome (what changed and where), not a marketing pitch.
- If the commit completes a numbered task or ticket that appears in the diff, put the id in parentheses at the end, e.g. `(T2)`.
- Do not use Conventional Commits prefixes (`feat:`, `fix:`, `chore:`).

Examples of the shape (not required wording):

- `Implement user registration for the API (T2)`
- `Decouple API startup from database schema creation`
- `Suppress noisy toolchain warning in the host project`

## Description

- CRAV1 style **Description**: hyphen bullets when there is more than one change.
- Each bullet starts with a verb (`Adds`, `Implements`, `Configures`, `Introduces`, `Marks`, …).
- Say what changed and why it matters; mention endpoints, tests, or task-checkbox updates only if they are in the commit.
- A short paragraph (no bullets) is fine for a single small change.
- Do not list every file path.

Multi-change shape:

```
- Adds an endpoint that does X.
- Implements persistence and validation for Y.
- Introduces tests for the success path and the main rejections.
- Marks the related task as completed in the spec docs.
```

Single-change shape:

```
Adds a compiler warning suppression so local builds stay quiet.
```

## Do not

- Marketing or “ship” phrasing.
- Dumping the entire conversation into the message.
- Including `artifacts/`, `bin/`, or `obj/` unless the user explicitly asked to commit them.
- Putting a work-item mention (`#<id>` or `AB#<id>`) in the Summary or in the Description body. The skill appends that line when `docs/specs/<slug>/work-item.md` says to.
