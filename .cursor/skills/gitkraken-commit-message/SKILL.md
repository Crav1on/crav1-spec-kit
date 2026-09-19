---
name: gitkraken-commit-message
description: >-
  Draft a GitKraken-ready commit summary and description. Ask whether to apply
  references/style.md for this commit only or persist it as a Cursor rule.
  Use when the user asks for a commit message or GitKraken summary/description.
disable-model-invocation: true
icon: git-commit
color: purple
---

# GitKraken commit message

You draft paste-ready **Summary** and **Description** for GitKraken. You do **not** create the commit unless the user also asked you to commit.

Style file: [references/style.md](references/style.md). Prefer it over Conventional Commits (`feat:`, `fix:`).

Persistent opt-in rule (if present): `.cursor/rules/gitkraken-commit-style.mdc`.  
Template for that rule: this skill’s `assets/gitkraken-commit-style.mdc`.

## Before drafting

1. Inspect what would be committed (staged first; if empty, unstaged). On Windows, `git` may not be on `PATH` — try `git`, then `C:\Program Files\Git\cmd\git.exe`.
2. Check whether `.cursor/rules/gitkraken-commit-style.mdc` exists.

### If the rule **exists**

Do **not** ask about style. Draft using `references/style.md` (that file wins over `git log` while the rule is on). After the paste blocks, one short line: to stop this style, delete `.cursor/rules/gitkraken-commit-style.mdc`.

### If the rule **does not** exist

**Do not draft yet.** Offer two options (questions tool when available). Explain impact:

| Id | Choice | What it does | Disk |
| --- | --- | --- | --- |
| `once` | This commit only | Use `references/style.md` for **this** message. Ask again next time. | None |
| `onward` | This commit and onward | Same style for this message, **and** write `.cursor/rules/gitkraken-commit-style.mdc` (`alwaysApply: true`) so later chats do not ask. | Creates/overwrites that rule from `assets/gitkraken-commit-style.mdc` |

If they already said `once` / `onward` / “this commit only” / “keep going”, skip the menu.

After `onward`: write the rule **before** showing the message. Tell them they can remove the style later by **deleting** `.cursor/rules/gitkraken-commit-style.mdc` (no other cleanup).

## Draft

3. Read `git log` (about 8–15 commits) when git works — **only as extra context**. While applying `style.md` (this commit or the rule), `style.md` wins if the log disagrees.
4. Draft **one** message for the intended set of files. Warn if `artifacts/`, `bin/`, `obj/`, or other build output is staged.
5. Output only paste blocks (see below). Do not run `git commit` unless they asked.

## Style (must match `references/style.md`)

- **Summary:** one line, sentence case, no trailing period. Imperative or “Adds/Implement …”. Include `(T#)` when the change completes a `tasks.md` row. Not marketing (“Ship…”) and not `type(scope):`.
- **Description:** GitKraken Description field. `- ` bullets. Lead with why/what; name endpoints, tests, and spec task checkboxes when those are in the diff.
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
