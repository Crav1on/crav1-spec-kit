# From a draft spec to an accepted spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a starter has written `docs/specs/<slug>/spec.md` and it is not yet good enough to plan from. A kit script this command runs uses the interpreter in [Running a kit script](reference/running-scripts.md). The goal is a spec you accept: acceptance lines a stranger could mark yes or no, non-goals, and only the open questions you choose to keep. Every step here edits the spec one issue at a time, after you pick. None of them writes code or a plan.

On a brownfield repo, put the work on a branch first. `/crav1-create-feature-branch` offers `feat/<slug>` (spec and build on one branch) or `spec/<slug>` (specify only; build later on `feat/<slug>` after this spec is on the default branch). Starters already ask this; run it on its own when you skipped that prompt. When the same command is the Build prompt for a task, option 1 is the first line of `scripts/build_map.py docs/specs/<slug> --recommend T1`, and a typed name on that card is the answer (1.129.0). Since 1.140.0 a branch named on the task line wins over the plan step, the card lists that option first, and the description says where the name came from (the task line, the build map, or new). A merged or deleted branch is not offered. A different pick is written back as `(map:)` on the task and is not committed.

## First prompt

New chat. Strong reasoning model. Not the host plan UI.

When the design has real hunches (diagrams, ADRs, stack choices), start with a critique:

```text
/crav1-review-architecture
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
| Branch (brownfield, optional) | `/crav1-create-feature-branch <slug>`, pick `feat/<slug>` or `spec/<slug>`, or type a branch name on that card | Reads the current branch, the default branch, and whether the tree is dirty. A typed name is the card's free-text answer, hint `Type a branch name` (1.130.0). A dirty tree does not check out. No push, no pull request |
| Critique (optional) | `/crav1-review-architecture` | Starts the `crav1-review-architecture-agent` subagent. Returns numbered issues `I#` in chat. Writes nothing. Names `/crav1-review-security` as an optional next step and does not run it |
| Independent spec review (optional) | Ask for a spec review | The `crav1-spec-reviewer-agent` subagent critiques product and spec. Writes nothing |
| Tighten | `/crav1-tighten-spec`, then one card: `yes (Recommended)` for every recommendation, or type changes on that card, for example `I1 A, I3 C` | Lists issues `I1`, `I2`, … (reviewer findings in this chat first). Eight or fewer: one card, `yes (Recommended)`, and the card's free-text answer for changes. Since 1.145.0 that reply prints a findings table immediately before the card. The card names each item, for example `I1 acceptance is not yes/no: A make-testable`. It does not say `table above` unless that table is in the reply. The card is not asked without the table. An item you do not mention keeps its recommendation. There is no Edits choice. More than 8: one line with the counts (issues to fix, open questions, small wording), then one issue or a small group. One by one still works. A batch for that group prints the same table. An issue that only settles an open question is passed on in one line, with no menu. Patches only what you picked. `suggest` recommends and does not patch |
| Code first (partial slices) | Confirm the repo and branch when asked | When the slice is partial or `## In the code` names paths, reads that committed code before wording issues. A disagreement with the code is called out, not silently rewritten |
| Open questions | `/crav1-resolve-open-questions`, then one card: `yes (Recommended)`, or type changes on that card, for example `Q1 A, Q3 keep` | Every `Q#` shown together (`Q#` is a display number; the answer is matched to the question by its words, 1.84.0). Since 1.145.0 the reply prints a findings table immediately before the card. The card names each question and the recommended choice. It does not say `table above` unless that table is in the reply. The card is not asked without the table. `yes (Recommended)` takes the recommendations. Typed changes go on that card's free-text answer. An item you do not mention keeps its recommendation. There is no Edits choice (1.130.0). An answer becomes spec text, a constraint, a non-goal, or an ADR, with its impact. A question with an `Answered:` line offers that answer first. Name a branch or `pr71` to pick the spec (1.75.0). Add `detailed` for what each question blocks, who can answer, when it was asked, and its sources. Words or `orders Q3` open one question (1.77.0), and the run stops after that answer without asking another (1.90.5). `apply <file>` reads a filled playbook and, on the same yes, copies it to `docs/playbooks/<topic>.md` (1.120.0). A kept item opens the add-to-spec fact rules and does not start that command (1.134.0). See [Opening another kit skill](reference/open-skill-file.md) |
| Accept | Read the spec. Say it is accepted | — |

Questions only someone else can answer: draft them with [`/crav1-show-or-ask-open-questions`](from-show-or-ask-open-questions.md) and keep them open until the answer comes back.

## What gets written

- `docs/specs/<slug>/spec.md`: only the issue or question you picked, each time.
- The named diagram, ADR, or export, only when that pick says so.
- A branch line on the spec, only after a yes.
- `Blocks: T#` under a question you keep open, when the slice has `tasks.md` and you pick the tasks it blocks in `/crav1-resolve-open-questions`. **None** writes `Blocks: none`. **The whole slice** writes `Blocks: whole slice`. That hold stays after resolve-open-questions is recorded. A missing line holds a `T#` named in the question text, and holds the slice in [Tasks ready to build](from-tasks-ready-to-build.md) only when no task is named and that step has never been recorded. `/crav1-resolve-open-questions` does not walk `## Approval needed` and does not remove an `Approved:` line (1.141.0).
- A cleared research stale mark, when a resolved question settles the last open point.
- The slug in `used_by` on a note in `docs/notes/YYYY-MM/` that tighten quotes (generated index rebuilt).
- On `apply <file>`, `docs/playbooks/<topic>.md` for a filled playbook, and a `Playbook:` line on each spec that apply changed. The name is shown once. A draft is not copied. A hand-edit of the committed file is shown before overwrite.

Not written: application code, `plan.md`, `tasks.md`. Nothing is git-committed.

## After

Commit the accepted spec if you want it in git before planning:

```text
/crav1-finalize-commit
```

Then plan: [From a spec to a plan](from-spec-to-plan.md).

Reference pages: [review-architecture](reference/skills/crav1-review-architecture.md) · [tighten-spec](reference/skills/crav1-tighten-spec.md) · [resolve-open-questions](reference/skills/crav1-resolve-open-questions.md) · [create-feature-branch](reference/skills/crav1-create-feature-branch.md)

The run ends as [How a run ends](reference/run-ending.md) says: one `Next:` line, `Waiting:` only when a step is blocked, and `Uncommitted:` when files changed and are not committed.
