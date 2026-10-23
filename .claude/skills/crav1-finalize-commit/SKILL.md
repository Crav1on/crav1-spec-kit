---
name: crav1-finalize-commit
description: >-
  Always drafts first, then offers commit / copy / change / stop.
  `message only` drafts with no commit (same as copy). Replaces
  draft-commit-message (its rules are kept as a branch).
  `commit now` commits without the choice; `crav1` or `git log` sets
  the style. Finalize a commit: CRAV1 style vs git log first if needed, then draft
  the Summary and Description, then offer git commit first, then copy /
  change / stop. Wording is shown before those choices. Use when
  they want to change the message or actually create the commit, or
  /crav1-finalize-commit. Does not push. Does not commit until they pick
  commit. Paste-only: `message only`. Keeps a trailing
  work-item mention through the HEAD check and the strip of any trailer
  it did not write. After the commit it fetches; when behind it pulls
  with a merge and fixes kit-file conflicts so no line is lost; `pull`
  does only that. Never pushes.
disable-model-invocation: true
icon: git-branch
color: green
---

# Finalize commit

## No opening question (1.83.0)

Always draft first. There is no question before the wording. The draft rules are the message only branch, [branches/message-only/BRANCH.md](branches/message-only/BRANCH.md), whose style, work-item mention, and work-item offer rules apply to every run.

First produce the Summary and Description. Then keep those two fields in play until they pick **commit**, **copy**, or **stop**.

Command: `/crav1-finalize-commit`.

Order: (1) style menu if no persist rule, (2) generate and show Summary/Description, (3) then the choices with **`commit` first** (top of the questions tool), then copy / change / stop.

At most 4 options per question; a fifth goes under Other.

When the message or the files make one option the better fit, list it first and end its label with ` (Recommended)`. Otherwise keep the order above with no label.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Commit or message: `commit` / `commit now` / `message only` (draft, show, done: the same as `copy`, no git commit).
- Style: `crav1` / `git log`.
- Pull: `pull` (1.81.0) runs the pull path with no commit first.

`commit now`, and `commit` typed in the invocation (1.76.1): draft, show the paste blocks, then commit with no choice question. When `agent-tools/` or build output is in the file set, warn and offer the normal choices instead.

When the invocation contains one of these words (for example `/crav1-finalize-commit commit`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

Headless or bot run with no choice word (no person in the chat to answer): draft, show the blocks, and end as `copy`. No git commit.

## Draft

Follow [branches/message-only/BRANCH.md](branches/message-only/BRANCH.md) for the first draft:

- Style menu or persist rule (`once` / `onward` / `log-once` / `log-onward`)
- Inspect staged first, else unstaged
- Output the **Summary** and **Description** paste blocks
- Work-item mention, when [work-item-mention.md](branches/message-only/references/work-item-mention.md) resolves one: one blank line, then that mention as the **last line** of the Description. Subject stays as drafted.

Do **not** run `git commit` in that step. Do **not** skip the paste blocks — they stay GitKraken-copyable on every turn. The mention is inside the Description fence, so a GitKraken paste includes it. A work-item hint stays after the fences.

Remember the intended file set (the paths the message describes). Warn if `agent-tools/` or build output is in that set.

## After every new wording (first draft or change)

They choose **after** the message exists, not before.

When the style is not settled, ask the CRAV1 style vs git-log question in the same questions call as the commit/copy/change choices (1.70.0), and draft in the recommended style; a different style answer redrafts before anything is committed.

On the turn that produces wording:

1. Finish the draft (git inspect, style already chosen).
2. Write the **Summary** and **Description** paste blocks into the user-visible reply. This is required. Do not skip it.
3. **Then** offer the choices (questions tool when available). The prompt is `Commit this message?`. The blocks are already in the reply above; do not repeat them in the prompt.

   Options, **in this order**: `commit` / `copy` / `change` / `stop`. **`commit` is always the first/top option** in the questions tool and in any bullet list.

Never call the questions tool (or any blocking choice UI) before step 2.

| Id | Choice | What it does |
| --- | --- | --- |
| `commit` | Create the git commit | Use the **current** Summary + Description. See below. **Always list this first.** |
| `copy` | Copy for GitKraken | Done. Same outcome as `/crav1-finalize-commit`. They paste Summary/Description. No `git commit`. |
| `change` | Edit or rewrite | They say what to change (summary, description, or both), or say rewrite for a new draft from the diff. See below. |
| `stop` | Abort | No commit. They can still copy the last blocks. |

If they named `copy`/`change`/`commit` **before** any wording exists, ignore it, draft, show blocks, then offer choices.

Do not invent extra options (push, amend, commit subsets they did not name). A push asked for after the commit is a **new** request.

## When they pick `change`

Read [references/change.md](references/change.md). Redraft or edit, show the new blocks, then the same choices; no commit in that turn.

## When they pick `commit`

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output.
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). The body is the Description paste, including a trailing work-item mention when the draft has one. Do not add `Co-authored-by`, `Made-with: Cursor`, or other trailers yourself. Do not drop the mention line.
4. Read `git log -1 --format=%B`. Compare to the drafted Summary + Description. The mention, when the draft has one, is the last line of that Description. A last line of `#<id>` or `AB#<id>` is the work-item mention, not an added line.
5. Show the new hash, subject, and `git status` short result.
5a. **Fetch and check (1.81.0).** Fetch. When behind the upstream, pull with a merge and resolve kit-file conflicts by the kit's rules; otherwise check any unpushed merge for lines either side added that the merge dropped. Read [references/pull.md](references/pull.md) for both. Never push; end with `Ready to push.`
6. If the message has any line that was **not** in the draft (a `Co-authored-by`, `Signed-off-by`, `Generated with` or other trailer from Cursor, Claude Code or another tool), read [references/added-lines.md](references/added-lines.md).
7. After the commit message is settled (including a one-time strip of added lines), one optional line and nothing more: Next (optional): `/crav1-open-pr` when you want to push and open the PR. Do not run that skill in this turn.
8. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks, **then** offer the choices again (`commit` still first). Do not name `/crav1-open-pr` on a failed commit.

Do not `git commit --amend` for wording tweaks unless they asked. Amending **only** to restore the drafted message (strip added lines) is allowed as below.

## Added lines

The final message is exactly what this skill drafted. Any other line: read [references/added-lines.md](references/added-lines.md). Strip once by amend when HEAD is ours and unpushed; never loop.

## Hard rules

- Never offer commit/copy/change before Summary/Description exist. After they exist, show the blocks, then the choices with **`commit` first**.
- No commit until `commit` (or an unambiguous “commit this message now”) **after** they have seen the current blocks.
- `copy` never runs `git commit`.
- The committed message is exactly the drafted Summary + Description. After `commit`, strip any trailer or line the draft did not have (Cursor, Claude Code, any `Co-authored-by` / `Signed-off-by`) once with amend when HEAD is ours and unpushed; do not fight a second inject—tell them to turn that attribution off. The amend keeps the drafted Description, including a trailing work-item mention.
- Do not install a hook to enforce the work-item line. Do not block the commit when `work-item.md` is missing.
- Do not change product files except the persist rules the draft skill already writes. Cursor: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md`. Claude Code project: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md`. Claude Code user: `~/.claude/rules/draft-commit-style.md` or `~/.claude/rules/draft-commit-gitlog.md`.
- Never push and never rebase. Do not open a PR. After a successful commit, one optional line may name `/crav1-open-pr`. Do not invoke it.
