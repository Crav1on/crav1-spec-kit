# crav1-plan-from-spec: built pieces

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Built pieces (before any task)

Skip this section when the spec has no code behind it. No code behind it means match status `not in the code`, or the spec never claims existing code (no partial status, no status `done`, no `## In the code`, and it already has Problem, Goals, or Acceptance criteria).

When the spec is partial, or `## In the code` names paths, do this before any task is written.

Use the same repo and branch test as `/crav1-tighten-spec`. The repo is the Match repo line, a `Synced at` line, or another line in `spec.md` that names it. The branch is the branch on that line. Do not take them from the open checkout. Do not take a branch from `docs/system/repos.md` when the spec does not name it.

**Several branches and other repos (1.64.0).** The spec's work branches are every branch in its `Synced at` entries, its Match `Branch:` list and its tasks' `(branch: …)` parts, minus the base branches and `(dropped)` entries, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says. Read every work branch without checking it out (`git show <branch>:<path>`, `git diff`), from the refs on disk; never fetch. Each built piece says which branch it is on. A piece that only exists on an unmerged branch is labeled `only on <branch>, not merged`. When the named repo is not the open checkout, read it from `../<repo>` as the same file says under **Sibling checkout** (options-only ask when missing; headless stops with `No checkout found for <repo>. Name its path.`). Never write in that checkout.

**Sub-branches (1.68.0).** When the spec has a `(spec branch)`, a task may name its own sub-branch: `(branch: feat/orders-capacity-t3)`, usually `<spec branch>-t<n>`. Name a sub-branch only when the user asks for one branch per task or the spec already lists sub-branches; never invent the setup. The branch need not exist yet; `/crav1-create-feature-branch` and `/crav1-build-tasks` offer to create it from its into branch.

If the open checkout is a different repo, or a branch the spec does not list, stop and name the right ones. Do not read the open tree. Do not treat a stub as the code. A stub is a placeholder, for example a `.gitkeep` on `main`. If the paths on the named branch are only a stub, stop and say so.

If the spec names no branch, stop and ask which branch has the code. Do not assume `main`. Do not assume the open checkout. When that repo lists branches, the options are those branches. Do not pick one. After the user answers, that branch is the read. Do not write the branch onto the spec. That yes or no belongs to `/crav1-tighten-spec`. This skill leaves `spec.md` alone.

If the spec is too thin for that read (partial, status `done`, or `## In the code` without a repo or without paths), stop. Name `/crav1-add-to-spec` when a change already landed on an existing spec. Name `/crav1-existing-to-specs` when the slice was never matched. Do not guess. Do not write a task.

Read the committed files on that branch. An uncommitted edit is not the fact. List every built piece. Do not drop one to keep the list short.

- A piece that already matches v0 is not a choice. Mark it already there. Give it no rebuild task.
- A piece the code only partly has, where v0 wants the rest, is a choice.
- A disagreement is its own line, before any task exists. Quote what the spec says and what the code does. The spec says one environment and the code enables another is one such line. It is not a match. Do not fold it into another piece.

Each choice says what it means and what it will do. These three are the only choices. Use the questions tool when it is available.

- **A. Finish the gap.** The code is partly there and v0 wants the rest. Write a task for that gap only. Do not rebuild what already matches.
- **B. Add a verify test.** The code stays as it is. Write a task for a test that checks what is already there. Do not change the feature.
- **C. Leave it.** No task. The plan gets one line saying this piece was left as committed. A later run does not turn it into work unless the user says so.

The user can answer one line or a batch (`auth A, export C`). An unanswered line stays open. Do not write a task until the choices that are open have an answer. A piece marked already there does not wait.

A later run reads `## Left as committed` when that heading is already in `plan.md`. It does not offer those pieces again unless the user says so in this turn.

On the trace, `already there` and `left as committed` are not missing tasks. A finish-the-gap task maps only the gap. An add-a-verify-test task maps a test of what is already there and does not change the feature.
