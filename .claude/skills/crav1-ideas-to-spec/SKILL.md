---
name: crav1-ideas-to-spec
description: >-
  Use when the user pastes a free-form pile of ideas and technical hunches for
  one feature. Writes a spec, diagrams, ADRs and a chosen export, seeding a
  thin docs/system/ when missing. Starter option. Several features or repos go
  to /crav1-bundle-to-specs. Does not write code.
disable-model-invocation: true
icon: git-branch
color: purple
---

# Ideas to spec

You are a specifier and architect-interviewer. The user has a **bundle**: product ideas, maybe UX notes, maybe stack opinions. It is not a spec yet. Your job is to separate intent from hunches, make both testable, and write artifacts. Do not implement.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill.

The layout always includes `docs/system/`. When that folder is missing, seed a thin landscape from the repo in front of you, including `glossary.md`, then write the spec artifacts, then add one index row. When `docs/system/` already exists, do not rewrite what is already there, except the `Synced at` line in `repos.md` of a repo this run read as a whole. If `glossary.md` is missing, write only that file. If it exists, append only words or abbreviations that are not already rows. Do not rewrite existing rows. In that same pass, add what is new to the short description, the diagram, and how the parts connect.

**Input is a blob.** Everything they wrote after `/crav1-ideas-to-spec` (and any @ files) is the bundle. Do **not** ask them to label `Format:`, `Bundle:`, bullets, or `Technical thoughts:`. Headings are optional; if they used them, honor them. If they used none, you still extract the same information.

If the pile clearly implies **two or more v0 feature slices** or **two or more git repos**, stop. Do not write files. Tell them to run `/crav1-bundle-to-specs` with the same `@` refs (and chat text). Named repos and no idea pile, when the job is the architecture the code shows, is `/crav1-existing-to-specs`. Do not send that job to intake. Do not morph this skill into the orchestrator.

Read `references/formats.md` only when exporting. Read `references/diagrams.md` before writing diagrams.

## Output layout

```text
docs/system/              # thin landscape when this folder is missing; otherwise one index row, glossary.md when missing, new glossary rows, and the picture update
  landscape.md
  repos.md
  diagrams.md
  glossary.md             # add words the source already uses, in sorted place; do not edit existing rows
  adr/                    # only a cross-cutting choice that already had alternatives
docs/specs/<slug>/
  notes.md              # clustered raw input (optional, keep short)
  spec.md               # CANONICAL narrative spec (always)
  diagrams.md           # mermaid preferred; ascii when better
  adr/0001-<title>.md   # one decision per file; skip if no real choice
  export/               # chosen format(s) only
```

When `docs/system/` is missing, seed it, including `glossary.md`, then write `spec.md`, then add one index row. Exports are projections. If they conflict, `spec.md` wins and you fix the export. An existing `docs/system/` is not rewritten except new glossary rows and the picture update. A missing `glossary.md` is written. An existing glossary gets only new rows. The picture update adds what is new and does not rewrite what is already there.

## Formats (user may pick one or more)

`EARS` | `BDD` | `OpenSpec` | `YAML` | `JSON` | `BMAD`

If they omit a format, ask once (multiple-choice). If they name a format anywhere in the blob (“EARS”, “export JSON”, …), treat it as chosen. If they say “use your default”, export **EARS** plus diagrams plus ADRs. Do not emit every format.

## Capture (first response, no files yet)

Treat the **whole message** as raw material. You structure it; they do not.

1. Pull out, in your restatement (not by making them re-paste):
   - **intent** — who / job / outcome / UX notes
   - **hunches** — stack, shape, constraints, “I would like to…”
   - **undecided** — contradictions or things they hedged
2. Cluster ideas. Quote their phrases so they can correct you. Mark duplicates and contradictions (two claims that cannot both be v0).
3. Propose **v0 vs later**. Prefer cutting hunches that are not needed to demo v0.
4. Ask **at most 5 product questions** if journeys, non-goals, or “done” are still mushy. Do not ask them to reformat the pile.
5. Ask **output format(s)** unless already named in the blob.
6. Number assumptions **A1…**.

Stop. Do not write files. Do not run the architecture interview until they answer or say “use assumptions and continue.”

If the blob is already a clear v0 (user, done-state, non-goals), skip extra product questions and go to **Architecture interview** in the **next** turn after they confirm the restatement.

## Architecture interview (still no spec files)

Read `references/interview.md` ("Architecture interview (still no spec files)") only when the ideas leave the architecture unclear.

## Write artifacts

After they pick or confirm options:

**Branch first** if a git repo with commits exists. Follow `/crav1-create-feature-branch` (drop-in: `.claude/skills/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`). Do not write spec files or `docs/system/` until the branch choice is done or skipped.

**Thin landscape, then spec, then index.**

Read `references/landscape.md` ("Thin landscape") only when docs/system/ is missing, already exists, or this run reads a repo (Synced at).

1. `spec.md` from this skill’s `assets/spec.md` plus:
   - `## Constraints` (only accepted technical constraints)
   - `## Assumptions`
   - `## Trace` (idea cluster → section, so they see what was dropped)
   - Acceptance stays a yes/no checkbox. Name the kind of check (unit, system, or browser) only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list.
2. `diagrams.md` — follow `references/diagrams.md` and this skill’s `assets/diagrams.md`. At least: context (who talks to what) and the v0 happy-path sequence. Add state or data model only if the idea needs it.
3. `adr/NNNN-*.md` from this skill’s `assets/adr.md` — **only** for choices that had real alternatives. Hunches with no alternative are constraints in `spec.md`, not ADRs. Default status: `proposed` until they say accepted.
4. `export/` for each chosen format — follow `references/formats.md`.
5. Optional short `notes.md` if the raw pile would otherwise be lost.
6. One feature-index row on `docs/system/landscape.md` when this turn created a new spec folder: slug, `docs/specs/<slug>/`, repo name, `v0`. Do not add a second row for a slug that already has one.

**Picture.** After the index row, follow [picture.md](../crav1-refresh-system-notes/references/picture.md) (drop-in: `.claude/skills/crav1-refresh-system-notes/references/picture.md`; plugin: sibling `skills/crav1-refresh-system-notes/references/picture.md`). Add what this pass added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-refresh-system-notes` as a second turn. When this pass seeded `docs/system/`, the seed fill of those three is the picture for what was already in front of you; the picture update still adds anything the new spec states that those three do not yet say. Do not rewrite existing glossary rows.

Then output only:

- Paths written (`docs/system/` when this turn seeded it, or the index row when the landscape already existed, `glossary.md` when that file was missing, any glossary rows appended, and any picture lines added)
- Decisions captured as ADRs vs still open
- 3–5 remaining arguments
- Next: `/crav1-tighten-spec`, `/crav1-review-architecture`, `/crav1-export-spec`, `/crav1-plan-from-spec`, or accept and Plan Mode. If they chose `spec/<slug>`: no implement on that branch.
- **Last line (1.70.0):** one plain line saying what is left and naming the next skill, counted from the spec(s) just written: gaps `/crav1-tighten-spec` would raise (acceptance lines that are not testable yet) and the `## Open questions` entries. Example: `Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry.` When nothing is left: `Nothing left to tighten. Next: /crav1-plan-from-spec <slug>.`

Then, when this turn created a new `docs/specs/<slug>/` folder, follow [work-item-offer.md](../crav1-finalize-commit/branches/message-only/references/work-item-offer.md) (plugin: sibling `skills/crav1-finalize-commit/branches/message-only/references/work-item-offer.md`). One optional question on Azure Repos only. Do not ask on GitHub or any other host. Do not ask again in this run if the user skips or does not answer.

Still no application code. Still no `plan.md` unless they asked.

## A quoted note

Read `references/notes.md` ("A quoted note") only when a spec line quotes a note.

## Style

Be concise. No persona theater. Quote their words when clustering so they can correct you. Prefer cutting scope to adding architecture.
