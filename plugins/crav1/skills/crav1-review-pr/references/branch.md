# Branch review (1.80.0)

Read only on `branch`: `/crav1-review-pr branch feature/orders-retry`, `/crav1-review-pr branch orders-api feature/orders-retry` (a repo from `docs/system/repos.md`), or `/crav1-review-pr branch` for the current branch. A branch named without the word is still not a pull request ([which-pr.md](which-pr.md)).

## Diff

Local git only. Never fetch, check out, commit, push or post. Use the branch, or its remote-tracking copy when only that is on disk.

The base, first found wins: the head's Match `Branch:` line and its markers (an old `; `-joined line: the head's entry) (`(into <parent>)`, `(spec branch)`), as `crav1-add-to-spec` `references/branches.md` says; then the repo's `Merges into` cell; then the default branch. Diff from the merge-base. Show one line: `Base: <base> (<where found>). Merge-base: <short sha>. Remote copy: <age>, or local only.`

No base found: ask one question with up to 4 likely bases (the branches it forked nearest to, then the default) and Other. A headless or bot run stops: `No base for <branch>. Name it: /crav1-review-pr branch <branch> into <base>.`

## Review

Run the same checks as a pull request review: spec fit, plan, `verify.md`, the first-section secret rule, findings `F1`, `F2`, … with ship, fix or drop, and suggestions. Skip the body, the linter and required-check state, the comment record and posting; say once: `Skipped: body, checks, comment, no pull request.` The verdict is in the chat only.

When the base moved on since the merge-base, suggest merging the base into the branch. Never suggest a rebase.
