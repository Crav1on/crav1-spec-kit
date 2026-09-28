# Intake slice worker

The parent launches **crav1-intake-slice-agent** for **one** slug. This file is the protocol. The worker is not a user-facing slash command.

## Parent passes (and the worker may use only)

- Assigned **slug** and a one-paragraph **cluster** (intent vs hunches for this slice)
- Paths to `docs/system/` (must read; landscape ADRs and bulk `A#`s win)
- Intent vs context refs that apply to this slice
- Bulk `A1…` plus any mushy-interview answers for this slug
- Chosen **export format(s)**
- **Repos** this spec may touch
- Template paths: this skill’s `assets/spec.md`, `assets/spec-diagrams.md` (write as `diagrams.md`), `assets/adr.md` (drop-in also `.cursor/agent-assets/crav1-intake-slice-agent/`; plugin also `agent-assets/crav1-intake-slice-agent/`)
- Format and diagram recipes: `crav1-ideas-to-spec` `references/formats.md` and `references/diagrams.md`

## Worker does

1. Write `docs/specs/<slug>/` using ideas-to-spec Write artifacts:
   - `spec.md` from `assets/spec.md` plus `## Repos`, `## Constraints` (accepted technical constraints only), `## Assumptions`, `## Trace` (cluster → section)
   - `diagrams.md` from `assets/spec-diagrams.md` — at least context + v0 sequence for **this** slice
   - `adr/NNNN-*.md` only for choices that had real alternatives **inside this slice**. Do not duplicate landscape ADRs. Default status `proposed`
   - `export/` for each chosen format
   - Optional short `notes.md` if the cluster would otherwise be lost
2. Copy applicable bulk `A#`s into `## Assumptions`. Add **slice-local** `A#`s only if intake forces a guess the parent never made.
3. List allowed repos on `## Repos`.
4. Return: paths written, ADRs vs open, 3–5 remaining arguments.

## Worker must not

- Interview, ask format, or pause for Approvals & Execution
- Write or edit another slug
- Rewrite `docs/system/` (no landscape, repos table, or system ADRs)
- Invent a second system shape (landscape wins)
- Write application code, `plan.md`, `tasks.md`, `work-item.md`, or create git remotes
- Ask for a work item (the parent offers once after Index)
- Silently resolve ungrounded requirements — leave Open questions

If a requirement cannot be grounded in intake, bulk `A#`s, or mushy answers, it is an Open question, not a fake SHALL.

## STATUS (worker must end with this)

```text
STATUS: done | blocked
SLUG: <slug>
PATHS: docs/specs/<slug>/…
DETAIL: one line if blocked
```
