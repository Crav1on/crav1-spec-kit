---
name: crav1-finalize-commit
description: >-
  Always drafts first, then offers commit / copy / change / stop.
  `message only` drafts with no commit (same as copy). Replaces
  draft-commit-message (its rules are kept as a branch).
  `commit now` commits without the choice; `crav1` or `git log` sets
  the style. Finalize a commit: draft the Summary and Description, then
  offer git commit first, then copy / change / stop, with the CRAV1 style vs
  git log question in the same prompt when no style rule is saved. Wording is shown before those choices. Use when
  they want to change the message or actually create the commit, or
  /crav1-finalize-commit. Does not push. Does not commit until they pick
  commit. Paste-only: `message only`. Keeps a trailing
  work-item mention through the HEAD check and the strip of any trailer
  it did not write. Offers once per repo a shared .githooks
  commit-msg hook that strips known tool trailers. After the commit it fetches; when behind it pulls
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

Order (1.89.0): (1) generate and show Summary/Description, in the recommended style when no persist rule is saved, (2) then one prompt: the choices with **`commit` first** (top of the questions tool), then copy / change / stop, plus the style question when no persist rule is saved. There is no style menu before the draft.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Commit or message: `commit` / `commit now` / `message only` (draft, show, done: the same as `copy`, no git commit).
- Style: `crav1` / `git log`.
- Trailer hook: `strip trailers` / `keep trailers`.
- Pull: `pull` (1.81.0) runs the pull path with no commit first.

`commit now`, and `commit` typed in the invocation (1.76.1): draft, show the paste blocks, then commit with no choice question. When `agent-tools/` or build output is in the file set, warn and offer the normal choices instead.

When the invocation contains one of these words (for example `/crav1-finalize-commit commit`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

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

Trailer hook (1.90.0): when no answer is saved and `.githooks/commit-msg` is missing or not turned on, the same prompt adds `Strip tool trailers on every commit for this repo?` (`strip trailers` / `keep trailers`), asked once per repo. A teammate with the hook but no config gets the config line without a question. Read [references/trailer-hook.md](references/trailer-hook.md).

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
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output. After `strip trailers` in this run, also stage the new hook and its project rule by path, and nothing else unstaged ([references/trailer-hook.md](references/trailer-hook.md)).
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
- The committed message is exactly the drafted Summary + Description, including a trailing work-item mention. Added lines: [references/added-lines.md](references/added-lines.md).
- Do not install a hook to enforce the work-item line. Do not block the commit when `work-item.md` is missing. The only hook is the trailer hook, after `strip trailers`.
- Do not change product files except the persist rules the draft skill already writes, and the trailer hook and its saved answer (`.githooks/commit-msg`, `trailer-hook` rule). Cursor: `.cursor/rules/draft-commit-style.mdc` or `.cursor/rules/draft-commit-gitlog.mdc`. Claude Code project: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md`. Claude Code user: `~/.claude/rules/draft-commit-style.md` or `~/.claude/rules/draft-commit-gitlog.md`.
- Never push and never rebase. Do not open a PR. After a successful commit, one optional line may name `/crav1-open-pr`. Do not invoke it.
