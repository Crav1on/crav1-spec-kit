# From one sentence to a spec

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

You do not start in Plan Mode. You do not start by picking Next.js. You start by making the idea small enough to accept or reject.

`/crav1-spark-to-spec` is that first command whether the repo is **empty** or you are adding a **feature** to an app that already exists. The skill picks **greenfield** vs **brownfield** from context (and from what you @). A pile of ideas plus stack hunches is still [from-ideas](from-ideas.md) (`/crav1-ideas-to-spec`). Several files, or several features/repos, is [from-intake](from-intake.md) (`/crav1-intake-to-specs`). An existing spec that is only mushy is `/crav1-tighten-spec`, not a second spark. After `docs/system/` exists, a new feature is still this command with `@docs/system/` (new slug).

## Why your old prompt was the wrong *first* prompt

This is a strong **later** reviewer, and it is now the `crav1-spec-reviewer` subagent:

- Make requirements explicit and testable
- Propose spec sections, tasks, test strategy, risks
- When there *is* a repo: summarize, plan, file-level suggestions
- Stay concise

What did not belong on turn one:

- “You are Claude Sonnet/Opus…” — pick the model in Cursor; do not bake it into the prompt
- Architect + implementer + reviewer in one blob — that jumps to *how* before *what*
- **Greenfield only:** “Preserve existing architecture” / “when I share code…” — there is none yet
- **Brownfield:** skipping the spec and coding the feature into the current tree

## What to run

1. New Agent chat.
2. Type `/crav1-spark-to-spec` (or pin it as a Custom Mode with Option/Alt+Enter).
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

**Later feature** (after `/crav1-intake-to-specs` wrote `docs/system/`):

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
| 2 | Answer in bullets. Skip with “use assumptions” | Write `docs/specs/<slug>/spec.md` |
| 3 | “v0 is too big” / “offline matters” / “not for teams” | `/crav1-tighten-spec` turns each gap into an issue with choices (impact included; you can ask for a suggestion), one by one |
| 4 | Optional: “review this spec” | Parent agent delegates to **crav1-spec-reviewer** |
| 5 | Leftover Open questions | `/crav1-resolve-questions` — keep open or answer, one `Q#` at a time |
| Stop | You can demo this slice from the acceptance list; leftover Qs are explicit | Spec is done enough. `/crav1-plan-from-spec` then `/crav1-complete-task` / `/crav1-implement-task` / `/crav1-verify-spec` |

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

Or Plan Mode with the same spec attached. Then you review `plan.md` / `tasks.md`, and only then `/crav1-complete-task` or `/crav1-implement-task`.

If a repo already exists, `@` the relevant folders so plan and spec-reviewer apply “preserve existing patterns.”
