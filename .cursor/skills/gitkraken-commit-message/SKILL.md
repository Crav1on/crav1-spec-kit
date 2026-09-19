---
name: gitkraken-commit-message
description: >-
  Draft a GitKraken-ready commit summary and description. Ask whether to use
  references/style.md or this repo’s git log, for this commit only or onward
  as a deletable Cursor rule. Use when the user asks for a commit message or
  GitKraken summary/description.
disable-model-invocation: true
icon: git-commit
color: purple
---

# GitKraken commit message

You draft paste-ready **Summary** and **Description** for GitKraken. You do **not** create the commit unless the user also asked you to commit.

Bundled style: [references/style.md](references/style.md).  
Git-log style: this repo’s recent `git log` (subject + body).

Persistent rules (at most one should exist):

| File | Meaning | Template |
| --- | --- | --- |
| `.cursor/rules/gitkraken-commit-style.mdc` | Always `style.md` | `assets/gitkraken-commit-style.mdc` |
| `.cursor/rules/gitkraken-commit-gitlog.mdc` | Always live `git log` | `assets/gitkraken-commit-gitlog.mdc` |

## Before drafting

1. Inspect what would be committed (staged first; if empty, unstaged). On Windows, `git` may not be on `PATH` — try `git`, then `C:\Program Files\Git\cmd\git.exe`.
2. Read `git log` (about 8–15 commits: subject + body) when git works.
3. Check which persist rule exists.

### If `gitkraken-commit-style.mdc` exists

Do **not** ask. Draft using `references/style.md` (`style.md` wins over the log). After the blocks: delete that rule file to stop; mention the git-log rule if both files exist (ask which to keep).

### If `gitkraken-commit-gitlog.mdc` exists (and the style.md rule does not)

Do **not** ask. Draft matching **live `git log`**. If the log is empty, say so and fall back to asking the menu. After the blocks: delete `.cursor/rules/gitkraken-commit-gitlog.mdc` to stop.

### If neither rule exists

**Do not draft yet.** Offer these options (questions tool when available). Explain impact:

| Id | Choice | What it does | Disk |
| --- | --- | --- | --- |
| `once` | `style.md`, this commit only | Use bundled `references/style.md` for **this** message. Ask again next time. | None |
| `onward` | `style.md`, this commit and onward | Same, **and** write `gitkraken-commit-style.mdc`. Remove `gitkraken-commit-gitlog.mdc` if it exists. | Rule from `assets/gitkraken-commit-style.mdc` |
| `log-once` | Git log, this commit only | Match **this repo’s** recent messages for **this** message. Ask again next time. | None |
| `log-onward` | Git log, this commit and onward | Same, **and** write `gitkraken-commit-gitlog.mdc`. Remove `gitkraken-commit-style.mdc` if it exists. | Rule from `assets/gitkraken-commit-gitlog.mdc` |

If `git log` is empty or unavailable, say that `log-once` / `log-onward` have no pattern to copy; they can still pick `style.md`.

If they already named an id (`once`, `onward`, `log-once`, `log-onward`), skip the menu.

After `onward` or `log-onward`: write the matching rule **before** showing the message, and delete the other persist file so only one remains. Tell them they undo by **deleting that rule file**.

## Draft

4. Apply the chosen source (`style.md` **or** live log — not a blend that reintroduces Conventional Commits unless the log already uses it).
5. Draft **one** message for the intended set of files. Warn if `artifacts/`, `bin/`, `obj/`, or other build output is staged.
6. Output only paste blocks (see below). Do not run `git commit` unless they asked.

## When the source is `style.md`

- **Summary:** one line, sentence case, no trailing period. Imperative or “Adds/Implement …”. Include `(T#)` when the change completes a `tasks.md` row. Not marketing (“Ship…”) and not `type(scope):`.
- **Description:** GitKraken Description field. `- ` bullets. Lead with why/what; name endpoints, tests, and spec task checkboxes when those are in the diff.

## When the source is git log

- Copy the **shape** of recent subjects and bodies (length, prefixes or lack of them, bullets vs paragraph).
- Do not force `style.md` rules if the log does something else (including Conventional Commits).
- Still scope the message to the files they will actually commit.

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
