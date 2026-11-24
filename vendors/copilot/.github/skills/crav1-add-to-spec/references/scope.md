# Scope (1.75.0)

Which open questions, specs, or actions a run covers. `/crav1-show-or-ask-open-questions`, `/crav1-resolve-open-questions` and `/crav1-help todo` follow this file. Everything here is read-only.

## Person, spec, topic

Moved word for word from `/crav1-show-or-ask-open-questions` in 1.75.0.

- **Person.** The question names that person as who can answer, says `waiting for <person>`, says `via <person>`, or has an `Asked:` or `Pending:` line for that person. A question whose who is a group the person speaks for (the user says so, or the question says `via <person>`) is included. Do not guess who can answer a question that names nobody. List those separately as `No one named`, and ask whether to include them.
- **Spec.** Every open question on that spec.
- **Topic.** Match by meaning across all specs. Spec titles and the question words weigh most.
- **One question (1.77.0).** Words or `<spec> Q#` (document order, never written) pick one; several: ask, up to 4, rest under Other.

## Branch

A branch name scopes to every spec that names it as a work branch, as [branches.md](branches.md) says under **Where each branch is named**. A branch in another repo may start with the repo: `orders-api feat/orders-retry`.

## Pull request

The user writes `pr71`, `pr 71`, `#71`, or `pr <repo> 71`. No repo means the open repo. Find the specs in this order and say which step found it (`Found in the PR note`, `Found in the local git log`, `Found on GitHub`):

1. **PR note.** Search the month `docs/notes/YYYY-MM/index.md` files for `source: PR <n>` with that repo. The note's `used_by` names the specs, and its `<base> ← <head>` line gives the head branch, scoped as **Branch** above. A Match `Branch:` entry ending in `(PR <n>)` counts the same.
2. **Local git log** of that repo (open checkout or `../<repo>`), no fetch: `git log --all --grep` for `Merge pull request #<n> from <owner>/<branch>`, `(#<n>)` at the end of a subject, or `Merged PR <n>:`. A merge subject gives the head branch. Otherwise match the commit to the `commits:` of code-change notes.
3. **Online, only after asking.** Check sign-in locally, without logging in: `gh auth status` and `az account show`. When one is signed in for this remote, look it up read-only (`gh pr view <n> --json headRefName`, `az repos pr show --id <n> --detect false`) without asking. Otherwise ask, with the sign-in status as one line (`gh: not signed in. az: not installed.`):

   PR <n> isn't in the records or the local git history. To look it up online, sign in to GitHub (`gh auth login`) or Azure DevOps (`az login`) in a terminal, then pick A.

   - A) I've signed in, look it up
   - B) Use a branch name instead
   - C) Stop

   A runs one sign-in check, then the lookup. Still not signed in: show the question once more. Never poll. A headless or bot run does not ask: it prints the status line and `PR <n> not found offline.` and stops.

An open PR that no skill has read yet is found only by step 3.
