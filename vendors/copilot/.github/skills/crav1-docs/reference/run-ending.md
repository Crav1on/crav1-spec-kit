# How a run ends

Every skill ends a run in this shape (1.122.0). The skill still chooses which step is now, by the rules it already has. This page is only the shape.

A skill names the next step. It does not run it, unless that skill already runs the step today. The tighten-and-plan walk runs the steps inside the walk. Every other skill only names the step.

A script that prints Run next accepts `--vendor` (1.201.0). With no flag, and for cursor, claude, and copilot, the command prefix stays `/`. `--vendor codex` prints `$crav1-` in place of `/crav1-`. A path such as `.cursor/skills/crav1/crav1-help` is left as written.

## The shared walk ending (1.156.0)

The ready check (`/crav1-tasks-ready-to-build`), the tighten-and-plan ready check, and `/crav1-build-walk` build their ending with one shared script, skill `crav1-tasks-ready-to-build` `scripts/walk_ending.py --json <state> --vendor copilot` (each of the three skills ships a copy of that `walk_ending` script). The skill gives that text once as its answer, as-is. It never pastes the raw tool output and then repeats the reply, never adds more than one short lead sentence before it, never adds, drops, or rewrites a line, and never adds a `Next:` line of its own. For the same ready branches, the three print the same Run next entries. The order is:

Before a ready-check or walk ending, the reply has at most one short lead sentence of recap, for example `The plan review is done.`, then the ending, `Run next:` first. No longer recap and no list before it (1.164.0).

1. `Run next:` first. Since 1.164.0 each ready branch is one block: the branch in bold, one plain sentence of what it does from the plan step that owns it (left out when there is none), `<n> open tasks:` with one task per line, then `Run the whole branch:` with `/crav1-build-walk <slug> <branch>` and `Run only T#, the first task:` with `/crav1-build-walk <slug> T#`. Each label is on its own line and each command is alone in its code span on the next line. A branch with one open task says `1 open task:`, then `Run T#:` and the one command. For example:

   ```text
   **feat/orders-api-record**
   Record each decision with who made it and when.
   2 open tasks:
   - T2 Record the decision
   - T5 Store the card

   Run the whole branch:
   `/crav1-build-walk orders-api feat/orders-api-record`
   Run only T2, the first task:
   `/crav1-build-walk orders-api T2`

   ---

   **feat/orders-api-fixes**
   Receipt API fixes.
   2 open tasks:
   - T43 Read the receipt body
   - T8 Take in develop (waits on T5)

   Run the whole branch:
   `/crav1-build-walk orders-api feat/orders-api-fixes`
   Run only T43, the first task:
   `/crav1-build-walk orders-api T43`
   ```

   Since 1.165.0 a `---` line, with a blank line on each side, stands between two branch blocks so they never run together in a Markdown viewer. The open tasks are listed in the order the walk runs them. A listed task that cannot start yet says why on its line, for example `- T8 Take in develop (waits on T5)`, and when the first listed task cannot start the label is `Run only T#, the first task that can start:`. The plain sentence is used only when the plan step's first sentence is clean: it ends with a full stop, has no colon list, and does not open with a person (`Person A builds ...`). Otherwise the step's heading in plain words is used, or the line is left out. A long line, a sentence or a held question, is cut at a clause end or a word, never on a dangling word such as `the`, and a held question that opens with a heading such as `Client certificate.` shows the question itself.

   Since 1.166.0 every branch block has a description line between the bold branch and `<n> open tasks:`. In order: up to three clean sentences from the plan step (each ends with a full stop, has no colon list, no person leading it and no file or path), about 300 characters at most and cut only at a sentence end, never mid-sentence; else the plan note trimmed to its opening clause, the words before the first `:` or ` — `, with a person lead such as `Person A builds PR 73:` dropped, for example `The orders CI/CD branch, cut from develop after billing-ops.`; else the step's heading in plain words; else one sentence from the open task names, a shared prefix once, for example `Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy README.`, about 160 characters. The line is left out only when the branch has no plan step and no usable task name, and a person's name never shows. A held question that ends with `:` or only points to a note, such as `The note docs/notes/x.md, in Open questions, question 5, says:`, shows the quoted question that follows: the `>` blockquote under the bullet, else the text in quotes after the colon, else the first sentence ending in `?`.

   Since 1.167.0 what you can fix now with one command leads Run next as a `**Catch up first**` block, before the first branch block and in the same layout: the bold heading, one or two plain sentences of what is behind (since 1.175.0 the push has no sentence; its label says how far ahead), then each command alone in its code span under its label line, and the same `---` line before the first branch block. It covers verify.md behind tasks.md, a verify.md row for a T# that is not in tasks.md, and a specs repo ahead of origin. `/crav1-verify-build-against-spec` both checks the behind tasks and drops a row for a T# that tasks.md does not have, so those two share one label and one command. The push is `git push` (the specs repo is never behind here; a copy behind origin stops the check first). The block is left out when nothing is behind, and those items are no longer `Waiting:` lines. For example:

   ```text
   **Catch up first**
   verify.md is behind for T4 and T7, and it has a row for T44, which is not in tasks.md.

   Check T4 and T7 against the spec and remove the T44 row:
   `/crav1-verify-build-against-spec orders-api`
   Push the specs repo, which is 2 commits ahead of origin:
   `git push`

   ---

   **feat/orders-cicd**
   The orders CI/CD branch, cut from develop after billing-ops.
   ...
   ```

   Only the orphan row gives `Remove the T44 row (it is in verify.md but not in tasks.md):`, and only the behind tasks give `Check T4 and T7 against the spec:`. A not-ready ending puts the same block first, before its one next step.
2. `Held:` lines, then `Branch runs:` status lines.
3. For a branch run: `Built on <branch>:` (one line per task, with its commit and tests), then `Left:`.
   Print the block as the script wrote it (1.196.0). Never retype it: the heading stays bold, `**Catch up first**`, each label is on its own line ending in a colon, and each command is alone in its code span on the next line. Wrong: `Catch up first` in plain text, or a bare `/crav1-finalize-commit` with no code span. Right:

   ```text
   Run next:

   **Catch up first**

   Commit the 5 changed spec files:
   `/crav1-finalize-commit`
   Then push the specs repo:
   `git push`
   ```

4. `Loop:` and other `Waiting:` lines. Since 1.167.0 Waiting keeps only what you cannot act on now, such as a person's answer or a merge; verify-behind, orphan verify rows and an unpushed specs repo are the Catch up first block.
5. The not-ready reason (only when it is not already the Run next line), at most the one-line `/crav1-build-tasks` alternative, notes, and `Uncommitted:`.
6. A not-ready ready check starts its ending with `Run next:`, naming the first real next step (1.163.0): `/crav1-tighten-plan <slug>` when the plan was reopened for review, `/crav1-verify-build-against-spec <slug>` when verify.md is behind, or `git push` when the specs repo is ahead. Since 1.167.0 the verify and push steps come as the Catch up first block, not as a separate entry. Since 1.169.0 a task whose verify failed is `Fix T#:` with `/crav1-fix-build-gaps <slug> T#` in that block, and Needs verify alone never hides a ready branch (since 1.170.0 its `T# failed verify: <reason>.` line is one short sentence or two, never the whole Verify cell): with tasks that can start the result is ready-partial and their branch blocks follow the block. A build-walk ending, one task or a whole branch, never has a `Next:` line (1.157.0). It is only the Run next block first, then Built, Left, and Waiting. A wait that used to be the reason on a Next line is a `Waiting:` line.

The standalone ready check prints a brief reply by default (1.156.0): the header, the counts row, `Result:`, that ending, `Source:` and `Build map:`. The script prints it with `walk_progress.py readiness --root <spec-folder> --write-map --text --vendor copilot`. The per-task lists and the Order line come only with the word `full`.

## The verify reply (1.168.0)

`/crav1-verify-build-against-spec` ends the same way, through the same script: `walk_ending.py --verify <state file> --vendor copilot` (the skill ships a wrapper). The reply is brief: `Verify — <slug>`, a `Result:` line with the counts, `Changed since the last verify:` with one line per task whose state changed (`T6 failed: ...`, `T44 row dropped: not in tasks.md`), `Run next:`, then `Waiting:` lines for what the user cannot act on now, then `Report: docs/specs/<slug>/verify.md`. It never has a `Next:` line. The TL;DR, the tables, branch and promotion detail stay in `verify.md`; the word `full` shows the TL;DR and Tasks overview in chat.

Run next opens with a `**Catch up first**` block, in the 1.167.0 layout, when something can be settled now: a plan note such as `T24 to T26 may belong to another slice` (`/crav1-tighten-plan <slug>`), and the files the run wrote and did not commit (`/crav1-finalize-commit`, then `git push` under its own label, since finalize-commit never pushes). That replaces the verify reply's `Uncommitted:` line. Then the step: the reason once, the label on its own line, the command alone in its code span.

```text
Run next:

**Catch up first**
The plan says T24 to T26 may belong to another slice. verify.md is not committed.

Settle the plan note in the plan:
`/crav1-tighten-plan orders-api`
Commit verify.md:
`/crav1-finalize-commit`
Then push the specs repo:
`git push`

---

T6's four tests fail on stale asserts at the PR's tip.

Fix T6:
`/crav1-fix-build-gaps orders-api T6`
```

## Run next for every other skill (1.177.0)

A skill names the single step to run now as Run next: `Run next:`, one short reason, then a label on its own line and the command alone in its code span on the next line. The label goes above the command, never under it. One step, even when the command names several pull requests or slugs.

```text
Run next:
This run added Points nothing has sorted yet.

Sort the new Points on PR 71, PR 73 and PR 74:
`/crav1-pr-status pr71, pr73, pr74`
```

When nothing is needed now: `Run next: nothing needed now.`

**Waiting on someone, then check again (1.199.0).** When the only next step is to check again after someone answers, every PR skill uses one shape: a label naming who, on its own line, above the command alone in its code span. `Run next: nothing needed now.` is only for when there is nothing to check again either. The Waiting line under it names the wait and never carries a command. The signed-in user is `you`, never their name in the third person.

```text
Run next:

Check PR 84 again after person A answers in thread 198:
`/crav1-pr-status pr84 since-last`

Waiting: person A, to answer the settings question in thread 198.
```

A card the run asks comes before the ending, and the ending is printed once, after the answers.

The four PR skills (`/crav1-open-pr`, `/crav1-pr-status`, `/crav1-review-pr`, `/crav1-merge-pr`) and their references and scripts never print a `Next:` line (1.177.0). A skill whose own file still shows the older one-line form names one step on that line and moves to Run next when it is next changed.

### The older one-line form

The ready check is the exception (1.133.0). When tasks that can start sit on more than one build-map branch, `/crav1-tasks-ready-to-build` and the tighten-and-plan ready check print one `Next:` line per branch. Since 1.143.0 each of those lines recommends `/crav1-build-walk`, with the T number beside the task name and the branch, and names `/crav1-build-tasks` as the alternative for building one task without the walk. That alternative is not a second Next. Those branches do not wait on each other, so they can start together. One ready branch stays one line. Since 1.155.0 a ready branch with two or more open tasks also gets a whole-branch entry, `` `/crav1-build-walk <slug> <branch>` ``, beside its next-task entry. Since 1.150.0 the tighten-and-plan ready and ready-partial endings print `Run next:` first, before any Waiting line. Each command is alone in a code span and is a complete invocation for a new session: the T#s on that branch, and the slug when `docs/specs` has more than one slice. Since 1.153.0 that ending has exactly one Run next block, and the walk command appears only there. The bottom keeps Waiting lines and at most a one-line `/crav1-build-tasks` alternative, with no second copy of the command and no `Next:` line of its own. The ready-check reply must give that ending once, verbatim, and must never write a `Next:` line. Since 1.163.0 a not-ready ready check also starts with `Run next:`. Each held line is in that same reply. The reply does not say above or listed above. `/crav1-build-walk` ends the same way (1.157.0). Started from a ready-to-build report with no branch chosen, it prints one Run next entry per ready branch, naming that branch's next task as `T#` plus the short name. Once one branch is in progress, it prints `Run next:` first, then Waiting and Uncommitted, and no `Next:` line. Another branch whose tasks can start is its own Run next entry. A step skill it opened does not add its own `Next:` line. Since 1.168.0 `/crav1-verify-build-against-spec` ends with Run next too (above). Since 1.173.0 every `/crav1-finalize-commit` ending, `commit`, `copy`, `stop`, or a failed commit, is Run next or nothing, never a `Next:` line. Since 1.177.0 the four PR skills end with Run next too (above). A skill not moved yet keeps the one-line form.

A skill that runs on several pull requests or slugs at once may name them in that one command. That is still one step.

When nothing is needed now:

```text
Next: nothing needed now.
```

Do not list a second step on that line, in a second `Next:` line, or as an equal bullet. The ready check's one line per ready branch is the exception above, and the `/crav1-build-tasks` name on that line is the alternative for one task, not a second step. A step that depends on this step's result is not listed. The step named here says what comes after, when that applies. Do not list `pr<n> candidates` in the same ending as pr-status. That later command is named when the record has candidates.

## Waiting

`Waiting:` appears when a step is blocked, and when a step waits on a person's yes that is not a blocker (1.129.0). It names the step and who or what it waits on. One line per such step. Keep it short. Leave the line out when nothing is waiting.

A yes that is not on record is not a blocker. The task stays unticked. `Next` is to rerun that task after the yes.

A recorded yes that the assistant's permission check refused is not a missing yes (1.143.0). Waiting says the yes is on record and the check blocked the command. The offer is to run that exact command, or allow that one command and rerun. Next is the build step again after the command has run. Do not suggest working around the check.

```text
Waiting: /crav1-resolve-open-questions orders-retry, after a reviewer answers the open question.
Waiting: the partner's yes to turn off pipelines 7 and 24.
Waiting: your yes is on record. The assistant's permission check blocked the command.
Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2, T45)
```

When the ready check says `verify.md` is behind `tasks.md` (1.135.0), that last line is the Waiting line. Do not print the `Next:` line from `verify.md`. `Next` stays the ready check's own line for tasks that can still start.

## Uncommitted

A commit is not a step. When this run changed files and they are not committed, add one trailing line. Leave it out when nothing changed, or the changes are already committed.

```text
Uncommitted: 3 files; commit with `/crav1-finalize-commit` when ready.
```

The command is in a code span (1.199.0). A PR skill whose only change is its own PR note names the one-yes commit and push: ``Uncommitted: 1 file; commit and push with `/crav1-finalize-commit commit-push`.``

Do not put the commit command in `Next` or `Waiting`.

## Which step stays Next

Rules that already pick a first step keep that choice, and use this shape.

- A `Conflict:` line was written: `Next` is `/crav1-resolve-open-questions` for that slug, because the conflict is unsettled.
- New information changed an existing slice, and no `Conflict:` line was written: `Next` is `/crav1-tighten-spec` for that slug, because the new information is not tightened yet. Resolve and the plan are not listed here.
- Spark, ideas, and bundle keep one `Left:` line with one `Next:` on that same last line. `Next` is `/crav1-tighten-spec` while gaps or open questions remain, and `/crav1-plan-from-spec` when nothing is left to tighten.
- The committed or changed files include a `walk-progress.md` with at least one `- Step:` record (`resume` reports `has_steps`), and `resume` for that folder reports a `continue_from` (1.123.0). A file that has only `- Branch run:` status lines (1.155.0) is not a paused tighten-and-plan walk. `Next` is `/crav1-tighten-and-plan-ready-to-build`, with the playbook path when the progress file has one, because the walk paused before that step. This comes before a pull request.
- The checkout has an unfinished `build-progress` file for the branch HEAD is on (1.142.0). The ending is a Run next entry, not a `Next:` line (1.157.0): the command that resumes that walk, `` `/crav1-build-walk <slug> <branch>` `` when the file has a `Run: whole branch` section, otherwise `` `/crav1-build-walk <slug> T#` `` for the file's first unticked task. The slug is left out when `docs/specs` has one slice. This comes before a pull request, after the specify walk when both are unfinished.

```text
Run next:

`/crav1-build-walk orders-api feat/orders-cicd`
continue feat/orders-cicd, the build walk has not finished this branch
```

```text
Next: /crav1-tighten-and-plan-ready-to-build docs/playbooks/orders-retry.md, because the walk paused before plan-from-spec.
```

- That does not apply, and HEAD is a base branch (`main`, `master`, `develop`, the `Merges into` branch, or `release/*`). Do not name `/crav1-open-pr`. That command cannot open a pull request from the base into itself. `Next` is the push, using the branch name HEAD is on.

```text
Next: push main, because a pull request cannot open from main into itself.
```

On a feature branch, with no unfinished walk, `Next` stays `/crav1-open-pr` when the skill that just committed already names it.

```text
Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry, because those gaps are still in the spec.
```

## Order

After the skill's own recap, print Run next (or, in a skill not moved yet, its one `Next:` line), then any `Waiting` lines, then `Uncommitted` when it applies. Nothing else is a next-step list.

The tighten-and-plan ready check is the exception (1.150.0). Print `Run next:` first, then each held line, then any `Loop` and `Waiting` lines, then at most the one-line `/crav1-build-tasks` alternative, then `Uncommitted` when it applies. No `Next:` line follows the Waiting lines (1.153.0). `Run next:` is not a second step. It is the same build-walk command, short enough to start in a new session.

## Zoom the map (1.164.0)

The ready-check reply has the `Build map: <path>` line, then a label on its own line, `Zoom the map in your browser:`, then the command alone in its code span, `` `/crav1-tasks-ready-to-build <slug> open-map` ``. Only `open-map` is offered there. `export-map` stays inside `build-map.md`.
