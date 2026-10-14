# Ask the kit for help

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want to know what to run next, in what order, or what one command does. `/crav1-help` answers from the kit's own docs for the version you have installed, and every answer names the file it came from.

This is cross-cutting. It is not its own lane. It writes nothing and runs no other command. It is not [`/crav1-explain`](from-explain.md), which reads your product's `docs/system/`.

## First prompt

New chat, or the chat you are working in:

```text
/crav1-help
I have new information from a meeting and tasks that are not built. What do I run, in order?
```

## What you can ask

| You type | You get |
| --- | --- |
| `/crav1-help` | A short usage guide, example questions, and the list of routes |
| `/crav1-help tighten-spec` | What that command does, when to use it, what it reads and writes, and the steps before and after it |
| `/crav1-help next`, or a situation | The route for that situation, in order, with each step marked done, next, skipped, or to do |
| Any other question about the kit | The answer from the docs, or "the kit doesn't say" when they do not cover it |

Every answer ends with a line such as `Source: docs/reference/workflow.md#new-info`.

## Routes and file state

The order comes from one file, [workflow.yaml](reference/workflow.yaml), shown as [Workflow routes](reference/workflow.md). It has five routes: New slice, New information on an existing slice, Bug, Outside pull request, and Azure Boards (ADO) sync.

For a route question, the command reads the slice's files and does not change them:

- Open questions in `spec.md`.
- Whether `plan.md` exists.
- Ticked and unticked tasks in `tasks.md`.
- A failure in `verify.md`.
- Feature and task ids in `work-item.md`.

It keeps every step of the route in the answer and gives a reason for each one it marks skipped. It names the first step to run and stops. When the route reaches building, it also says that [`/crav1-tasks-ready-to-build`](from-tasks-ready-to-build.md) can run any time to list which tasks are ready and why the others are blocked.

Example: after a meeting changed a spec that has a plan and unbuilt tasks, the New information route gives tighten-spec, resolve-questions, plan-from-spec, specs-to-ado (only when the Feature itself changed), tasks-to-ado, complete-tasks, and verify-spec.

## When you push back

Ask "don't we need tighten-spec first?" and the command re-reads the file it cited. It keeps the answer when the file says so, corrects it when the file says otherwise, and says "the kit doesn't say" when the file does not settle it. It does not change an answer to agree with you.

Other agents follow the same rule. The always-on rule (`crav1.mdc` in Cursor, `CLAUDE.md` in Claude Code) tells them to call `/crav1-help` before they suggest more than one next step, or when you question an order, and to quote its answer.

## Where the answers come from

- In the kit repo, its own `docs/`.
- In every install, the `crav1-docs/` folder next to the skills: `skills/crav1-docs/` in the Cursor plugin, `.cursor/skills/crav1/crav1-docs/` in the Cursor drop-in, and `.claude/skills/crav1-docs/` (or `~/.claude/skills/crav1-docs/`) in Claude Code. Each release bundles its own docs, so the answer fits the version you have.
- When only the skill folders were copied and `crav1-docs/` is missing, the command answers from the skill files only and says so.

It never fetches an answer from GitHub. When the machine is online, it reads the kit's tag names once and adds one line when a newer version is tagged.

## What does not get written

Nothing. No file, no commit, no command run.

## After

Run the step it named, for example:

```text
/crav1-tighten-spec
@docs/specs/<slug>/spec.md
```

Reference page: [help](reference/skills/crav1-help.md) · Routes: [Workflow routes](reference/workflow.md)
