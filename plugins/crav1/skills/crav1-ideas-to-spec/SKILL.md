---
name: crav1-ideas-to-spec
description: Turn a free-form pile of ideas (and any technical hunches in the same text) into a spec, diagrams, ADRs, and a chosen export format. When docs/system/ is missing, seed a thin landscape from the repo, including glossary.md, then the spec, then one index row. When that folder exists, write glossary.md if it is missing, or append only words that are not already rows. Do not rewrite existing glossary rows. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. Do not rewrite what is already there. Use when the user has more than a one-liner but not a finished spec. Do not write application code. They do not need to structure the input.
disable-model-invocation: true
icon: git-branch
color: purple
---

# Ideas to spec

You are a specifier and architect-interviewer. The user has a **bundle**: product ideas, maybe UX notes, maybe stack opinions. It is not a spec yet. Your job is to separate intent from hunches, make both testable, and write artifacts. Do not implement.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill.

The layout always includes `docs/system/`. When that folder is missing, seed a thin landscape from the repo in front of you, including `glossary.md`, then write the spec artifacts, then add one index row. When `docs/system/` already exists, do not rewrite what is already there, except the `Synced at` cell of a repo this run read as a whole. If `glossary.md` is missing, write only that file. If it exists, append only words or abbreviations that are not already rows. Do not rewrite existing rows. In that same pass, add what is new to the short description, the diagram, and how the parts connect.

**Input is a blob.** Everything they wrote after `/crav1-ideas-to-spec` (and any @ files) is the bundle. Do **not** ask them to label `Format:`, `Bundle:`, bullets, or `Technical thoughts:`. Headings are optional; if they used them, honor them. If they used none, you still extract the same information.

If the pile clearly implies **two or more v0 feature slices** or **two or more git repos**, stop. Do not write files. Tell them to run `/crav1-intake-to-specs` with the same `@` refs (and chat text). Named repos and no idea pile, when the job is the architecture the code shows, is `/crav1-repos-to-spec`. Do not send that job to intake. Do not morph this skill into the orchestrator.

Read `references/formats.md` only when exporting. Read `references/diagrams.md` before writing diagrams.

## Output layout

```text
docs/system/              # thin landscape when this folder is missing; otherwise one index row, glossary.md when missing, new glossary rows, and the picture update
  landscape.md
  repos.md
  diagrams.md
  glossary.md             # append words the source already uses; do not edit existing rows
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
4. Ask **at most 5 product questions** if journeys, non-goals, or “done” are still mushy. Use the questions tool when available. Do not ask them to reformat the pile.
5. Ask **output format(s)** unless already named in the blob.
6. Number assumptions **A1…**.

Stop. Do not write files. Do not run the architecture interview until they answer or say “use assumptions and continue.”

If the blob is already a clear v0 (user, done-state, non-goals), skip extra product questions and go to **Architecture interview** in the **next** turn after they confirm the restatement.

## Architecture interview (still no spec files)

Ask **at most 7** technical questions. Prefer options, not essays. Cover only what the bundle actually implies:

- System boundary: what is in-process vs external
- Data: source of truth, ownership, retention
- Control flow: sync vs async, who waits
- Auth/trust: who is allowed to do the risky thing
- Failure: timeout, retry, idempotency, what the user sees
- Constraints they already stated (language, cloud, offline, existing repo)
- What must **not** change if a codebase exists

Then offer **2–3 architecture options** at the same abstraction level (not “use Redis vs not” mixed with “monolith vs 12 microservices”). For each: one-line shape, one good, one bad.

Do **not** pick a winner unless they already did. List which hunches would become ADRs vs which are implementation details (those stay out of requirements).

Stop again.

## Write artifacts

After they pick or confirm options:

**Branch first** if a git repo with commits exists. Follow `/crav1-feature-branch` (drop-in: `.cursor/skills/crav1/crav1-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-feature-branch/SKILL.md`). Do not write spec files or `docs/system/` until the branch choice is done or skipped.

**Thin landscape, then spec, then index.**

When `docs/system/` does not exist (greenfield or brownfield, including an existing app), create it before the spec from this skill’s `assets/system/` (same files as `docs/system/_template/` and as intake `assets/` `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr.md`):

| File | Fill |
| --- | --- |
| `landscape.md` | One short paragraph of what is in front of you (the app when it exists; otherwise the bundle). **v0** is this slice. **Later** stays short. Bulk `A#`s are the assumptions already listed. Constraints are only ones the repo or the bundle already shows. Under `## How the parts connect`, one line per connection the repo or the bundle already states. Do not invent a connection. Leave the feature index empty until the spec exists. |
| `repos.md` | The repo in front of you. Status `exists` when this checkout is a real repo; `proposed` until a URL exists. One boundaries line only when the repo already shows one. Include the `Synced at` column. Fill that cell only when this run read that whole repo, as under **Synced at** below. |
| `diagrams.md` | One system-context diagram of what is actually there. One heading, one sentence, one fence. Do not invent services. Slice sequences stay in `docs/specs/<slug>/diagrams.md`. |
| `glossary.md` | From `assets/system/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | From `assets/system/adr.md` only when a cross-cutting choice already had real alternatives. Otherwise write no ADR. Slice ADRs stay under `docs/specs/<slug>/adr/`. |

Fill those files from the repo in front of you and from answers already given. Do not ask a landscape interview. Do not run `/crav1-intake-to-specs`. Do not respec the whole product. If this slice needs a repo that is not the checkout in front of you, add that `repos.md` row and a landscape ADR in this seed, before the spec.

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the repo in front of you, the bundle, and answers already given. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that source already uses. When that same source already says the expansion or meaning, put that text in Meaning. When the source never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the source already treats that word as a term. Write the file even when it has no rows. When `glossary.md` already exists, append only words or abbreviations that are not already rows. Do not rewrite, reorder, or edit existing rows. Do not change a Meaning cell that already has text. Do not run an extra interview.

When `docs/system/` already exists, do not rewrite `repos.md` or existing ADRs except the new-repo case below and the `Synced at` cell of a repo this run read as a whole, and do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. If `glossary.md` is missing, write only that file from the same sources and the same glossary rules. If it exists, append only new rows under those rules. If they need a new repo, write a landscape ADR from `assets/system/adr.md` and a `repos.md` row before the spec. Those are the only edits before the spec. The index row and the picture update come after the spec exists.

**Synced at.** Where this run reads a repo, record the commit it actually read. `Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`.

When this run reads a whole repo, set that repo's `Synced at` cell to the branch and commit actually read. When that branch is already listed, replace that branch's entry. Leave every other branch in the cell. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the column is missing, add it. Other repos' new cells stay empty. Do not write a slice `Synced at` line for a repo this run read as a whole.

When this run reads only one slice, do not touch the repo column. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. One line per repo. Update the line for that repo. Leave other `Synced at` lines.

Do not stamp a repo or a slice this run did not read. An empty cell stays empty. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates.

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

**Picture.** After the index row, follow [picture.md](../crav1-keep-current/references/picture.md) (drop-in: `.cursor/skills/crav1/crav1-keep-current/references/picture.md`; plugin: sibling `skills/crav1-keep-current/references/picture.md`). Add what this pass added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-keep-current` as a second turn. When this pass seeded `docs/system/`, the seed fill of those three is the picture for what was already in front of you; the picture update still adds anything the new spec states that those three do not yet say. Do not rewrite existing glossary rows.

Then output only:

- Paths written (`docs/system/` when this turn seeded it, or the index row when the landscape already existed, `glossary.md` when that file was missing, any glossary rows appended, and any picture lines added)
- Decisions captured as ADRs vs still open
- 3–5 remaining arguments
- Next: `/crav1-tighten-spec`, `/crav1-architecture-reviewer`, `/crav1-export-spec`, `/crav1-plan-from-spec`, or accept and Plan Mode. If they chose `spec/<slug>`: no implement on that branch.

Then, when this turn created a new `docs/specs/<slug>/` folder, follow [work-item-offer.md](../crav1-draft-commit-message/references/work-item-offer.md) (plugin: sibling `skills/crav1-draft-commit-message/references/work-item-offer.md`). One optional question on Azure Repos only. Do not ask on GitHub or any other host. Do not ask again in this run if the user skips or does not answer.

Still no application code. Still no `plan.md` unless they asked.

## Style

Be concise. No persona theater. Quote their words when clustering so they can correct you. Prefer cutting scope to adding architecture.
