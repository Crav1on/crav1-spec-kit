# crav1-open-pr: existing pull request

Read only when the pointer in `SKILL.md` sends you here: a pull request is already open for this head → base (1.114.0).

## Find and read it

After the push (or open only) succeeded, read the open pull request for head → base on the host picked in **Host**:

- GitHub: `gh pr list --head <head> --base <base> --state open --json number,url,author,body,title,createdAt,updatedAt`, and the current user from `gh api user --jq .login`.
- Azure DevOps: `az repos pr list --source-branch <head> --target-branch <base> --status active --output json` (read `pullRequestId`, `createdBy`, `title`, `description`, `creationDate`), and the current user from `az account show --query "user.name"`. Compare by unique name or email, case-insensitive.

When the author cannot be told, treat it as someone else's pull request. When no host CLI can read it, print the URL, say the description was not updated and no comment was posted, and stop.

**What is new.** List the commits on the head since the description was written: since the last commit the description links to (format A links are pinned to a commit), else since the pull request was last updated, else since it was created. Show them as one short list (short sha, subject). When none are new, say so and offer only **push only** (already done) and **stop**.

## Choices

Show the pull request (`PR <n>`, title, author, URL) and what is new, then ask once. Options **in this order**:

| Their own pull request | Someone else's pull request |
| --- | --- |
| `update` Update description | `comment` Add as comment |
| `comment` Add as comment | `update` Update description |
| `push-only` Push only | `push-only` Push only |
| `stop` Stop | `stop` Stop |

`push-only` and `stop` post nothing; the push already happened. Say so.

## Draft the text

- **Update description.** Keep format A (`references/draft.md`). Add or change only the bullets and sections the new commits touch; re-pin their links to the new head commit. Keep every line a person wrote or edited (anything not in format A, reworded bullets, added notes) unless it is now wrong; then say which line and why. Show the full new description, then the changed lines as a short `Changed:` list (added, edited, removed).
- **Add as comment.** A short comment: one opening line saying what was pushed and why, then one bullet per change, link first to its file and lines at the new head commit, then what changed and why. End with anything a reviewer should look at again. It is kit-neutral, like a posted review: no specs, plans, tasks, lanes, notes, skill or command names, tool names, or file-type words; it reads as a person's comment.

## Edit before posting

Show the exact text in a fenced block, then end with:

> **Reply yes** (or "confirm") to post it as shown.
> To change something first, reply with your edits, for example "drop the second bullet".
> Nothing is posted until you say yes.

On edits, apply only those, show the whole text again with the same three lines. Post only on a yes given after the latest text was shown. A yes from before a redraft does not count.

## Post

- GitHub: description `gh pr edit <n> --body-file <file>`; comment `gh pr comment <n> --body-file <file>`.
- Azure DevOps: description `az repos pr update --id <n> --description "@<path>"`; comment as a new thread through `az devops invoke --area git --resource pullRequestThreads --route-parameters project=<project> repositoryId=<repo> pullRequestId=<n> --http-method POST --in-file <path>` with one comment of type `text` and status `active`. Use the temp-file steps in `references/azure-devops.md` (UTF-8 without a BOM, quoted `@`, delete the file after).

Do not change the title, reviewers, labels, draft state, work items or auto-complete. On success, print the URL of the pull request or comment. On failure, show the error and keep the text so they can paste it. Then follow **After it exists**.
