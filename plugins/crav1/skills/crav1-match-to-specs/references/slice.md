# Match slice

The parent writes **one** `docs/specs/<slug>/` in this chat, or hands this file to **one** worker for this slug. This file is the protocol. It is not a slash command.

Do not use `crav1-intake-slice-agent` or that agent's prompt. Intake writes a buildable v0 spec. This protocol writes a match.

## Parent passes (and a worker may use only)

- Assigned **slug** and a short **title**
- **Match status**: `done`, `partial`, or `not in the code`
- **Repo** this slice belongs to (where the behavior is, or would be). The spec file still goes in the destination repo from the first question
- **What the dump says** for this slice (quotes or a close paraphrase)
- **Paths** read in that repo, or none
- **Trace**, split three ways:
  - read from the code
  - accepted from the dump because the map confirmation left it in
  - inferred (in the dump or in a reading, and not confirmed)
- Open questions already on the confirmed map for this slice
- **Source folders** the parent already wrote for an imported source this slice quotes: `docs/sources/YYYY-MM-DD-<slug>/`. Omit this when the parent wrote none. The lines to add are in the imported-sources convention (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`)
- Template: this skill’s `assets/spec.md` (drop-in: `.cursor/skills/crav1/crav1-match-to-specs/assets/spec.md`; plugin: this skill’s `assets/spec.md`)
- Path to `docs/system/` as already written (read it; do not edit it)

A worker that does not receive the match status and the trace does not write.

## Done or partial

Write `docs/specs/<slug>/spec.md` from `assets/spec.md`.

- **Status** is the confirmed match status. Do not upgrade it.
- **What the dump says** is the dump, not a new product brief.
- **In the code** lists repo paths that support the slice and what those paths show. Partial: also say what is missing, using the dump’s words.
- **Trace** keeps the three labels. Confirmed dump facts are accepted, not inferred. Anything not on the confirmed map stays inferred or is left out. When the parent passed a source folder, add the `Source:` and `Trace:` lines from the imported-sources convention. Do not import the file again. Do not commit.
- **Open questions** stay open. Do not answer them in the body.
- Add a normal spec section only when the dump or the code supports it: Problem, Goals, Non-goals, Users and journeys, Acceptance criteria, Constraints, Assumptions. Omit the section when it does not. Do not invent acceptance criteria, journeys, or a done-state to make the file look buildable. A checkbox the dump or the code already states is yes/no. Name unit, system, or browser only when that kind is already obvious there. Otherwise leave the kind for plan. Do not invent a test list.

## Not in the code

Thin. Same template, and only these parts:

- **Status** `not in the code` and the repo the map named
- **What the dump says**
- One sentence that the code does not have it
- **Trace** present and empty
- **Open questions**

Do not add In the code. Do not add Problem, Goals, Acceptance criteria, or any other section. Do not invent a design so the slice can be planned. More information can be added later, until planning. This command does not add it.

## Either status

Write `spec.md` only. Do not write `diagrams.md`, `plan.md`, `tasks.md`, `export/`, `adr/`, `notes.md`, or `work-item.md`.

Do not edit `docs/system/`. Do not write another slug. Do not write `docs/sources/`. The parent already wrote a source folder when one was needed. Do not interview. Do not plan, implement, or commit. Do not write application code.

## STATUS (a worker must end with this)

```text
STATUS: done | blocked
SLUG: <slug>
MATCH: done | partial | not in the code
PATHS: docs/specs/<slug>/spec.md
DETAIL: one line if blocked
```
