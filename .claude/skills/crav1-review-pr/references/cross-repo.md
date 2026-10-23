# crav1-review-pr: cross repo

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Specs repo and code repo

The **code repo** is the repo the pull request is in. The **specs repo** is the checkout that has `docs/specs/`. They may be the same repo.

- **Same repo.** Everything below works as before: spec files come from the pull request head.
- **Both open.** The specs repo is the workspace folder with `docs/specs/`. The code repo is the folder whose git remote matches the pull request. When several folders have `docs/specs/`, ask which one, options only. A headless run stops: `Several spec repos open: <a>, <b>. Name one.`
- **Run from the specs repo.** A pull request from a repo in its `docs/system/repos.md`. The code repo's checkout is `../<repo>`, as `crav1-add-to-spec` `references/branches.md` says under **Sibling checkout** (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). Only an Azure DevOps diff needs that checkout.
- **Run from the code repo, specs repo not open.** Look read-only for a sibling `../*/docs/system/repos.md` with a row for this repo. When one is found, that is the specs repo: read the spec there, and write the notes there without committing; name the full path in the report.

When no specs repo is found, review against the pull request head and body as before, and print the notes in the chat with the path they would have.

The review is read-only toward the code repo and its host. The only exception is the fetch in [Diff from a sibling checkout](../SKILL.md#diff-from-a-sibling-checkout-azure-devops), after a pick.

## Other repo, in the review

For a pull request in another repo, pass its URL (or `--repo <owner>/<repo>` with the number). `gh pr diff` reads the diff from the host, so no local checkout is needed.

A spec over several repos (1.65.0): an item or task that belongs to another repo is not a spec miss on this pull request. That is a task `(branch: <other repo> …)`, a Match `Branch:` item with another repo's prefix, or a requirement the spec ties to another repo. List those parts in the `I3` info note.

For a pull request in another repo (1.65.0), the same line also names `/crav1-add-to-spec code change <repo> <head branch>`, which brings the merged branch into the spec. Do not run either.
