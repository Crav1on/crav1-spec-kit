# Fix a loop (1.161.0)

Read this only when the reply has a `Loop:` line, or the user said `fix-loop` or `fix-loop <n>`.

Two or more branches wait for each other when a task on one branch waits for a task on the other, and the other way round. Neither branch can merge first, so their tasks are Blocked. The kit works out the fix. Never tell the user to edit `tasks.md` by hand.

## What the reply shows

Under each `Loop:` line the script prints the fixes, best first:

- `Recommended fix (say `fix-loop`): …` with the whole explanation.
- `Other fix (say `fix-loop 2`): …` for each alternative, at most three fixes in all.

Each fix says, in plain words, generated from the tasks:

1. The problem, for example `T14 and T15 are on feat/orders-cicd, but they wait for T13 on feat/orders-dev-switch, which itself waits for feat/orders-cicd to merge, so the two branches wait for each other.`
2. The change, for example `Build T14 and T15 on feat/orders-dev-switch instead, right after T13.`
3. What stays: `The tasks stay the same; only the branch and pull request they go into change.`
4. The order afterwards, for example `Then feat/orders-cicd holds T9-T12 and merges first, and feat/orders-dev-switch runs T13, T14, T15, T16.`
5. `Why:` in a few words, for example `Why: the plan step for feat/orders-dev-switch already describes this work.` with no list of matched keywords.

The fix numbers run across every loop in the reply, so `fix-loop 3` always names the same fix. A ready or ready-partial reply also has a Run next entry, `/crav1-tasks-ready-to-build <slug> fix-loop`.

## How the fixes are chosen

- **Move.** A task that waits across the loop, plus the tasks on its branch that wait on it, are built on the branch it waits for. The move is kept only when that loop is gone and no new loop appears, and it never empties a branch or moves a done task. It is recommended when the target branch's plan step already describes those tasks (shared words), then the smaller move.
- **Drop a wait.** One task starts without one of its waits. It is offered as an alternative, or alone when the tasks themselves wait for each other, and it says it changes the build order.
- When no single change breaks the loop, the line says so and names `/crav1-tighten-plan`.

## Apply it

1. The user says `fix-loop` or `fix-loop <n>`, or picks it from Run next.
2. Run `<interpreter> -X utf8 scripts/walk_progress.py fix-loop --root <spec-folder> --pick <n> --text --vendor copilot` (skill `crav1-tighten-and-plan-ready-to-build`). It writes nothing, exits 0, and prints `Change:` and a `Card:` with numbered options. Ask that card as it is: the plain question, the picked fix first and marked Recommended, each option saying what happens, and `Leave it` last.
3. On yes, run the same command with `--yes`. It writes or replaces the `(map: <branch>)` mark on each moved task line (a repo word before the old branch is kept), or removes the one task from the `(after:)` mark, rebuilds `build-map.md`, and prints `No loop left.` or the next loop with its own fixes. Then `Uncommitted: docs/specs/<slug>/tasks.md, docs/specs/<slug>/build-map.md`.
4. Print its Run next entry, which reruns the ready check. Commit nothing. Never touch `spec.md`.
