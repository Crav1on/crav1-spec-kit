# crav1-open-pr: base branch

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.3; the rules are unchanged.

## Base branch

**Into and Merges into (1.64.0).** Before the default-branch steps below, as skill `crav1-add-to-spec`, `references/branches.md` says:

1. **Into.** When the head is listed in a spec's Match `Branch:` list with an `(into <branch>)` marker, that branch is the base. When the head has no marker and its fork point (as skill `crav1-add-to-spec`, `references/branches.md` says) is another spec branch, ask once before the draft (1.68.0): "<head> split off <parent>. Does it merge into <parent>?" A yes writes `(into <parent>)` on the head's entry, and `(spec branch)` on the parent's entry when it has none, in the spec repo (not committed), and the base is <parent>. A no writes nothing and goes on to step 2. A headless run doesn't ask and writes nothing. A sub-branch's PR goes into its spec branch; the spec branch's PR goes into the Merges into branch.
2. **Merges into.** Else, when `docs/system/repos.md` has a `Merges into` cell for this repo, that branch is the base. When the open repo has no `docs/system/repos.md` row for itself (the specs live in another repo), look read-only in the sibling checkouts (`../*/docs/system/repos.md`) for one row naming this repo, and use its cell. Several rows that disagree: ask.
3. Else the default branch, from the steps below.

Name where the base came from in the draft (`Base: develop (Merges into in ../orders-specs/docs/system/repos.md)`).

Default branch:

1. `git symbolic-ref refs/remotes/<remote>/HEAD` (for example `origin/main` → `main`) when that ref exists.
2. Else, when `gh auth status` succeeds and the remote is GitHub, `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.
3. Else the local branch `main`, else `master`, else `develop`, when exactly one of those exists.
4. If more than one candidate remains, or none does, **ask**. Do not guess.
