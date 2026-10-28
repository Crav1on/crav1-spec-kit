# Ask the kit for help

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want to know what to run next, in what order, or what one command does. `/crav1-help` answers from the kit's own docs for the version you have installed, and every answer names the file it came from.

This is cross-cutting. It is not its own lane. It writes nothing and runs no other command. It is not [`/crav1-explain-existing-system`](from-explain-existing-system.md), which reads your product's `docs/system/`.

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
| `/crav1-help work item homes`, `marks.md`, `stale marks` | The concept, from the [glossary](concepts/glossary.md) and the concept pages |
| `/crav1-help list`, `/crav1-help list build` | Every command grouped by lane and phase, or one lane, from the [skills reference](reference/skills.md) and [guild routing](guild-routing.md) |
| `/crav1-help status <slug>`, `/crav1-help where am I` | Where one slice is: task counts (ready, blocked, needs verify, done) with the same rules as [`/crav1-tasks-ready-to-build`](from-tasks-ready-to-build.md), the route step it is on, and the next step |
| `/crav1-help todo`, `todo next`, `todo top 8`, then an optional scope such as `pr71`, `orders-retry`, `feat/orders-retry`, or `Dana` | What to do next, ranked from the records (1.75.0): questions that block ready tasks, answered questions not resolved, pending drafts older than 3 days, asks older than 7 days, dates in Constraints, stale research, decisions, ready tasks, parked specs. Each line gives the spec, the reason with its age, and the next command. A **Yours first** group comes from `git config user.name` or `todo for <name>`. A pull request is found offline from its PR note or the local git log; online only after you pick to |
| A word in the project's own glossary | Help answers about kit words; a project word such as `bcas` is `/crav1-glossary bcas` (1.101.0), which the usage guide now lists. See [The glossary](from-glossary.md) |
| `/crav1-help add-to-spec` | Its choice words, plus the line `After a PR: all` (1.76.0): `pr71` alone is a code change, `pr71 all` adds the description and comments |
| `/crav1-help ado-sync` | For a merged skill, also its choice words, such as `suggest features` / `push features` / `push tasks` / `pull tasks` / `pull spec changes` ([choice words](guild-routing.md#choice-words-for-bots-and-scripted-runs)) |
| `/crav1-help renamed`, or an old name | The old-to-new names, the choice word to use, and that the old names were removed in 1.58.0 |
| `/crav1-help compare build-tasks build-features` | Two commands side by side: lane, purpose, reads, writes, next steps, and when to pick which |
| `/crav1-help compare explain-this-code explain-existing-system` | explain-this-code reads one piece of code (a file, function, selection, or PR diff); explain-existing-system reads the system notes in `docs/system/`. Both are read-only |
| `/crav1-help whats new`, `/crav1-help whats new since 1.50` | The changelog for your installed version, or every release since the one you name |
| Any other question about the kit | The answer from the docs, or "the kit doesn't say" when they do not cover it |

Called with nothing, it shows this list with examples. Every answer ends with a line such as `Source: reference/workflow.md#new-info`.

A skill, route, concept or free-form answer is at most 5 lines (1.95.0). Ask it to do something, such as "review my branch", and you get one line, for example `Run /crav1-review-pr branch: it diffs your branch against its base and checks it against the spec.` Help never runs the command for you.

## Routes and file state

The order comes from one file, [workflow.yaml](reference/workflow.yaml), shown as [Workflow routes](reference/workflow.md). It has five routes: New slice, New information on an existing slice, Bug, Outside pull request, and Azure Boards (ADO) sync.

For a route question, the command reads the slice's files and does not change them:

- Open questions in `spec.md`.
- Whether `plan.md` exists.
- Ticked and unticked tasks in `tasks.md`.
- A failure in `verify.md`.
- Feature and task ids in `work-item.md`.

It keeps every step of the route in the answer and gives a reason for each one it marks skipped. It names the first step to run and stops. When the route reaches building, it also says that [`/crav1-tasks-ready-to-build`](from-tasks-ready-to-build.md) can run any time to list which tasks are ready and why the others are blocked.

Example: after a meeting changed a spec that has a plan and unbuilt tasks, the New information route gives tighten-spec, resolve-open-questions, plan-from-spec, ado-sync (only when the Feature itself changed), ado-sync, build-tasks, and verify-build-against-spec.

## When you push back

Ask "don't we need tighten-spec first?" and the command re-reads the file it cited. It keeps the answer when the file says so, corrects it when the file says otherwise, and says "the kit doesn't say" when the file does not settle it. It does not change an answer to agree with you.

Other agents follow the same rule. The always-on rule (`crav1.mdc` in Cursor, `CLAUDE.md` in Claude Code) tells them to call `/crav1-help` before they suggest more than one next step, or when you question an order, and to quote its answer.

## Parked and retired specs

Help skips specs in `docs/specs/retired/` and `Moved:` pointers. Parked specs are listed under **Parked** with date, reason, and how many notes wait for each, for example `orders-export (parked 2026-10-16, waiting on partner), 2 notes waiting`. It names `/crav1-retire-spec un-park` to pick one up ([retire spec](from-retire-spec.md)).

## Where the answers come from

The skill names its docs folder for each host and reads it directly (1.96.1). It never looks for `docs/reference/` at the root of your repo and never searches for the docs:

- In the kit repo, its own `docs/`.
- Cursor: `.cursor/skills/crav1/crav1-docs/` in the drop-in, `skills/crav1-docs/` in the plugin folder.
- Claude Code: `.claude/skills/crav1-docs/`, or `~/.claude/skills/crav1-docs/` in user scope.
- When only the skill folders were copied and `crav1-docs/` is missing, the command answers from the skill files only and says so.

Each release bundles its own docs and `CHANGELOG.md`, so the answer fits the version you have. The answer starts with the answer, not with a line about which docs it used; the `Source:` line at the end says where it came from.

It never fetches an answer from GitHub. When the machine is online, it reads the kit's tag names once and adds one line when a newer version is tagged.

## What does not get written

Nothing. No file, no commit, no command run. `todo` stores nothing either.

## After

Run the step it named, for example:

```text
/crav1-tighten-spec
@docs/specs/<slug>/spec.md
```

Reference page: [help](reference/skills/crav1-help.md) · Routes: [Workflow routes](reference/workflow.md)
