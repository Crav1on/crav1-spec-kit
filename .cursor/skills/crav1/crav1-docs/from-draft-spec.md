# From a draft spec to an accepted spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a starter has written `docs/specs/<slug>/spec.md` and it is not yet good enough to plan from. The goal is a spec you accept: acceptance lines a stranger could mark yes or no, non-goals, and only the open questions you choose to keep. Every step here edits the spec one issue at a time, after you pick. None of them writes code or a plan.

On a brownfield repo, put the work on a branch first. `/crav1-feature-branch` offers `feat/<slug>` (spec and build on one branch) or `spec/<slug>` (specify only; build later on `feat/<slug>` after this spec is on the default branch). Starters already ask this; run it on its own when you skipped that prompt.

## First prompt

New chat. Strong reasoning model. Not the host plan UI.

When the design has real hunches (diagrams, ADRs, stack choices), start with a critique:

```text
/crav1-architecture-reviewer
@docs/specs/<slug>/

Critique the design. Number the issues. Do not edit the spec.
```

Otherwise start with tighten:

```text
/crav1-tighten-spec
@docs/specs/<slug>/spec.md
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Branch (brownfield, optional) | `/crav1-feature-branch <slug>`, pick `feat/<slug>` or `spec/<slug>` | Reads the current branch, the default branch, and whether the tree is dirty. A dirty tree does not check out. No push, no pull request |
| Critique (optional) | `/crav1-architecture-reviewer` | Starts the `crav1-architecture-reviewer-agent` subagent. Returns numbered issues `I#` in chat. Writes nothing. Names `/crav1-security-review` as an optional next step and does not run it |
| Independent spec review (optional) | Ask for a spec review | The `crav1-spec-reviewer-agent` subagent critiques product and spec. Writes nothing |
| Tighten | `/crav1-tighten-spec`, then answer one issue at a time: a letter, a batch such as `I1 A, I3 C`, or `suggest` | Lists issues `I1`, `I2`, … (reviewer findings in this chat first). For the current issue: the finding, why it matters, and two to four options with their impact. Patches only that issue after you pick. `suggest` recommends one and does not patch |
| Code first (partial slices) | Confirm the repo and branch when asked | When the slice is partial or `## In the code` names paths, reads that committed code before wording issues. A disagreement with the code is called out, not silently rewritten |
| Open questions | `/crav1-resolve-questions`, then keep each open or answer it | One `Q#` at a time. An answer becomes spec text, a constraint, a non-goal, or an ADR, with its impact. A question with an `Answered:` line offers that answer first |
| Accept | Read the spec. Say it is accepted | — |

Questions only someone else can answer: draft them with [`/crav1-ask-open-questions`](from-ask-open-questions.md) and keep them open until the answer comes back.

## What gets written

- `docs/specs/<slug>/spec.md`: only the issue or question you picked, each time.
- The named diagram, ADR, or export, only when that pick says so.
- A branch line on the spec, only after a yes.
- `Blocks: T#` under a question you keep open, when the slice has `tasks.md` and you pick the tasks it blocks in `/crav1-resolve-questions`. Without it, the question blocks the whole slice in [Tasks ready to build](from-tasks-ready-to-build.md).
- A cleared research stale mark, when a resolved question settles the last open point.
- `Used by <slug>` on a note in `docs/notes/` that tighten quotes.

Not written: application code, `plan.md`, `tasks.md`. Nothing is committed.

## After

Commit the accepted spec if you want it in git before planning:

```text
/crav1-finalize-commit
```

Then plan: [From a spec to a plan](from-spec-to-plan.md).

Reference pages: [architecture-reviewer](reference/skills/crav1-architecture-reviewer.md) · [tighten-spec](reference/skills/crav1-tighten-spec.md) · [resolve-questions](reference/skills/crav1-resolve-questions.md) · [feature-branch](reference/skills/crav1-feature-branch.md)
