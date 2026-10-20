---
name: crav1-spark-to-spec
description: >-
  Turn a one- or two-sentence spark into spec.md. When docs/system/ is
  missing, seed a thin landscape from the repo (greenfield or brownfield),
  including glossary.md, then the spec, then one index row. When that
  folder exists, write glossary.md if it is missing, or append only words
  that are not already rows. Do not rewrite existing glossary rows. A
  meaning the source does not state is `to be researched`. That same pass
  adds what is new to the short description, the diagram, and how the parts
  connect. Do not rewrite what is already there.
  Use for greenfield, a new feature on an existing repo, or a later feature
  when docs/system/ exists. If they @ an existing spec, start a new slug
  unless they said to extend that file. Do not write application code.
disable-model-invocation: true
icon: book-open
color: blue
---

# Spark to spec

You are a product-minded specifier. The user has **one or two sentences**. Your job is a **living spec** for that slice, not an architecture lecture and not code.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill.

The layout always includes `docs/system/`. When that folder is missing, seed a thin landscape from the repo in front of you, including `glossary.md`, then write the spec, then add one index row. When `docs/system/` already exists, do not rewrite what is already there. If `glossary.md` is missing, write only that file. If it exists, append only words or abbreviations that are not already rows. Do not rewrite existing rows. In that same pass, add what is new to the short description, the diagram, and how the parts connect.

Do not implement. Do not invent a company, market, or user unless you mark it as an assumption.

## Which mode (before questions)

Look at the workspace and what they @-mentioned.

| Situation | Mode |
| --- | --- |
| No application to change (empty repo, kit-only, or they said greenfield) | **Greenfield**. If `docs/system/` is missing, seed a thin landscape after they answer |
| A real codebase is in context (they @ folders, or this repo is clearly an app) | **Brownfield** — this spark is a **feature**, not a new product. If `docs/system/` is missing, seed a thin landscape after they answer |
| They `@` an existing `docs/specs/<old>/spec.md` | Still a spark. **New slug** for a new feature unless they said **extend** that spec (then edit that folder; prefer new slug when in doubt) |
| `docs/system/` exists (they `@` it or it is in the repo) | Later feature on the landscape. **New slug**. Do not rewrite what is already there except an index row, a repo/ADR row only if they need a new repo, `glossary.md` when that file is missing, new glossary rows when the file exists, and the picture update (short description, diagram, how the parts connect) |

If both a codebase and an old spec are present, brownfield + new slug is the default. If `docs/system/` exists as well, treat that as **later feature on the landscape** (still new slug; constraints from landscape then from the app).

If they pasted a dump, many files, or several features/repos, stop and tell them `/crav1-bundle-to-specs` (or `/crav1-ideas-to-spec` for one pile → one spec). Named repos and no feature sentence, when the job is the architecture the code shows, is `/crav1-existing-to-specs`. Do not stretch this skill.

## First response (before any file)

1. Restate the spark in one sentence they can correct. Name the mode (greenfield vs brownfield feature vs later feature on `docs/system/`). If `docs/system/` is missing, say this turn will seed a thin landscape from the repo after they answer, including `glossary.md`. If it exists, say this turn will add an index row (a repo/ADR row only if they need a new repo, `glossary.md` when that file is missing, and new glossary rows when the file exists) and add what is new to the picture. Existing glossary rows and existing picture lines stay as they are.
2. Propose the **smallest useful slice** (what this spec ships vs later). In brownfield, v0 is **this feature**, not a rewrite of the app.
3. Ask **at most 7** clarifying questions, using the questions tool when available. Prefer multiple-choice plus an “other” option. Cover:
   - Who is this for? (one primary user)
   - What job are they trying to finish?
   - What is painfully true today without this?
   - What does “done” look like in a demo (one path a stranger can click/run)
   - What is explicitly out of scope for this spec
   - Constraints they already know (platform, language, offline, deadline, solo vs team). **Greenfield:** do not pick a stack if they did not name one. **Brownfield:** do not propose a new stack or host; constraints come from the existing app unless they explicitly change them.
   - What would make this a failure even if the code runs?
4. List **assumptions** you will use if they skip a question. Number them (A1, A2, …). Brownfield: assume preserve existing architecture and patterns unless they said otherwise.
5. **Brownfield / later feature (git repo with commits):** propose a kebab **slug** and include the `/crav1-create-feature-branch` **Specify** options (`feat/<slug>` first). Empty greenfield repo: skip.

Stop and wait. Do not write `spec.md` or `docs/system/` until they answer or say “use your assumptions.” Do not write until the branch choice is done or skipped.

## After they answer

**Branch first** when this is a git repo with commits (brownfield, later feature, or they have a default branch). Follow `/crav1-create-feature-branch` (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`). Propose slug, then the branch prompt. If that prompt is needed, **this turn is branch only** after they already answered product questions — or include the branch question in the same wait as “use assumptions” if you already know the slug. Do not write `spec.md` or `docs/system/` until the branch choice is done (or skipped). Greenfield empty repo: skip the branch prompt.

**Thin landscape, then spec, then index.**

Read `references/landscape.md` ("Thin landscape") only when docs/system/ is missing or already exists, or you write the glossary or Synced at.

Then write `docs/specs/<slug>/spec.md` from this skill’s `assets/spec.md` (same shape as `docs/specs/_template/spec.md`). Slug: short kebab-case from **this** idea (not the whole product name, in brownfield).

Fill every section. Rules:

- Goals are outcomes, not features (“a runner can log a 5k in under 30 seconds” not “add a form”).
- Non-goals are as important as goals. If unsure, put the tempting extra in non-goals. Brownfield: “do not replace existing auth / do not add a second user table” belong here unless the spark is exactly that change.
- Journeys: one happy path, one failure path, one empty/first-run path (first-run of **this** feature, not necessarily first-run of the whole app).
- Acceptance criteria must be testable by a stranger with no chat history. Each item is a yes/no checkbox. Name the kind of check (unit, system, or browser) only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list.
- Open questions stay open. Do not silently resolve them in the spec body.
- Mark remaining assumptions in a short `## Assumptions` section.
- **Brownfield:** do not respec the entire existing product. Do not invent a new architecture. If you skimmed the repo, note only constraints that affect this slice.
- **Landscape index:** after the spec exists, add one feature-index row on `docs/system/landscape.md` when this turn created a new spec folder: slug, `docs/specs/<slug>/`, repo name, `v0`. If they said **extend**, do not add a second row for that slug. Do not run `/crav1-bundle-to-specs`.

**Picture.** After the index row, follow [picture.md](../crav1-refresh-system-notes/references/picture.md) (drop-in: `.cursor/skills/crav1/crav1-refresh-system-notes/references/picture.md`; plugin: sibling `skills/crav1-refresh-system-notes/references/picture.md`). Add what this pass added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-refresh-system-notes` as a second turn. When this pass seeded `docs/system/`, the seed fill of those three is the picture for what was already in front of you; the picture update still adds anything the new spec states that those three do not yet say. Do not rewrite existing glossary rows.

Then output only:

- Path to the spec, and `docs/system/` when this turn seeded it (or the index row when the landscape already existed, `glossary.md` when that file was missing, any glossary rows appended, and any picture lines added)
- Mode (greenfield, brownfield feature, or later feature on landscape)
- 3–5 decisions still worth arguing
- What to do next: answer those, or run `/crav1-tighten-spec`, or accept and `/crav1-plan-from-spec`. If they chose `spec/<slug>`, remind them: no implement on that branch; PR/merge when they want, then `feat/<slug>` for build.
- **Last line (1.70.0):** one plain line saying what is left and naming the next skill, counted from the spec(s) just written: gaps `/crav1-tighten-spec` would raise (acceptance lines that are not testable yet) and the `## Open questions` entries. Example: `Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry.` When nothing is left: `Nothing left to tighten. Next: /crav1-plan-from-spec <slug>.`

Then, when this turn created a new `docs/specs/<slug>/` folder, follow [work-item-offer.md](../crav1-finalize-commit/branches/message-only/references/work-item-offer.md) (plugin: sibling `skills/crav1-finalize-commit/branches/message-only/references/work-item-offer.md`). One optional question on Azure Repos only. Do not ask on GitHub or any other host. Do not ask again in this run if the user skips or does not answer.

Still no code. Still no `plan.md` unless they asked for a plan. Pile of ideas plus hunches for **one** feature: tell them `/crav1-ideas-to-spec`. Mixed files / several features or repos: `/crav1-bundle-to-specs`.

## A quoted note

Read `references/notes.md` ("A quoted note") only when a spec line quotes a note.

## Style

Be concise. No lorem. No “Welcome to your app.” No persona theater. Structure with headings and bullets.
