---
name: gitkraken-commit-message
description: >-
  Draft a GitKraken-ready commit summary and description that match this
  repository’s existing commit style. Use when the user asks for a commit
  message, GitKraken summary/description, or text to paste into GitKraken.
disable-model-invocation: true
icon: git-commit
color: purple
---

# GitKraken commit message

You draft paste-ready **Summary** and **Description** for GitKraken. You do **not** create the commit unless the user also asked you to commit.

Style source of truth for this skill is [references/style.md](references/style.md). Prefer that file over generic Conventional Commits (`feat:`, `fix:`). If `git log` is available, match **this repo’s** recent messages first; if they disagree with the bundled examples, follow the live log.

## Steps

1. Inspect what would be committed (staged first; if empty, unstaged). On Windows, `git` may not be on `PATH` — try `git`, then `C:\Program Files\Git\cmd\git.exe`.
2. Read `git log` (about 8–15 commits: subject + body) when git works.
3. Draft **one** message for the intended set of files. Warn if `artifacts/`, `bin/`, `obj/`, or other build output is staged.
4. Output only paste blocks (see below). Do not run `git commit` unless they asked.

## Style (must match)

- **Summary:** one line, sentence case, no trailing period. Imperative or “Adds/Implement …”. Include `(T#)` when the change completes a `tasks.md` row. Not marketing (“Ship…”) and not `type(scope):`.
- **Description:** blank line conceptually after the summary (GitKraken Description field). `- ` bullets. Lead with why/what the change does; name endpoints, tests, and spec task checkboxes when those are in the diff.
- Scope the message to the files they will actually commit, not the whole conversation.

## Output

```markdown
**Summary**
```
<summary>
```

**Description**
```
- bullet
- bullet
```
```

If they should exclude paths, add one short sentence after the blocks.
