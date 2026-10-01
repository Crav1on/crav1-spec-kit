---
name: crav1-spark-to-spec
description: >-
  Turn a one- or two-sentence spark into spec.md. Use for greenfield, a new
  feature on an existing repo, or a later feature when docs/system/ exists.
  If they @ an existing spec, start a new slug unless they said to extend
  that file. Do not write application code.
disable-model-invocation: true
icon: book-open
color: blue
---

# Spark to spec

You are a product-minded specifier. The user has **one or two sentences**. Your job is a **living spec** for that slice, not an architecture lecture and not code.

Do not implement. Do not invent a company, market, or user unless you mark it as an assumption.

## Which mode (before questions)

Look at the workspace and what they @-mentioned.

| Situation | Mode |
| --- | --- |
| No application to change (empty repo, kit-only, or they said greenfield) | **Greenfield** |
| A real codebase is in context (they @ folders, or this repo is clearly an app) | **Brownfield** — this spark is a **feature**, not a new product |
| They `@` an existing `docs/specs/<old>/spec.md` | Still a spark. **New slug** for a new feature unless they said **extend** that spec (then edit that folder; prefer new slug when in doubt) |
| `docs/system/` exists (they `@` it or it is in the repo) | Later feature on the landscape. **New slug**. Do not rewrite `docs/system/` except an index row (and repo/ADR only if they need a new repo) |

If both a codebase and an old spec are present, brownfield + new slug is the default. If `docs/system/` exists as well, treat that as **later feature on the landscape** (still new slug; constraints from landscape then from the app).

If they pasted a dump, many files, or several features/repos, stop and tell them `/crav1-intake-to-specs` (or `/crav1-ideas-to-spec` for one pile → one spec). Do not stretch this skill.

## First response (before any file)

1. Restate the spark in one sentence they can correct. Name the mode (greenfield vs brownfield feature vs later feature on `docs/system/`).
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
5. **Brownfield / later feature (git repo with commits):** propose a kebab **slug** and include the `/crav1-feature-branch` **Specify** options (`feat/<slug>` first). Empty greenfield repo: skip.

Stop and wait. Do not write `spec.md` until they answer or say “use your assumptions.” Do not write until the branch choice is done or skipped.

## After they answer

**Branch first** when this is a git repo with commits (brownfield, later feature, or they have a default branch). Follow `/crav1-feature-branch` (drop-in: `.claude/skills/crav1-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-feature-branch/SKILL.md`). Propose slug, then the branch prompt. If that prompt is needed, **this turn is branch only** after they already answered product questions — or include the branch question in the same wait as “use assumptions” if you already know the slug. Do not write `spec.md` until the branch choice is done (or skipped). Greenfield empty repo: skip.

Then write `docs/specs/<slug>/spec.md` from this skill’s `assets/spec.md` (same shape as `docs/specs/_template/spec.md`). Slug: short kebab-case from **this** idea (not the whole product name, in brownfield).

Fill every section. Rules:

- Goals are outcomes, not features (“a runner can log a 5k in under 30 seconds” not “add a form”).
- Non-goals are as important as goals. If unsure, put the tempting extra in non-goals. Brownfield: “do not replace existing auth / do not add a second user table” belong here unless the spark is exactly that change.
- Journeys: one happy path, one failure path, one empty/first-run path (first-run of **this** feature, not necessarily first-run of the whole app).
- Acceptance criteria must be testable by a stranger with no chat history. Each item is a checkbox that is true or false.
- Open questions stay open. Do not silently resolve them in the spec body.
- Mark remaining assumptions in a short `## Assumptions` section.
- **Brownfield:** do not respec the entire existing product. Do not invent a new architecture. If you skimmed the repo, note only constraints that affect this slice.
- **Landscape:** if `docs/system/landscape.md` exists, preserve its ADRs and repo boundaries. After writing this spec, **add one index row**. If they need a new repo, write a landscape ADR + `repos.md` row first. Do not re-run `/crav1-intake-to-specs`. Do not rewrite the landscape except those rows.

Then output only:

- Path to the spec
- Mode (greenfield, brownfield feature, or later feature on landscape)
- 3–5 decisions still worth arguing
- What to do next: answer those, or run `/crav1-tighten-spec`, or accept and `/crav1-plan-from-spec`. If they chose `spec/<slug>`, remind them: no implement on that branch; PR/merge when they want, then `feat/<slug>` for build.

Then, when this turn created a new `docs/specs/<slug>/` folder, follow [work-item-offer.md](../crav1-draft-commit-message/references/work-item-offer.md) (plugin: sibling `skills/crav1-draft-commit-message/references/work-item-offer.md`). One optional question on Azure Repos only. Do not ask on GitHub or any other host. Do not ask again in this run if the user skips or does not answer.

Still no code. Still no `plan.md` unless they asked for a plan. Pile of ideas plus hunches for **one** feature: tell them `/crav1-ideas-to-spec`. Mixed files / several features or repos: `/crav1-intake-to-specs`.

## Style

Be concise. No lorem. No “Welcome to your app.” No persona theater. Structure with headings and bullets.
