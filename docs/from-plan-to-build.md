# Build tasks

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when `plan.md` and `tasks.md` are accepted. Build one task `T#` at a time, in this chat or in an isolated worker. A kit script this command runs uses the interpreter in [Running a kit script](reference/running-scripts.md). Prefer a fresh chat so the build is not mixed with the exploration that came before. If the agent drifts, revert, tighten the plan, and build again instead of patching in follow-ups.

| You want | Command |
| --- | --- |
| One task, here, and watch the diff | `/crav1-build-tasks T1` |
| One task, start to commit, in an isolated worker | `/crav1-build-tasks T1` |
| Several tasks on one spec | `/crav1-build-tasks T1-T3` (or all unchecked) |
| Several ready specs, one after another | `/crav1-build-features <slug-a> <slug-b>` (or all ready) |

## First prompt

```text
/crav1-build-tasks T1
@docs/specs/<slug>/
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Branch | Pick the branch when asked | Each command calls `/crav1-create-feature-branch` before code. On a base branch there is no Stay (see [Never on a base branch](#never-on-a-base-branch-1990)). `/crav1-build-features` makes `feat/<slug>` from the into branch per slug without asking again |
| Linter gate | When `## Linter` says none and you have not chosen to go on, decide first | Stops with no code until you choose |
| Approvals (worker commands) | Answer the one pause: `continue` or `click` | `/crav1-build-tasks`, and `/crav1-build-features` pause once for the host's tool-approval setting, not per task or per slug. When the run ends they say how to restore it |
| Commit style (worker commands) | Pick a commit style once when asked | Writes the commit-style rule once when it is missing. Workers then commit without asking |
| Build | Watch the diff | `/crav1-build-tasks` writes the code and the checks the row names, runs that verify step, and marks the row `[x]` only when it passes. A worker (`crav1-build-task-agent`) does the same in isolation: implement, commit, verify, and an optional fix |
| Batch stop | Answer the worker | `/crav1-build-tasks` stops the batch when a worker needs you. `/crav1-build-features` runs specs one after another, never in parallel, and with one ready slug points at `/crav1-build-tasks` |
| Picture | Say yes or no | `/crav1-build-features` asks once whether to run `/crav1-refresh-system-notes` when a slice is marked done or retired, and does not run it. The other build commands do not ask |

Before the tests run, the kit checks their local dependencies (Azurite, a database container, an emulator) and asks start, skip, or stop for one that is down. A task whose tests skipped for a missing dependency is not ticked unless you chose skip. See [Local test dependencies](from-verify.md#local-test-dependencies).

## What gets written

- The code and checks for each task, and `[x]` on that row in `tasks.md` after its verify passes.
- Worker commands also write `verify.md`, `fix-log.md` when a fix runs, and the commits, plus the commit-style rule once.
- `/crav1-build-features`: a `feat/<slug>` checkout per slug.

Not written: `spec.md`, other tasks. No push, no pull request.

## Tasks on several branches (1.64.0)

A task line can name its branch: `- [ ] T3: … (after: T1) (branch: feat/orders-retry)`.

- `/crav1-build-tasks` on one task offers **feat/orders-retry (Recommended)** first in the `/crav1-create-feature-branch` Build prompt, then `feat/<slug>`, Other name and Stop (Stay only off a base branch). A task naming a base branch is blocked. A branch that exists nowhere is never created from default without asking.
- A range or all-tasks run switches to each task's branch on a clean tree; starting the run is the consent. A missing branch blocks that task.
- `/crav1-build-features` does the same per slug. A slug whose tasks are done but whose branches aren't all merged shows `done (2 branches not merged)`.
- The next-step line after a build names `/crav1-open-pr` to push and open the PR. When the branch already has one (its Match line ends in `(PR 77)`), it says `/crav1-open-pr` to push to PR 77 and update its description or comment instead (1.114.0).
- `/crav1-tasks-ready-to-build` shows the branch beside each ready task, and one Branches line. It also rewrites `docs/specs/<slug>/build-map.md` (1.128.0).

## Never on a base branch (1.99.0)

Implementation code is never written or committed on a base branch: `main`, `master`, `develop`, the repo's `Merges into` branch, or any `release/*`. On a work branch (`feat/`, `feature/`, `bug/`, `bugfix/`, `fix/`, `hotfix/`, or one a spec names) the build goes ahead. On a base branch, `/crav1-build-tasks` and `/crav1-fix-build-gaps` ask once:

- **Create feat/orders-retry from develop (Recommended)**: forks from the into branch, so a repo that merges into `develop` forks from `develop`, not `main`. Uncommitted changes come along when you are on that branch.
- **Use an existing branch**: lists the repo's other branches, the spec's own first. A pick the spec doesn't list is added to its Match `Branch:` list with `(into develop)`.
- A typed branch name on that same card, and **Stop**. There is no second card to collect the name, and there is no Stay.

On a branch that is neither (`chore/x`, a detached checkout) the same prompt offers **Stay** instead of the typed name. A release fix goes on `fix/<slug>` marked `(into release/x)`. A headless run stops with one line unless it has the choice word `new branch`. `/crav1-build-features` forks `feat/<slug>` from the into branch without asking. The worker returns `blocked` if it ever finds itself on a base branch. Spec and doc writes, and the specs repo itself, are exempt.

## A spec branch with task sub-branches (1.68.0)

Some teams give a spec its own long-lived branch and each task a short sub-branch that merges into it. Made-up example: `feat/orders-capacity` is the spec branch; `feat/orders-capacity-t3` and `feat/orders-capacity-t4` are cut from it.

- **Markers.** The Match lines read `- Branch: feat/orders-capacity (spec branch)` and `- Branch: feat/orders-capacity-t3 (into feat/orders-capacity)`, one per branch (1.86.0). When a read finds a branch that split off another spec branch, `/crav1-add-to-spec` code change, `/crav1-tighten-spec` or `/crav1-open-pr` asks once: `feat/orders-capacity-t3 split off feat/orders-capacity. Does it merge into feat/orders-capacity?` A yes writes the markers. A no, or a headless run, writes nothing and treats it as stacked.
- **Tasks.** `/crav1-plan-from-spec` may name a sub-branch: `(branch: feat/orders-capacity-t3)`. When it doesn't exist yet, the Build prompt offers **Create feat/orders-capacity-t3 from feat/orders-capacity (Recommended)** and writes the `(into …)` marker after the yes.
- **No double import.** Reading the spec branch after its sub-branches imports only the commits made directly on it. A squash-merged sub-branch counts as covered through the host PR, or is listed as `may already be in <note>`.
- **Pull requests.** A sub-branch's PR goes into the spec branch; the spec branch's PR goes into the repo's `Merges into` branch, else the default branch.
- **Done.** Status shows `Sub-branches: 1 of 2 merged into feat/orders-capacity.` The spec is done when the spec branch has reached the base branch. A sub-branch that never merged is reported as `left behind: feat/orders-capacity-t4 (not in feat/orders-capacity)` and doesn't block done.
- **Reverts.** A merged branch whose change was later reverted on the base shows `feat/orders-retry: merged, reverted on develop (<sha>)`. It is report only and doesn't change done.

## The branch the build offers (1.129.0)

The branch question is its own card, before the permissions question. Option 1 is the branch the build map already uses for that task (`scripts/build_map.py --recommend T1`). On that branch already, there is no prompt. A typed name on the card is the answer. If you pick a different branch, the task line gains `(map: <that branch>)` in the specs repo. That write is not a commit. A `(host setup)` option says the script will live on the recommended branch, and says when the task text names a branch that is cut later.

A missing permissions answer, or a branch name in the permissions slot, is asked again. The run does not guess `click`.

## A yes that is not on record (1.129.0)

When the live change needs someone's yes (host setup, or another approval), and that yes is not already on record, the worker returns `needs_yes`. The task stays unticked. That is waiting, not blocked.

```text
Waiting: the partner's yes to turn off pipelines 7 and 24.
Next: /crav1-build-tasks T1, because that yes is not on record yet.
```

## Host setup tasks (1.115.0)

A task marked `(host setup)` is a host setting, not a file. The worker writes the checked-in script and its manual steps, shows them, and runs the script only after your yes; it ticks the task only when the script's `check` part reads the setting back `ok`. Without that yes the task stays unticked and the run waits, as above. The rules are the same as [Set up a host setting](from-host-setup.md) (`/crav1-host-setup`).

When the build writes a new `.sh` file, the repo has no `*.sh` rule with `eol=lf`, and `core.autocrlf` is true or the host is Windows, the run offers one line in `.gitattributes`: `*.sh text eol=lf`. It does not add the line unless you accept.

## After

Prove the slice against the spec: [Verify and fix](from-verify.md). Then [From commit to merge](from-commit.md).

Reference pages: [build-tasks](reference/skills/crav1-build-tasks.md) · [build-tasks](reference/skills/crav1-build-tasks.md) · [build-tasks](reference/skills/crav1-build-tasks.md) · [build-features](reference/skills/crav1-build-features.md) · [subagents](reference/skills.md#subagents)

The run ends as [How a run ends](reference/run-ending.md) says: one `Next:` line, `Waiting:` when a step is blocked or waits on a person's yes, and `Uncommitted:` when files changed and are not committed.
