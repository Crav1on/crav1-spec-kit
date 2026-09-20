---
name: crav1-draft-commit-message
description: >-
  Draft paste-ready GitKraken Summary and Description only. Does not create a
  git commit. Ask style.md vs this repo’s git log, this commit only or onward
  as a deletable rule. Use for GitKraken paste, or /crav1-draft-commit-message.
  To edit the wording and then copy or git commit, use /crav1-finalize-commit.
disable-model-invocation: true
icon: git-commit
color: purple
---

# Draft commit message

You draft paste-ready **Summary** and **Description** (GitKraken fields). You do **not** create the commit unless the user also asked you to commit.

Command: `/crav1-draft-commit-message`. To **edit** the text and/or **create** the commit after they accept it, use `/crav1-finalize-commit` (it follows this skill, then a commit / copy / edit / rewrite / stop menu, **commit first**).

Bundled style: [references/style.md](references/style.md).  
Git-log style: this repo’s recent `git log` (subject + body).

Persistent rules (at most one should exist):

| File | Meaning | Template |
| --- | --- | --- |
| `.cursor/rules/draft-commit-style.mdc` | Always `style.md` | `assets/draft-commit-style.mdc` |
| `.cursor/rules/draft-commit-gitlog.mdc` | Always live `git log` | `assets/draft-commit-gitlog.mdc` |

Also treat these **legacy** names as the same persist (if you find them, use them; new writes use the names above):

- `.cursor/rules/gitkraken-commit-style.mdc` → style.md onward
- `.cursor/rules/gitkraken-commit-gitlog.mdc` → git log onward

## Before drafting

1. Inspect what would be committed (staged first; if empty, unstaged). On Windows, `git` may not be on `PATH` — try `git`, then `C:\Program Files\Git\cmd\git.exe`.
2. Read `git log` (about 8–15 commits: subject + body) when git works.
3. Check which persist rule exists (new names first, then legacy).

### If a **style.md onward** rule exists

Do **not** ask. Draft using `references/style.md` (`style.md` wins over the log). After the blocks: delete that rule file to stop; mention the git-log rule if both files exist (ask which to keep).

### If a **git-log onward** rule exists (and no style.md rule)

Do **not** ask. Draft matching **live `git log`**. If the log is empty, say so and fall back to asking the menu. After the blocks: delete the git-log rule file to stop.

### If neither rule exists

**Do not draft yet.** Offer these options (questions tool when available). Explain impact:

| Id | Choice | What it does | Disk |
| --- | --- | --- | --- |
| `once` | `style.md`, this commit only | Use bundled `references/style.md` for **this** message. Ask again next time. | None |
| `onward` | `style.md`, this commit and onward | Same, **and** write `draft-commit-style.mdc`. Remove any git-log persist rule. | Rule from `assets/draft-commit-style.mdc` |
| `log-once` | Git log, this commit only | Match **this repo’s** recent messages for **this** message. Ask again next time. | None |
| `log-onward` | Git log, this commit and onward | Same, **and** write `draft-commit-gitlog.mdc`. Remove any style.md persist rule. | Rule from `assets/draft-commit-gitlog.mdc` |

If `git log` is empty or unavailable, say that `log-once` / `log-onward` have no pattern to copy; they can still pick `style.md`.

If they already named an id (`once`, `onward`, `log-once`, `log-onward`), skip the menu.

After `onward` or `log-onward`: write the matching **new** rule name **before** showing the message, and delete the other persist files (including legacy names) so only one remains. Tell them they undo by **deleting that rule file**.

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
