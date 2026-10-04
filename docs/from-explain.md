# From the system notes

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when **system notes already exist** under `docs/system/` and you want them read back. Spark, ideas, intake, and match write those notes. This command reads them.

This is cross-cutting. It is not its own lane. It does not start Specify, Plan, or Build. It does not guess. It does not write a second document. It does not teach.

The first answer is a short TLDR. Say longer and it goes one level deeper from the same notes. Point it at one part and the answer stays on that part. Ask whether the system can do something: yes points at the note that says yes, no points at the note that says no, and a thing the notes never mention is not written down.

The picture is the short description, the diagram, and how the parts connect. When that picture is older than the specs, the answer says so. The update is [keep current](from-keep-current.md) (`/crav1-keep-current`). This command does not run it.

## First prompt

New chat. Not the host plan UI.

Whole system:

```text
/crav1-explain
@docs/system/
```

One part:

```text
/crav1-explain
@docs/system/diagrams.md
```

Whether the system can do something:

```text
/crav1-explain

Can the system do <the thing>?
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Notes | — | Stops when `docs/system/` has no notes yet. Points at spark, ideas, intake, or match. Does not invent the notes |
| Answer | Read the TLDR | A few sentences from the short description, or from the part you named |
| Longer | Say longer | One level deeper from the same notes. The next longer opens one more heading. Stops when the notes have no further level |
| Can it | Ask the question | Yes and where, no and where, or that is not written down |
| Age | — | When the picture is older than the specs, says so and names `/crav1-keep-current`. Does not run it |

No notes in front of the command: it stops and points at spark, ideas, intake, or match.

## What gets written

Nothing. The answer stays in the chat.

No second document. No `plan.md`. No `tasks.md`. No application code. A missing `docs/system/` is not seeded here.

## After

When the answer says the picture is older than the specs:

```text
/crav1-keep-current
```
