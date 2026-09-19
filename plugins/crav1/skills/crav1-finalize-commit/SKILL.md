---
name: crav1-finalize-commit
description: >-
  Finalize a commit: draft GitKraken Summary and Description the same way as
  crav1-draft-commit-message, then copy for GitKraken, edit or rewrite the
  wording, or git commit when they accept it. Shows the drafted text first and
  waits for the next message before asking copy/edit/commit. Use when they want
  to change the message or actually create the commit, or /crav1-finalize-commit.
  Does not push. Does not commit until they pick commit. Paste-only with no
  follow-up: use /crav1-draft-commit-message.
disable-model-invocation: true
icon: git-branch
color: green
---

# Finalize commit

You wrap **`crav1-draft-commit-message`**. First produce the same Summary and Description. Then keep those two fields in play until they pick **copy**, **commit**, or **stop**.

Command: `/crav1-finalize-commit`.

Show the drafted **Summary** and **Description** before they choose copy, edit, or commit. Do not open a questions UI on the same turn as that wording.

Paste-only (no edit/commit menu): tell them `/crav1-draft-commit-message` instead, or they can pick `copy` here.

## Draft (same as the other skill)

Follow skill **`crav1-draft-commit-message`** in full for the first draft (drop-in: `.cursor/skills/crav1/crav1-draft-commit-message/SKILL.md`; plugin: sibling `skills/crav1-draft-commit-message/SKILL.md`):

- Style menu or persist rule (`once` / `onward` / `log-once` / `log-onward`)
- Inspect staged first, else unstaged
- Output the **Summary** and **Description** paste blocks

Do **not** run `git commit` in that step. Do **not** skip the paste blocks — they stay GitKraken-copyable on every turn.

Remember the intended file set (the paths the message describes). Warn if `agent-tools/` or build output is in that set.

## After every new wording (first draft, edit, or rewrite)

**They must see Summary and Description in the chat before choosing.** A blocking questions UI on the same turn hides that text.

On any turn that **outputs or changes** the paste blocks:

1. Put **Summary** and **Description** first (same fenced blocks as the draft skill).
2. Then one short plain-text line, **below** the blocks, not a modal. Example: `When you have read that, reply copy, edit, rewrite, commit, or stop.`
3. **End the turn.** Do not call the questions tool, AskQuestion, or any other blocking choice UI. Do not `git commit`. Do not regenerate again in this turn.

Wait for their **next message**. Only then treat `copy` / `edit` / `rewrite` / `commit` / `stop` (or equivalent wording). If that next message is vague, list the five ids as a markdown table in chat and wait again — still no questions tool.

Do not ask copy/edit/commit in the same turn as the style.md vs git-log menu. Style (if needed) is a **previous** turn with no draft yet; the draft turn is wording only.

| Id | Choice | What it does |
| --- | --- | --- |
| `copy` | Copy for GitKraken | Done. Same outcome as `/crav1-draft-commit-message`. They paste Summary/Description. No `git commit`. |
| `edit` | Change the text | They say what to change (summary, description, or both). Apply **only** those edits. Keep the same style source. Show blocks again, then **end the turn** (wording first, wait). |
| `rewrite` | New draft from the diff | Run the draft skill’s draft step again on the **same** file set and style source. Discard the previous wording. Show blocks, then **end the turn**. |
| `commit` | Create the git commit | Use the **current** Summary + Description. See below. |
| `stop` | Abort | No commit. They can still copy the last blocks. |

If they already named an id **after** seeing the current blocks, skip waiting. If they named an id **before** any wording exists, ignore it, draft first, end the turn.

Do not invent extra options (push, amend, commit subsets they did not name). If they ask to push after a successful commit, that is a **new** request — only then `git push`.

## When they pick `edit`

- If they paste a full new Summary and/or Description, use that text (cleanup only: no Conventional Commits unless the style source is git log that already uses them).
- If they give notes (“shorter summary”, “mention verify.md”), rewrite just those parts.
- Ask which field if it is unclear.
- Then paste blocks and **end the turn** (they read, then choose). Never commit in the same turn as `edit` unless they also said `commit` **after** seeing the new blocks.

## When they pick `commit`

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output.
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). Do not add `Co-authored-by` or extra trailer lines.
4. Do **not** push.
5. Show the new hash, subject, and `git status` short result.
6. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks. Wait for their next message. No questions tool.

Do not `git commit --amend` unless they explicitly asked to amend.

## Hard rules

- No questions tool / blocking choice UI on a turn that shows Summary/Description.
- No commit until `commit` (or an unambiguous “commit this message now”) **after** they have seen the current blocks.
- `copy` never runs `git commit`.
- Do not change product files except the persist rules the draft skill already writes (`draft-commit-style.mdc` / `draft-commit-gitlog.mdc`).
- Do not open a PR.
