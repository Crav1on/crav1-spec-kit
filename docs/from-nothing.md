# From one sentence to a spec

You do not start in Plan Mode. You do not start by picking Next.js. You start by making the idea small enough to accept or reject.

## Why your old prompt was the wrong *first* prompt

This is a strong **later** reviewer, and it is now the `spec-reviewer` subagent:

- Make requirements explicit and testable
- Propose spec sections, tasks, test strategy, risks
- When there *is* a repo: summarize, plan, file-level suggestions
- Stay concise

What did not belong on turn one:

- “You are Claude Sonnet/Opus…” — pick the model in Cursor; do not bake it into the prompt
- “Preserve existing architecture” — you have none yet
- “When I share code…” — there is no code yet
- Architect + implementer + reviewer in one blob — that jumps to *how* before *what*

## What to run

1. New Agent chat.
2. Type `/spark-to-spec` (or pin it as a Custom Mode with Option/Alt+Enter).
3. Paste **only** the spark plus the line below.

```text
/spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Do not write code. Ask questions first.
```

That slash command *is* the first prompt. The skill contains the rest so you do not re-paste a persona every time.

Use a strong reasoning model for this phase.

## How to iterate (usually 2–4 turns)

| Turn | You do | Agent does |
| --- | --- | --- |
| 1 | Spark + `/spark-to-spec` | Restate, propose v0, ≤7 questions, numbered assumptions |
| 2 | Answer in bullets. Skip with “use assumptions” | Write `docs/specs/<slug>/spec.md` |
| 3 | “v0 is too big” / “offline matters” / “not for teams” | `/tighten-spec` turns each gap into an issue with choices (impact included), one by one |
| 4 | Optional: “review this spec” | Parent agent delegates to **spec-reviewer** |
| 5 | Leftover Open questions | `/resolve-questions` — keep open or answer, one `Q#` at a time |
| Stop | You can demo v0 from the acceptance list; leftover Qs are explicit | Spec is done enough. New chat → Plan Mode → `@spec.md` |

Good iteration messages (short):

- “Primary user is me, solo, evenings. Non-goal: sharing.”
- “Cut anything that needs an account.”
- “Done means I can do X in one sitting. Y is later.”
- “A3 is wrong; the painful part is Z.”

Bad iteration messages:

- “Make it a platform.”
- “Also add AI, mobile, and admin.”
- “Just start coding and we’ll see.”

## After the spec is accepted

New chat so exploration does not pollute implementation.

```text
Plan Mode. @docs/specs/<slug>/spec.md

Turn this spec into an implementation plan and testable tasks.
Do not code yet. Stay inside v0 and the non-goals.
```

Then you review the plan, save it next to the spec, and only then click Build.

If a repo already exists, `@` the relevant folders and the spec-reviewer will apply “preserve existing patterns.”
