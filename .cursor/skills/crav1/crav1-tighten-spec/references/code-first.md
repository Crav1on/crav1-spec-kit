# crav1-tighten-spec: code first

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Read committed code first

Decide in this order. Stop at the first match.

1. **No code behind it.** Match status is `not in the code`, or the spec never claims existing code (no partial status, no status `done`, no `## In the code`, and it already has Problem, Goals, or Acceptance criteria). Skip the read. Tighten as this skill does today.
2. **Too thin.** The slice is partial, status is `done`, or `## In the code` is present, and the spec does not name a repo or does not name paths that can be read. Also too thin: there is no partial status and no `## In the code`, and step 1 did not match. Stop. Name `/crav1-add-to-spec` when a change already landed on an existing spec. Name `/crav1-existing-to-specs` when the slice was never matched. Do not guess. Do not tighten. Do not invent the repo or the paths.
3. **Read.** The slice is partial, or `## In the code` names paths. Read the committed code on the repo and branch the spec names. That code is the current fact. Wording issues come after that read.

The rest of this section applies only when step 3 matched.

The repo is the Match repo line, a `Synced at` line, or another line in `spec.md` that names it. The branch is the branch on that line. Do not take the repo or the branch from the open checkout. Do not take a branch from `docs/system/repos.md` when the spec does not name it.

Read only that repo and the branches the spec lists. If the open checkout is a different repo, read that repo's code from `../<repo>` as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Sibling checkout** (ask for the path with options only when it is missing; a headless run stops with `No checkout found for <repo>. Name its path.`). Do not read the open tree when it is not the named repo.

**Several branches (1.64.0).** A spec may list its work branches in its `Synced at` lines, its Match `Branch:` lines (one per branch; an old `; `-joined line counts as its entries) and its tasks' `(branch: …)` parts. Read every work branch without checking it out (`git show <branch>:<path>`, `git diff`), from the refs on disk; never fetch. Say which branch each piece of code is on, and label a piece that only exists on an unmerged branch `only on <branch>, not merged`. The rule "stop when the open checkout is a different branch" applies only to branches the spec does not list. Name the age of each remote copy read, as the same file says.

Do not treat a stub as the code. A stub is a placeholder, for example a `.gitkeep` on `main`. If the paths on the named branch are only a stub, stop and say so. Do not tighten against that stub.

If the spec names no branch, stop and ask which branch has the code. Do not assume `main`. Do not assume the open checkout. When that repo lists branches, the options are those branches. Do not pick one. After the user answers, that branch is the read. Then ask whether to write the branch onto the spec, in the same batch as the issues (1.70.0). That question is yes or no. It is not an `I#` patch. On yes, add `Branch: <name>` beside the repo the spec already names (under `## Match` when that section exists, otherwise one line after the title and before the first heading). When `Branch:` lines are already there, a yes adds a new line in sorted place (repo, then branch), as `crav1-add-to-spec` `references/merge-safe.md` says (1.86.0): `- Branch: feat/orders-retry` above `- Branch: feature/orders-openapi`. It never replaces or joins the lines already there. When the spec spans repos, start the line with the repo (`- Branch: orders-api feat/orders-retry`). Spec branch and sub-branches (1.68.0): read `(into …)` and `(spec branch)` markers already on the list and keep them. When the written branch's fork point is another listed branch and it has no marker, ask one more yes/no question, "<branch> split off <parent>. Does it merge into <parent>?", as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Spec branch and sub-branches**. A yes writes `(into <parent>)` on that line and `(spec branch)` on the parent's line when it has none. A no writes nothing (stacked). A headless run doesn't ask and writes nothing. On no, leave the spec unchanged. This read still uses that branch. Do not set `Synced at`. Do not write the branch as a silent edit. If the spec already names the branch, do not ask.

Read the committed files on that branch. An uncommitted edit is not the fact.

A disagreement between the spec and that code is called out. Quote what the spec says and what the code does. Do not silently rewrite the spec to match the code. The same call-out applies when tightened wording would disagree with the code. Do not offer finish the gap, add a verify test, or leave it. Those choices belong to `/crav1-plan-from-spec`.
