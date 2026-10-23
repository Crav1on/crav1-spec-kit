# Pull request host (GitHub and Azure DevOps)

Shared by `/crav1-open-pr` (to create) and `/crav1-review-pr` (to read). Read only when the pointer in that skill's `SKILL.md` sends you here. Moved word for word from both `SKILL.md` files in 1.86.3; the rules are unchanged.

## Order

Resolve **one** path, in this order: GitHub `gh`, then Azure DevOps `az`, then the no-host step.

- **open-pr (create):** the no-host step is printed commands and GitKraken GUI paste. Do not claim a pull request was opened unless that path returned a URL.
- **review-pr (read):** the no-host step is to say you cannot read the pull request. Do not claim you read it unless that path returned the diff and the body.

## GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the repo is GitHub (`github.com`, or `gh repo view` succeeds for that repo).

- **open-pr:** GitHub means the remote URL. **Create** then uses the GitHub steps. If the remote is GitHub and `gh auth status` does not succeed, print the GitHub-shaped fallback (`references/fallback.md`, "Fallback (no URL)"). Do not use `az`.
- **review-pr:** GitHub means `github.com` in the URL, the remote, or the `repos.md` URL. When `gh auth status` fails, read that skill's `references/github.md` ("GitHub not signed in").

## Azure DevOps (`az`)

Read the skill's own `references/azure-devops.md` ("Azure DevOps (`az`)") only when the remote is Azure DevOps.

## Other remotes

- **open-pr:** when the remote is neither GitHub nor Azure DevOps, print the GitHub-shaped fallback. Do not claim a pull request was opened. When no host CLI can open the pull request, read `references/fallback.md` ("Fallback (no URL)").
