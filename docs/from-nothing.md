# From one sentence to a spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

You do not start in the host plan UI. You do not start by picking Next.js. You start by making the idea small enough to accept or reject.

`/crav1-spark-to-spec` is that first command whether the repo is **empty** or you are adding a **feature** to an app that already exists. The skill picks **greenfield** vs **brownfield** from context (and from what you @). The layout always includes `docs/system/`. When that folder is missing, this command seeds a thin landscape from the repo (empty or an existing app), then writes the spec, then adds one index row. It fills that landscape from the repo already in front of the agent. It does not open a second interview, and it does not respec the whole product. When `docs/system/` already exists, the landscape stays as it is and this command adds one index row (a repo or ADR row only when the feature needs a new repo). A missing `glossary.md` is written. An existing glossary gets only new rows for words that are not already listed. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. A pile of ideas plus stack hunches is still [from-ideas](from-ideas.md) (`/crav1-ideas-to-spec`). Several files, or several features/repos, is [from-intake](from-intake.md) (`/crav1-intake-to-specs`). An existing spec that is only mushy is `/crav1-tighten-spec`, not a second spark. A later feature on an existing landscape is still this command with `@docs/system/` (new slug).

## Why your old prompt was the wrong *first* prompt

This is a strong **later** reviewer, and it is now the `crav1-spec-reviewer-agent` subagent:

- Make requirements explicit and testable
- Propose spec sections, tasks, test strategy, risks
- When there *is* a repo: summarize, plan, file-level suggestions
- Stay concise

What did not belong on turn one:

- “You are Claude Sonnet/Opus…” — pick the model in the host; do not bake it into the prompt
- Architect + implementer + reviewer in one blob — that jumps to *how* before *what*
- **Greenfield only:** “Preserve existing architecture” / “when I share code…” — there is none yet
- **Brownfield:** skipping the spec and coding the feature into the current tree

## What to run

1. New chat. On Cursor that is Agent chat. On Claude Code, open a session in the product repo. The slash command is the same.
2. Type `/crav1-spark-to-spec`.
3. Paste the spark. `@` the app (and an old spec only if this feature extends it).

**Greenfield** (no app, or you want a new product slice with no existing architecture):

```text
/crav1-spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Do not write code. Ask questions first.
```

**Brownfield** (feature on an existing repo):

```text
/crav1-spark-to-spec
@src
@docs/specs/<existing-product>/spec.md

Spark: <one or two sentences for this feature>

This is a feature on the current app. New spec slug. Preserve existing architecture. Do not write code. Ask questions first.
```

If you `@` an existing spec **without** saying extend, the skill starts a **new** slug for the feature. To change that spec in place, say **extend** or use `/crav1-tighten-spec`.

On a brownfield git repo the skill **prompts** for a branch before it writes files (never a silent checkout, never a PR):

- **`feat/<slug>`** (default) — spec and later build on one branch
- **`spec/<slug>`** — specify-only; you merge that when you want the spec on the default branch, then `/crav1-feature-branch` → `feat/<slug>` to build (so you can specify another feature while this one is implemented)
- **Stay** / **other name**

You can run `/crav1-feature-branch` by itself. The kit does not push or open the pull request; use GitKraken or your git host for that.

**Later feature** (`docs/system/` already exists, from intake or from an earlier spark or ideas run):

```text
/crav1-spark-to-spec
@docs/system/
@docs/specs/<related>/

Spark: <one or two sentences for this feature>

New spec slug. Preserve landscape ADRs and repo boundaries. Do not write code. Ask questions first.
```

That slash command *is* the first prompt. The skill contains the rest so you do not re-paste a persona every time.

Use a strong reasoning model for this phase.

## How to iterate (usually 2–4 turns)

| Turn | You do | Agent does |
| --- | --- | --- |
| 1 | Spark + `/crav1-spark-to-spec` | Restate, name greenfield vs brownfield, propose v0 for **this** slice, ≤7 questions, numbered assumptions |
| 2 | Answer in bullets. Skip with “use assumptions” | When `docs/system/` is missing, seed a thin landscape, including `glossary.md`, write `docs/specs/<slug>/spec.md`, then one index row. When the landscape already exists, add the index row, write `glossary.md` if it is missing, and append only new glossary rows. A meaning the source does not state is `to be researched`. On Azure Repos, one optional work-item id question (skip leaves no file) |
| 3 | “v0 is too big” / “offline matters” / “not for teams” | `/crav1-tighten-spec` turns each gap into an issue with choices (impact included; you can ask for a suggestion), one by one |
| 4 | Optional: “review this spec” | Parent agent delegates to **crav1-spec-reviewer-agent** |
| 5 | Leftover Open questions | `/crav1-resolve-questions` — keep open or answer, one `Q#` at a time |
| Stop | You can demo this slice from the acceptance list; leftover Qs are explicit | Spec is done enough. `/crav1-plan-from-spec`, optional `/crav1-review-plan` / `/crav1-tighten-plan`, then complete-task / implement / verify |

Good iteration messages (short):

- “Primary user is me, solo, evenings. Non-goal: sharing.”
- “Cut anything that needs an account.”
- “Done means I can do X in one sitting. Y is later.”
- “A3 is wrong; the painful part is Z.”
- Brownfield: “Do not add a second login. Reuse the current API host.”

Bad iteration messages:

- “Make it a platform.”
- “Also add AI, mobile, and admin.”
- “Just start coding and we’ll see.”

## After the spec is accepted

New chat so exploration does not pollute implementation.

```text
/crav1-plan-from-spec
@docs/specs/<slug>/spec.md
```

`/crav1-plan-from-spec` writes `plan.md` and `tasks.md`. The host plan UI is not those files ([install.md](install.md)). Then optional `/crav1-review-plan` and `/crav1-tighten-plan` (plan/tasks only). Then `/crav1-complete-task` or `/crav1-implement-task`.

If a repo already exists, `@` the relevant folders so plan and spec-reviewer apply “preserve existing patterns.”
