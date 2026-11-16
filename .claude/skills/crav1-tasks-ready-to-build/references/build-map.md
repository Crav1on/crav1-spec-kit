# Build map (1.140.0)

Read this only when `scripts/build_map.py` cannot run. The script writes the file. Do not invent the map and do not hand-edit it.

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. On Windows that is `python` with `PYTHONUTF8=1`. Elsewhere it is `python3`. Pass `-X utf8`. The Store alias message `Python was not found` means that command was not found. Try the next interpreter.

```text
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs --scope "cc 1.0" --chat
<interpreter> <this skill folder>/scripts/build_map.py docs/specs/<slug>
<interpreter> <this skill folder>/scripts/build_map.py docs/specs/<slug> --recommend T1
```

`--recommend T1` prints that open task's branch and does not write the file. The first line is the branch. `/crav1-build-tasks` and the Build prompt use that line as option 1. Later lines are `source: task line`, `source: build map`, or `source: new`, then `from: <base>` when the task line states one, and `because:` when a merged or deleted branch was skipped. When the task-line branch is only on a remote, or is the head of an open pull request, `because:` says so and a last `checkout: <name>` line follows; the build checks that branch out without the branch card (1.160.0). The branch is checked in the task's code repo: a repo prefix on the mark, a Match `Branch: <repo> <name>` line, or a `Repo:` line in tasks.md names it, and `--code-repo <path>`, the specs repo, or a sibling checkout with that name holds it. `repo: <path>` is printed when that is not the specs repo. When the repo is not found the line is `because: could not check <repo> from here`, never deleted. A task whose own line records a merged pull request stays on that branch in the file. `--recommend` does not print a merged or deleted branch, including for that task.

`--chat` prints the short summary: the path, each wave's parallel count, then that wave's `Overlap:` lines, one per pair, in the same words as the file. Without it the script prints one `Build map:` line per slice. The ready-check list keeps that one line. Both write `docs/specs/<slug>/build-map.md`. `--stdout` prints and does not write. A folder with `spec.md` and no `tasks.md` is `no tasks yet (run /crav1-plan-from-spec)` and gets no file.

The file is committed with the spec. This command does not commit.

## The page line (1.162.0)

Under the `# Build map` heading, one line names the zoomable page: to zoom the diagram, `/crav1-tasks-ready-to-build <slug> open-map`; to share the map as one file, `/crav1-tasks-ready-to-build <slug> export-map`. See [map-page.md](map-page.md).

## What a row shows

Six things, and nothing else, plus one note when the task text names a different branch. No estimates. No file lists. Task ids appear in the Tasks field as `T#` plus the short name (1.133.0). Other fields still drop them. The map is rewritten on every ready check, so those ids match `tasks.md`.

1. **Branch.** The task's branch, in this order: a branch named on the task line, else the name beside that T# in a leading Branches paragraph (for example `chore/merge-main-into-develop` (T4)), else the plan step's `feat/<slug>-<words>` name, else `feat/<slug>-<words>` from the task. On the task line, `(map: <branch>)` wins, then `(branch: <branch>)`, then the Branches-paragraph name, then a `feat/…` or `chore/…` name in the sentence, then `committed later on <branch>`. When the line names more than one branch, the task's own name wins over a done sibling's already-merged branch. A repo prefix on a mark is dropped. `from <base>` after that branch is its base. Words in a generated name come from the step or the task, with the small words dropped. An open task is never placed under a branch git proves merged, or under a done sibling's branch, when the task line or the Branches paragraph names another (1.153.0).
2. **Delivers.** One line, the step sentence, or the short task names when the branch is not the whole step. A task id in that prose is replaced with that task's short name, or removed. A removed id does not leave a dangling `'s`, an empty `()`, a leading comma, or a double space.
3. **Tasks.** One task per entry, separated by `; `, as `T#` plus the short name. Example: `T5 orders-api: require pipeline 6 as build validation`. The short name is the `task: T# <title>` line in the slice's `work-item.md` when that line exists. Otherwise it is the task text up to the first ` (`, `, in `, or sentence end, at most about 80 characters. Marks such as `(host setup)`, `(manual, secret)`, `(verify: …)`, `(spec: …)`, `(after: …)`, and branch prefixes are dropped. The `T#` stays.
4. **Waits for.** The other branches it waits for, or `none`. A dependency that names no task is `a dependency that names no task`. On a branch whose every task is done the field is `Waited for:`, because nothing waits any more (1.162.0).
5. **Question.** Each open question holding the branch, then who has the answer. Who comes from the question's own "Waiting for <who>" phrase, then the latest `Pending:` or `Asked:` line, otherwise `nobody named yet` (1.170.0).
6. **Ready now.** One of `ready`, `waiting on a question`, `waits in order`, `blocked`, `done`, or `held, waits on <branch>`. A wait inside the same branch does not change this. `blocked` is a cycle, a dependency that names no task, a plan risk, or a missing plan. A branch caught in a loop says `blocked, in a loop` (1.154.0). `done` means every task on the branch is ticked. `held, waits on <branch>` means this branch has no question of its own and waits on a branch a question holds. That branch cannot start now.

When the row branch differs from a branch named in the task text (`(branch: …)`, `committed later on <branch>`, or another `feat/…` name), the row adds one line: `Task text names feat/orders-cicd; built on feat/orders-retry`. When the row is the branch named on the task line and the plan step's name is the other one, the line points the other way: `Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts`. The row's own name is not listed. The note does not change Ready now or the wave.

Wave 1 is the branches that do not wait for another branch. Wave 2 is what opens after those, and so on. A branch held only by a question can still sit in wave 1; Ready now says it is waiting. The wave heading is always `N branch, M can start now` or `N branches, M can start now`, including one branch (`Wave 1: 1 branch, 1 can start now`) and a wave where every branch can start (`Wave 1: 3 branches, 3 can start now`). A question hold, a claimed branch, a branch held because it waits on one, or a branch that waits in order, lowers M (`Wave 1: 3 branches, 2 can start now`, or `Wave 2: 1 branch, 0 can start now`). Only a branch that is ready under the same rule as the ready check counts as able to start. A done branch does not. When the wave has done tasks, the heading adds them after that count: `1 branch, 1 can start now, 2 done`. That count is also the first part of each wave line in the `build-map` summary. Each `Overlap:` line for that wave follows it, one pair per line. Blocked branches are listed under `## Blocked`, not in a wave. A branch always sits in a later wave than every branch it waits for, unless both are in the same loop. Branches in one loop share a wave number and are listed under `## Blocked`, in an `In a loop` subgraph. A branch that only waits for a loop keeps its own wave and Ready now (1.154.0).

The flowchart is `flowchart LR`. Each wave is one subgraph, with `direction TB` inside, so the branches in a wave sit side by side across the page and one above another inside the wave. An arrow means the later branch waits for the earlier one.

Under a wave, an `Overlap:` line names a pair of branches in that wave that share a requirement or a path. A requirement is the text of `(spec: …)` on a task, compared with case folded and extra space collapsed. A path is a backtick span in the task line that contains `/` or a file extension, compared exactly as written. The plan's file list is not used. The note does not block, and it does not change Ready now or which wave a branch is in. A branch row still has the six fields above, and still no file list.

## Grouping

Numbered items under `## Approach` are the plan steps. A step owns the tasks whose ids are written in that step. `(step: 1)` on a task line is the same link, and it wins when the step text names a different step. One branch per step.

`(map: feat/cancel-refund)` puts that task on the named branch. `(branch: feat/orders-retry)` does the same when no `(map:)` is set. A `feat/…` name in the sentence, or `committed later on feat/orders-cicd`, does the same when neither mark is set. Tasks that resolve to the same name share it. Leave every branch off the task line and the task stays on its plan step. Two tasks on one step can name different branches. The plan step's name is only the fallback.

When the plan has no steps, the file says `The plan has no steps, so this map uses one branch per task.` When the steps name no task, it says `The plan steps do not name tasks, so this map uses one branch per task.` A task the steps do not name gets its own branch, and the file says so. A cycle, or an `(after:)` that names no task, is listed under Blocked. Branches that wait for each other get one `Loop:` line near the top of the file, naming the branches and the task line behind each direction of the wait (1.154.0). The fix offer follows on its own lines, as [loop-fix.md](loop-fix.md) says (1.161.0).

A ticked task stays in its wave row (1.132.0). The Tasks field strikes the id and the short name through and marks it done, with its pull request link, or the recorded branch, or a commit from `verify.md` when there is no pull request: `~~T5 short name~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))`. The link comes from a Match `Branch:` line `(PR n)` and a repo URL in the spec. No network read. A wave whose every task is done is wrapped in `<details><summary>Wave N done (K tasks)</summary>`. The heading, the rows, and the fields stay in the file. Nothing is deleted. When there are no tasks, the file says `Nothing left to build.`

## Ready check (1.133.0)

Read this when the readiness script cannot run. Do not invent branches.

Group the tasks that can start, and the held tasks, by the row `scripts/build_map.py docs/specs/<slug> --recommend T#` prints. That is the same branch as the map. Order the branches by wave, then by the order of the rows in the file. One ready branch is still one group.

Print one line per branch. A task is `T#` plus its short name, the same words as the Tasks field.

```text
Run next:

**feat/orders-api-record**
Record each decision with who made it and when.
2 open tasks:
- T2 Record the decision
- T5 Store the card

Run the whole branch:
`/crav1-build-walk feat/orders-api-record`
Run only T2, the first task:
`/crav1-build-walk T2`

---

**feat/orders-api-export**
1 open task:
- T6 Email the receipt

Run T6:
`/crav1-build-walk T6`

Held:
- `feat/orders-api-currency` (wave 1):
  - T3 Choose the currency — open question "Which currency for refunds?" Waiting for the partner.
- `feat/orders-api-archive` (wave 2):
  - T4 Archive the receipt — held, waits on T3
```

Since 1.164.0 each ready branch is one block: the branch in bold, a description of what it does from the plan step that owns it (since 1.166.0 never left out while there is a plan step or a usable task name), `<n> open tasks:` with one task per line, then `Run the whole branch:` with `/crav1-build-walk <slug> <branch>` and `Run only T#, the first task:` with `/crav1-build-walk <slug> T#`. Each label is on its own line and each command is alone in its code span on the next line. A branch with one open task says `1 open task:`, then `Run T#:` and the one command. Since 1.165.0 a `---` line, with a blank line on each side, stands between two branch blocks so they never run together in a Markdown viewer. The open tasks are listed in the order the walk runs them. A listed task that cannot start yet says why on its line, for example `- T8 Take in develop (waits on T5)`, and when the first listed task cannot start the label is `Run only T#, the first task that can start:`. The plain sentence is used only when the plan step's first sentence is clean: it ends with a full stop, has no colon list, and does not open with a person (`Person A builds ...`). Otherwise the step's heading in plain words is used, or the line is left out. Since 1.166.0 every branch block has a description line between the bold branch and `<n> open tasks:`. In order: up to three clean sentences from the plan step (each ends with a full stop, has no colon list, no person leading it and no file or path), about 300 characters at most and cut only at a sentence end, never mid-sentence; else the plan note trimmed to its opening clause, the words before the first `:` or ` — `, with a person lead such as `Person A builds PR 73:` dropped, for example `The orders CI/CD branch, cut from develop after billing-ops.`; else the step's heading in plain words; else one sentence from the open task names, a shared prefix once, for example `Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy README.`, about 160 characters. The line is left out only when the branch has no plan step and no usable task name, and a person's name never shows. A held question that ends with `:` or only points to a note, such as `The note docs/notes/x.md, in Open questions, question 5, says:`, shows the quoted question that follows: the `>` blockquote under the bullet, else the text in quotes after the colon, else the first sentence ending in `?`. A long line, a sentence or a held question, is cut at a clause end or a word, never on a dangling word such as `the`, and a held question that opens with a heading such as `Client certificate.` shows the question itself. The slug rule is unchanged. After Held, a `Branch runs:` block lists each `- Branch run:` status line in `walk-progress.md` that is not `merged`, for example `- feat/orders-api-record: running, T2 done, next T5 (log: build-progress/feat--orders-api-record.md)`.

A held task names its open question and who has the answer, or `held, waits on T#`. Each held task is its own line under its branch, and the question is short: its first sentence, no markdown markers, about 100 characters at most (1.164.0). The Run next block is first and is the only place the walk command appears, one entry per branch that has a task that can start, and only when the result is `ready` or `ready-partial`. The bottom keeps Waiting lines that do not repeat a Held entry. Since 1.176.0 the one-line `/crav1-build-tasks` alternative is left out of the ready check's ending; `/crav1-help status` names it instead. Never write a `Next:` line after the Waiting or Held lines (1.153.0). Do not flatten the branches into one list.

A held line shows the wave, or `in a loop` for a branch caught in a loop. It never shows `(blocked)` (1.154.0). When branches wait for each other, print one Loop line per loop before the Waiting lines, naming the branches and the task line behind each direction of the wait: `Loop: feat/orders-api-x and feat/orders-api-y wait for each other: T14 on feat/orders-api-x waits for T13 on feat/orders-api-y, and T13 on feat/orders-api-y waits for T12 on feat/orders-api-x.` Then print the fix lines under it, `Recommended fix (say `fix-loop`): …` first ([loop-fix.md](loop-fix.md), 1.161.0).
