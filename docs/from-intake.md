# From intake files to specs

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when you have **1–N files** (notes, markdown, screenshots, diagrams, optional source code as background) that may describe a small app **or** a system with several features and several git repos.

You still do **not** start by coding. The command writes a **landscape** under `docs/system/`, then one `docs/specs/<slug>/` per accepted v0 feature. Later features do **not** re-run this command.

One-liner? [from-nothing](from-nothing.md) (`/crav1-spark-to-spec`). One unstructured pile that is clearly one feature and one repo? [from-ideas](from-ideas.md) (`/crav1-ideas-to-spec`).

## First prompt

New Agent chat. Strong reasoning model. Not Plan Mode yet.

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

That slash command *is* the prompt. Pin `/crav1-intake-to-specs` as a Custom Mode if you want it on for the session.

## The extra steps (vs ideas)


| Phase            | You                                      | Agent                                                                 |
| ---------------- | ---------------------------------------- | --------------------------------------------------------------------- |
| Map              | `@` intake; confirm or split slugs/repos | Intent vs context, v0 vs later, bulk `A1…`, ready vs mushy per slug   |
| Mushy interview  | Answer only flagged slugs, or “use assumptions” | ≤5 questions per mushy slug, in **this** chat. Workers never interview |
| Landscape        | Accept the map                           | `docs/system/` (`landscape.md`, `repos.md`, diagrams, cross-cutting ADRs) |
| Slice specs      | Wait                                     | One isolated worker per v0 slug (`docs/specs/<slug>/`)                |
| Index            | —                                        | Feature table on `landscape.md`                                       |
| Stop             | v0 slugs are demoable from their specs   | Per slug: reviewer → tighten → plan. Not one plan for the universe    |


Bulk assumptions: you confirm them with the map. Ready slugs get no interview. Thin `docs/system/` is still written when Map is one app and one repo.

Repos stay `proposed` until you have a URL. This command does not `git init` or create remotes unless you explicitly ask.

## What gets written

```text
docs/system/
  landscape.md
  repos.md
  diagrams.md
  adr/
docs/specs/<slug>/
  spec.md
  diagrams.md
  adr/
  export/
```

Human starter copies: `docs/system/_template/` (same files as skill `crav1-intake-to-specs` `assets/` for landscape). Feature spec shape matches ideas-to-spec plus **Repos**, **Constraints**, **Assumptions**, **Trace**.

## Later features

Do not run `/crav1-intake-to-specs` again.

```text
/crav1-spark-to-spec
@docs/system/
@docs/specs/<related>/

Spark: <the new feature>
```

Or `/crav1-ideas-to-spec` if the new thing is already a pile. **New slug.** If you need a new repo: landscape ADR + `repos.md` row, then the spec, then an index row.

## Critique and build (per slug)

Same as [from-ideas](from-ideas.md): `/crav1-architecture-reviewer` `@docs/specs/<slug>/`, then tighten, resolve questions, `/crav1-plan-from-spec`, implement or complete-task, verify, fix-from-verify.
