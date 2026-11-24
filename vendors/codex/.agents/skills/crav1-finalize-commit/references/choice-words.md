# Choice words

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

Exact words for bots and scripted runs. There are no `--flags`.

- Commit or message: `commit` / `commit-now` / `message-only` (draft, show, done: the same as `copy`, no git commit).
- Base branch (1.99.0): `new-branch` (create `feat/<slug>` from the into branch and commit there).
- Style: `crav1` / `git-log`.
- Trailer hook: `strip-trailers` / `keep-trailers`.
- Pull: `pull` (1.81.0) runs the pull path with no commit first.
- Commit and push (1.199.0): `commit-push` is `commit-now`, then one plain `git push` once the fetch check says nothing was lost. One yes covers both. A rejected push stops with the pull advice in [pull.md](pull.md); never a force push.

`commit-now`, and `commit` typed in the invocation (1.76.1): draft, show the paste blocks, then commit with no commit-or-message choice question. commit-now may still ask one question: the work-item mention question, when `work-item.md` has several Feature lines and none clearly matches the slice (1.193.0, [work-item-mention.md](../branches/message-only/references/work-item-mention.md)). A headless run with no one to answer ends as `copy`. When `agent-tools/` or build output is in the file set, warn and offer the normal choices instead. On a base branch with implementation code staged (1.99.0), ask the base-branch prompt instead ([base-branch.md](base-branch.md)); `new-branch` answers it.

Kit-rewritten files (1.173.0): when the only changed files are kit-owned files the kit rewrote (`build-map.md`, `walk-progress.md`, `build-progress/*`) and a value in them disagrees with `verify.md` or `build-progress`, such as a done hash, a typed `commit` or `commit-now` still asks. Say which value disagrees and offer the normal choices with `stop` recommended. Except (1.180.0): a task recorded merged on the host but not ticked is tick pending, not a disagreement worth `stop`. Run `scripts/task_state.py commit-check --root <spec-folder>` in this skill for each changed spec folder. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not decide it in the chat. When it lists `tick_pending`, print its `line`, recommend `commit` (its `recommend`), and put its `run_next` entry in Run next as-is: the verify step when `verify.md` does not pass the task yet, else the tick.

When the invocation contains one of these words (for example `$crav1-finalize-commit commit`), take that choice and do not ask. This holds for a person, a bot, or a headless run.
