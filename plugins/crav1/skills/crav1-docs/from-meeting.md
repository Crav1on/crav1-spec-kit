# From a meeting to specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user has **minutes, a transcript, an email, or a chat thread** (a file, a paste, an export from a meeting tool, or a pasted team chat) and wants the decisions matched to specs that already exist. An email or a chat thread is accepted as well as minutes or a transcript.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. It does not run this command. The six starter options stay unchanged.

[Intake](from-intake.md) starts a landscape and new feature slugs from a dump. It does not match items against specs that already exist. [Add](from-add.md) takes one piece of new information for one existing spec. This command extracts many items, matches them, and hands one kept addition to add-to-spec.

When a kept addition quotes a mail, a transcript, a chat, a screenshot, or another original, the command writes that source under `docs/sources/YYYY-MM-DD-<slug>/`, with the original files and a `README.md`, following the imported-sources convention. It does not write the spec. It does not commit. The quote reaches the spec through `/crav1-add-to-spec`, and that spec's `Source:` and `Trace:` lines link to the folder. A leave, a dismiss, a kept new feature, and a kept bug do not write the folder.

Note is a fourth choice: `Note — keep it in the repo without tying it to a spec yet.` It writes `docs/notes/YYYY-MM-DD-<slug>.md` and one line on `docs/notes/index.md`. The quote stays verbatim. There is no question after Note about what kind of note it is. Note is the recommended answer when the item is worth keeping and is not a decision, a clarification, information, or an answer for an existing spec. Dismiss stays for a greeting, scheduling, and thanks. The command reads `docs/notes/` first. An item already noted is shown as already noted and is not written again. It does not commit the note. A note that quotes an imported source also writes that source folder.

## First prompt

New chat. Paste the minutes, transcript, email, or chat, or `@` the file.

```text
/crav1-add-to-spec
@<minutes, transcript, meeting tool export, email, or chat thread>

Extract what matters for features. Match it to the specs we already have. Do not write a spec. Do not commit.
```

That slash command *is* the prompt.

If the message has no input and no `@`, the command stops. Options only. It does not pick a file.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Input | Pasted or `@` a file | Minutes, a transcript, an email, or a chat thread. Stops when nothing was pointed at. Does not scan the repo. Does not guess |
| Kind and date | Glance | Kind from what the input shows: meeting, email, or chat. Date from the input. Asks once when the kind is not clear. Asks once when there is no date: give a date, or skip |
| Extract | Read the list | Requirements, decisions, changes, open questions, bugs, and information worth keeping that is not yet a spec. Each item is a quote. Speaker and time when the input shows them. Small talk is dropped |
| Match | Read every item | Addition, new feature, bug, or unclear. Every candidate spec stays listed. Skip `_template`. `docs/notes/` is checked first |
| Build state | Read the line | One `State:` line on each item that matches a spec, in the list and in the question. `Fits: none` has no state line |
| One at a time | Keep, leave, dismiss, or note | One item. The recommendation is on that question. Note is recommended when it is worth keeping and not for an existing spec. Dismiss is for noise, and for this run only |
| Keep | Glance | Addition goes through `/crav1-add-to-spec`. New feature or bug only names the next command |
| Note | Glance | Writes `docs/notes/` and does not ask what kind of note it is. Does not write a spec |
| Stop | Counts | Writes the source folder when a kept addition or a note imports a source. Does not write a spec. Does not commit. Does not start Specify, Plan, or Build |

## Build state

An item that matches an existing spec shows one line, `State: <state>.`, and a short reason that names the evidence. The same line is in the item block and in the keep, leave, dismiss, or note question.

| State | Meaning |
| --- | --- |
| built | The spec already says the item is present, or a checked task covers it |
| partly built | Part of it is covered. The reason names which part |
| planned | It is in `plan.md` or an open task, and it is not done |
| not built | The matched spec, plan, and tasks do not cover it |

An item with `Fits: none` has no state line.

The read is that slice’s `spec.md` (including `## Match`), then `plan.md`, then `tasks.md` checkboxes, then `verify.md` when that file is present. When those do not settle it, one read-only look at the code that spec or plan points to. No search of the codebase. A state from that code, or a state that is still uncertain, ends with `(inference, not in the docs)`.

The line does not change the options. It is not written. It is not part of the quote handed to `/crav1-add-to-spec`.

## What gets written

For a kept addition that imports a source, `docs/sources/YYYY-MM-DD-<slug>/`: the original files, unchanged except where the convention says otherwise, and a `README.md`. The README says what it is, the sender or the participants, the date and the time, and how it was converted. A mail is a `.eml` file with CRLF line endings kept. Each image inside that mail, inline or attached, gets the same four choices, asked once for the list. A binary file handed over on its own is still one of four choices, asked one file at a time. Personal details in the mail, in an image, and in converted text are flagged before the files are written. The command does not commit.

No `docs/system/`. No new spec folder. No marks. No dismissals file.

A kept addition is a quote on the existing `spec.md`, written by `/crav1-add-to-spec`. The handoff passes the kind, the date, and the source folder when one was written. The quote starts with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` Examples: `From email 2026-10-06.`, `From meeting.` The spec `Source:` and `Trace:` lines link to the source folder. One kind and one date apply to every item. The impact check still runs there. Other files change only when apply is picked.

A left item is not written. A dismissed item is not written. The state line is not written. The next run can offer a left or dismissed item again.

## After

When a kept addition or an answer changed an existing spec, the next steps follow the [New information on an existing slice](reference/workflow.md#new-info) route for that slug: `/crav1-tighten-spec` first, then `/crav1-resolve-open-questions`, then `/crav1-plan-from-spec` when the slice has a plan. This command names them and does not run them. Ask `/crav1-help next` for the full order with your slice's state.

A kept new feature names one next command. This command does not run it.

- One kept new feature that is one or two sentences: `/crav1-spark-to-spec`
- One kept new feature that is a pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Two or more kept new features: `/crav1-bundle-to-specs`

A kept bug names `/crav1-fix-bug`. This command does not run it.

When a file changed and the user wants it in git:

```text
/crav1-finalize-commit
```

That puts the spec lines, and any source folder this command wrote, in git. No push. This command does not commit.

Reference page: [add-to-spec](reference/skills/crav1-add-to-spec.md)
