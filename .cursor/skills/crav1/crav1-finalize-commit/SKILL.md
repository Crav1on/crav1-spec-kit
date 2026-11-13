---
name: crav1-finalize-commit
description: >-
  Use when the user wants a commit message drafted or a commit made. Drafts
  Summary and Description first, then offers commit, copy, change, or stop.
  Choice words: `message only`, `commit now`, `pull`; `crav1` or `git log`
  sets the style. Never pushes.
disable-model-invocation: true
icon: git-branch
color: green
---

# Finalize commit

## No opening question (1.83.0)

Always draft first. There is no question before the wording. The draft rules are the message only branch, [branches/message-only/BRANCH.md](branches/message-only/BRANCH.md), whose style, work-item mention, and work-item offer rules apply to every run.

First produce the Summary and Description. Then keep those two fields in play until they pick **commit**, **copy**, or **stop**.

Command: `/crav1-finalize-commit`.

Order (1.89.0): (1) generate and show Summary/Description, in the recommended style when no persist rule is saved, (2) then one prompt: the choices with **`commit` first** (top of the questions tool), then copy / change / stop, plus the style question when no persist rule is saved. There is no style menu before the draft.

## Choice words

Read `references/choice-words.md` ("Choice words") when the invocation has any word after the command.

Headless or bot run with no choice word (no person in the chat to answer): draft, show the blocks, and end as `copy`. No git commit.

## Draft

Follow [branches/message-only/BRANCH.md](branches/message-only/BRANCH.md) for the first draft:

- Persist rule, else draft in the recommended style; the style question (`once` / `onward` / `log-once` / `log-onward`) waits for the choices
- Inspect staged first, else unstaged
- Output the **Summary** and **Description** paste blocks
- Work-item mention, when [work-item-mention.md](branches/message-only/references/work-item-mention.md) resolves one: one blank line, then that mention as the **last line** of the Description. Subject stays as drafted.

Do **not** run `git commit` in that step. Do **not** skip the paste blocks — they stay GitKraken-copyable on every turn. The mention is inside the Description fence, so a GitKraken paste includes it. A work-item hint stays after the fences.

Remember the intended file set (the paths the message describes). Warn if `agent-tools/` or build output is in that set.

## After every new wording (first draft or change)

They choose **after** the message exists, not before.

When the style is not settled, ask CRAV1 style vs git log in the same questions call (1.70.0); a different style answer redrafts before anything is committed. Ask the style question at most once per run (1.90.5): once answered, or given as a choice word, every later draft in this run uses that answer without asking again.

On the turn that produces wording:

1. Finish the draft (git inspect; style from the persist rule, else the recommended style).
2. Write the **Summary** and **Description** paste blocks into the user-visible reply. This is required. Do not skip it.
3. **Then** offer the choices. The prompt is `Commit this message?`. The blocks are already in the reply above; do not repeat them in the prompt.

   Options, **in this order**: `commit` / `copy` / `change` / `stop`. **`commit` is always the first/top option** in the questions tool and in any bullet list.

Without a questions tool, use numbered lists, one per question, then end with `Reply with choice words in one line, e.g. commit once strip trailers.`

Never call the questions tool (or any blocking choice UI) before step 2.

Trailer hook (1.90.0): when no answer is saved and `.githooks/commit-msg` is missing or not turned on, read [references/trailer-hook.md](references/trailer-hook.md) before the choices (`strip trailers` / `keep trailers`). Do not open it when an answer is saved or the hook is already on.

| Id | Choice | What it does |
| --- | --- | --- |
| `commit` | Create the git commit | Use the **current** Summary + Description. See below. **Always list this first.** |
| `copy` | Copy for GitKraken | Done. Same outcome as `/crav1-finalize-commit`. They paste Summary/Description. No `git commit`. |
| `change` | Edit or rewrite | They say what to change (summary, description, or both), or say rewrite for a new draft from the diff. See below. |
| `stop` | Abort | No commit. They can still copy the last blocks. |

If they named `copy`/`change`/`commit` **before** any wording exists, ignore it, draft, show blocks, then offer choices.

Do not invent extra options (push, amend, commit subsets they did not name). A push asked for after the commit is a **new** request.

**Base branch (1.99.0).** Before offering the choices, when HEAD is a base branch and anything staged is implementation code, read [references/base-branch.md](references/base-branch.md): the prompt becomes `Commit on a work branch?`, and nothing is committed on the base, even with `commit now`; `new branch` answers it.

## When they pick `change`

Read [references/change.md](references/change.md). Redraft or edit, show the new blocks, then the same choices; no commit in that turn.

## When they pick `commit`

Read [references/commit.md](references/commit.md) for the commit steps, the pull, and the Next line. Do not open it on `copy`, `change`, or `stop`. `commit now` reads it after the blocks are shown.

## Added lines

The final message is exactly what this skill drafted. Any other line: read [references/added-lines.md](references/added-lines.md). Strip once by amend when HEAD is ours and unpushed; never loop.

## Hard rules

- Never offer commit/copy/change before Summary/Description exist. After they exist, show the blocks, then the choices with **`commit` first**.
- No commit until `commit` (or an unambiguous “commit this message now”) **after** they have seen the current blocks.
- `copy` never runs `git commit`.
- The committed message is exactly the drafted Summary + Description, including a trailing work-item mention. Added lines: [references/added-lines.md](references/added-lines.md).
- Do not install a hook to enforce the work-item line. Do not block the commit when `work-item.md` is missing. The only hook is the trailer hook, after `strip trailers`.
- Do not change product files except the persist rules the draft skill already writes, and the trailer hook and its saved answer (`.githooks/commit-msg`, `trailer-hook` rule). Cursor: `.cursor/rules/draft-commit-style.mdc` or `.cursor/rules/draft-commit-gitlog.mdc`. Claude Code project: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md`. Claude Code user: `~/.claude/rules/draft-commit-style.md` or `~/.claude/rules/draft-commit-gitlog.md`.
- Never commit implementation code on a base branch ([references/base-branch.md](references/base-branch.md)).
- Never push and never rebase. Do not open a PR. This run makes at most two commits: the drafted commit, and one merge commit when the branch was behind. Do not commit a notes index rebuild on its own. After a successful commit, the Next line follows run-ending.md. Do not invoke the command it names.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
