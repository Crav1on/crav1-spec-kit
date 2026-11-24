# crav1-review-pr: github

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.80.2; the rules are unchanged.

## GitHub not signed in

If the pull request is on GitHub and `gh auth status` does not succeed, stop. Say `gh` is not authenticated. Do not use `az`. Do not invent a review.

## GitHub (Read it first)

```text
gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,headRefOid,headRepository,headRepositoryOwner,files,statusCheckRollup
gh pr diff <n-or-url>
gh pr checks <n-or-url>
```

Read `references/cross-repo.md` ("Other repo, in the review") only when the pull request is in another repo.

`state` must be `OPEN`.
