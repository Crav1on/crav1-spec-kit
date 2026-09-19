---
name: crav1-review-commit
description: >-
  Draft a GitKraken-style Summary and Description using crav1-draft-commit-message,
  then offer copy-only, edit the text, regenerate, or create the git commit.
  Use when the user wants to review or change the message before committing,
  or /crav1-review-commit. Do not push. Do not commit until they pick commit.
disable-model-invocation: true
icon: git-branch
color: green
---

# Review commit message

You wrap **`crav1-draft-commit-message`**. First produce the same Summary and Description. Then keep those two fields in play until they pick **copy**, **commit**, or **stop**.

Command: `/crav1-review-commit`.

Paste-only (no edit/commit menu): tell them `/crav1-draft-commit-message` instead, or they can pick `copy` here.

## Draft (same as the other skill)

Follow skill **`crav1-draft-commit-message`** in full for the first draft (drop-in: `.cursor/skills/crav1/crav1-draft-commit-message/SKILL.md`; plugin: sibling `skills/crav1-draft-commit-message/SKILL.md`):

- Style menu or persist rule (`once` / `onward` / `log-once` / `log-onward`)
- Inspect staged first, else unstaged
- Output the **Summary** and **Description** paste blocks

Do **not** run `git commit` in that step. Do **not** skip the paste blocks — they stay GitKraken-copyable on every turn.

Remember the intended file set (the paths the message describes). Warn if `agent-tools/` or build output is in that set.

## After every draft (including after an edit)

Show the two paste blocks, then **stop and ask**. Questions tool when available. Do not commit, regenerate, or rewrite until they choose.

| Id | Choice | What it does |
| --- | --- | --- |
| `copy` | Copy for GitKraken | Done. Same outcome as `/crav1-draft-commit-message`. They paste Summary/Description. No `git commit`. |
| `edit` | Change the text | They say what to change (summary, description, or both). Apply **only** those edits. Keep the same style source. Show blocks again, then this menu. |
| `rewrite` | New draft from the diff | Run the draft skill’s draft step again on the **same** file set and style source. Discard the previous wording. Show blocks, then this menu. |
| `commit` | Create the git commit | Use the **current** Summary + Description. See below. |
| `stop` | Abort | No commit. They can still copy the last blocks. |

If they already named an id or pasted replacement text, skip the menu for that turn.

Do not invent extra options (push, amend, commit subsets they did not name). If they ask to push after a successful commit, that is a **new** request — only then `git push`.

## When they pick `edit`

- If they paste a full new Summary and/or Description, use that text (cleanup only: no Conventional Commits unless the style source is git log that already uses them).
- If they give notes (“shorter summary”, “mention verify.md”), rewrite just those parts.
- Ask which field if it is unclear.
- Then paste blocks + menu again. Never commit in the same turn as `edit` unless they also said `commit`.

## When they pick `commit`

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output.
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). Do not add `Co-authored-by` or extra trailer lines.
4. Do **not** push.
5. Show the new hash, subject, and `git status` short result.
6. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks. Return to the menu.

Do not `git commit --amend` unless they explicitly asked to amend.

## Hard rules

- No commit until `commit` (or an unambiguous “commit this message now”).
- `copy` never runs `git commit`.
- Do not change product files except the persist rules the draft skill already writes (`draft-commit-style.mdc` / `draft-commit-gitlog.mdc`).
- Do not open a PR.
