# From intake files to specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when you have **1–N files** (notes, markdown, screenshots, diagrams, optional source code as background) that may describe a small app **or** a system with several features and several git repos. This command is a starter option. The seven are in [first-run.md](first-run.md). Asking for startup options names that list and does not run this command.

You still do **not** start by coding. The command writes a **landscape** under `docs/system/`, then one `docs/specs/<slug>/` per accepted v0 feature. Later features do **not** re-run this command.

One-liner? [from-nothing](from-nothing.md) (`/crav1-spark-to-spec`). One unstructured pile that is clearly one feature and one repo? [from-ideas](from-ideas.md) (`/crav1-ideas-to-spec`). Minutes, a transcript, an email, or a chat thread to match against specs that already exist? [from-meeting](from-meeting.md) (`/crav1-meeting-to-specs`). That command writes nothing itself.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

`@` any mix of intent (what to build) and context (existing code or “like this”). No required structure in those files.

```text
/crav1-intake-to-specs
@notes/overview.md
@sketches/flow.png
@legacy-api/

<optional sentence: new system, that code is context — or extract-as-is>

Treat hunches as proposed, not decided.
Do not write code. Map first, then landscape, then one spec per v0 slug.
```

Default if you only `@` a codebase and do not say extract-as-is: **new system, this code is context.**

That slash command *is* the prompt.

## The extra steps (vs ideas)


| Phase            | You                                      | Agent                                                                 |
| ---------------- | ---------------------------------------- | --------------------------------------------------------------------- |
| Map              | `@` intake; confirm or split slugs/repos | Intent vs context, v0 vs later, bulk `A1…`, ready vs mushy per slug   |
| Branch           | Pick `feat/…` or `spec/…` (or stay)    | `/crav1-feature-branch` before `docs/system/` (no push, no PR)        |
| Mushy interview  | Answer only flagged slugs, or “use assumptions” | ≤5 questions per mushy slug, in **this** chat. Workers never interview |
| Landscape        | Accept the map                           | `docs/system/` (`landscape.md`, `repos.md`, diagrams, `glossary.md`, cross-cutting ADRs) |
| Slice specs      | Wait                                     | One isolated worker per v0 slug (`docs/specs/<slug>/`)                |
| Index            | —                                        | Feature table on `landscape.md`, then the picture update (short description, diagram, how the parts connect) |
| Commit (optional)| Glance at files, then `/crav1-finalize-commit` | Prompted next step only; intake does not commit                       |
| Stop             | v0 slugs are demoable from their specs   | Per slug: reviewer → tighten → plan. Not one plan for the universe    |


Bulk assumptions: you confirm them with the map. Ready slugs get no interview. Thin `docs/system/` is still written when Map is one app and one repo.

Repos stay `proposed` until you have a URL. This command does not `git init` or create remotes unless you explicitly ask.

## What gets written

```text
docs/system/
  landscape.md
  repos.md
  diagrams.md
  glossary.md
  adr/
docs/specs/<slug>/
  spec.md
  diagrams.md
  adr/
  export/
```

Human starter copies: `docs/system/_template/` (same files as skill `crav1-intake-to-specs` `assets/` for landscape, including `glossary.md`, and as `assets/system/` on `crav1-spark-to-spec` and `crav1-ideas-to-spec`). Feature spec shape matches ideas-to-spec plus **Repos**, **Constraints**, **Assumptions**, **Trace**.

## Later features

Do not run `/crav1-intake-to-specs` again.

```text
/crav1-spark-to-spec
@docs/system/
@docs/specs/<related>/

Spark: <the new feature>
```

Or `/crav1-ideas-to-spec` if the new thing is already a pile. **New slug.** If `docs/system/` is missing, spark and ideas seed a thin landscape from the repo, including `glossary.md`, then the spec, then one index row. They do not rewrite lines that landscape already has. A missing `glossary.md` is written. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. They do not re-run intake. If you need a new repo: landscape ADR + `repos.md` row, then the spec, then an index row.

## After Index

On an Azure Repos remote, intake then asks once for an optional work-item id. One question lists the new slugs. Skip leaves no `work-item.md`. GitHub and other hosts are not asked. See [from-ideas](from-ideas.md).

If you are done with this dump (not about to rewrite Map output in the same chat):

```text
/crav1-finalize-commit
```

That puts `docs/system/` and the new spec slugs in git. No push. Intake does not commit for you.

## Critique and build (per slug)

Same as [from-ideas](from-ideas.md): `/crav1-architecture-reviewer` with the spec folder attached, then tighten, resolve questions, `/crav1-plan-from-spec` (names a linter when the repo has one, and stops before Build when it does not), optional `/crav1-review-plan` then `/crav1-tighten-plan`, implement or complete-task / complete-tasks / complete-features, verify, fix-from-verify.
