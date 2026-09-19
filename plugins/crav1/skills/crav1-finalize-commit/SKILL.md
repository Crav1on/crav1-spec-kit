---
name: crav1-finalize-commit
description: >-
  Finalize a commit: style.md vs git log first if needed, then draft GitKraken
  Summary and Description, then offer copy / edit / rewrite / git commit.
  Wording is shown before those choices. Use when they want to change the
  message or actually create the commit, or /crav1-finalize-commit. Does not
  push. Does not commit until they pick commit. Paste-only: /crav1-draft-commit-message.
disable-model-invocation: true
icon: git-branch
color: green
---

# Finalize commit

You wrap **`crav1-draft-commit-message`**. First produce the same Summary and Description. Then keep those two fields in play until they pick **copy**, **commit**, or **stop**.

Command: `/crav1-finalize-commit`.

Order: (1) style menu if no persist rule, (2) generate and show Summary/Description, (3) then the copy/edit/rewrite/commit/stop choices. Never put those choices before the wording exists.

Paste-only (no copy/edit/commit choices): tell them `/crav1-draft-commit-message` instead, or they can pick `copy` here.

## Draft (same as the other skill)

Follow skill **`crav1-draft-commit-message`** in full for the first draft (drop-in: `.cursor/skills/crav1/crav1-draft-commit-message/SKILL.md`; plugin: sibling `skills/crav1-draft-commit-message/SKILL.md`):

- Style menu or persist rule (`once` / `onward` / `log-once` / `log-onward`)
- Inspect staged first, else unstaged
- Output the **Summary** and **Description** paste blocks

Do **not** run `git commit` in that step. Do **not** skip the paste blocks — they stay GitKraken-copyable on every turn.

Remember the intended file set (the paths the message describes). Warn if `agent-tools/` or build output is in that set.

## After every new wording (first draft, edit, or rewrite)

They choose **after** the message exists, not before.

**Do not** open copy/edit/commit choices in the same turn as the style.md vs git-log menu. If style is needed, that turn is style only: no draft, no finalize choices.

On the turn that produces wording:

1. Finish the draft (git inspect, style already chosen).
2. Write the **Summary** and **Description** paste blocks into the user-visible reply. This is required. Do not skip it.
3. **Then** offer the choices (questions tool when available). Put the **actual Summary and Description** in the question prompt so the choice UI still shows the generated text, for example:

   `Summary: <one line>`

   `Description:` (the bullets)

   `What next?`

   Options: `copy` / `edit` / `rewrite` / `commit` / `stop`.

Never call the questions tool (or any blocking choice UI) **before** step 2. Never call it as the first action of a draft turn. Draft first, choices last. Do not `git commit` until they pick `commit`.

| Id | Choice | What it does |
| --- | --- | --- |
| `copy` | Copy for GitKraken | Done. Same outcome as `/crav1-draft-commit-message`. They paste Summary/Description. No `git commit`. |
| `edit` | Change the text | They say what to change (summary, description, or both). Apply **only** those edits. Keep the same style source. Show the new blocks, **then** the same choices again. |
| `rewrite` | New draft from the diff | Run the draft skill’s draft step again on the **same** file set and style source. Discard the previous wording. Show the new blocks, **then** the same choices again. |
| `commit` | Create the git commit | Use the **current** Summary + Description. See below. |
| `stop` | Abort | No commit. They can still copy the last blocks. |

If they named `copy`/`edit`/`commit` **before** any wording exists, ignore it, draft, show blocks, then offer choices.

Do not invent extra options (push, amend, commit subsets they did not name). If they ask to push after a successful commit, that is a **new** request — only then `git push`.

## When they pick `edit`

- If they paste a full new Summary and/or Description, use that text (cleanup only: no Conventional Commits unless the style source is git log that already uses them).
- If they give notes (“shorter summary”, “mention verify.md”), rewrite just those parts.
- Ask which field if it is unclear.
- Then show the new paste blocks and **then** the same choices again. Never commit in the same turn as `edit` unless they also said `commit` **after** seeing the new blocks.

## When they pick `commit`

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output.
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). Do not add `Co-authored-by` or extra trailer lines.
4. Do **not** push.
5. Show the new hash, subject, and `git status` short result.
6. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks, **then** offer the choices again.

Do not `git commit --amend` unless they explicitly asked to amend.

## Hard rules

- Never offer copy/edit/commit before Summary/Description exist. After they exist, show the blocks, then the choices (question prompt includes that wording).
- No commit until `commit` (or an unambiguous “commit this message now”) **after** they have seen the current blocks.
- `copy` never runs `git commit`.
- Do not change product files except the persist rules the draft skill already writes (`draft-commit-style.mdc` / `draft-commit-gitlog.mdc`).
- Do not open a PR.
