# What's known about one thing

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user asks about **one feature, slice, resource, or not-yet-feature**. Status and what is pending are this command. The answer comes from the specs first.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

[Explain](from-explain.md) (`/crav1-explain`) reads `docs/system/` first. When the picture has nothing on the question, it quotes the first paragraph of a matching spec, labelled as coming from the spec, and names this command. It does not run this command. This command is the one feature. It reads the specs first.

The command writes nothing. It does not run another skill. It may name one.

## First prompt

New chat. Name the thing, or `@` a spec folder or a code folder.

```text
/crav1-whats-known-about

What's the status of <the feature, slice, or resource>? What's pending?
```

One folder:

```text
/crav1-whats-known-about
@docs/specs/<slug>/
```

That slash command *is* the prompt.

A name matches first as written (`fn-market-data`, a slug, a title). A sentence or two is matched on its key words. An `@` keeps the search inside that path. A focus such as "just the security bits" or "only what's pending" still runs the full read. The answer shows only those sections.

If the message has no name, no sentence, and no `@`, the command stops. Options only. It does not pick a thing.

Pasted minutes go to `/crav1-meeting-to-specs`. A long dump goes to `/crav1-match-dump-to-specs`. This command stops and names that one. It does not run it.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Question | A name, a sentence or two, an `@`, or a focus | Stops when nothing was named. Does not scan the repo to pick a thing |
| Match | — | One pass. Exact name first, then key words. Spec titles and Match quotes weigh highest. One winner, or a list to choose from |
| Slice | Read the answer | The spec, the plan, the tasks, Match, and open questions. The path is named |
| No slice | Read what is known | Repo, code, and environment notes. A candidate slice. Names spark, ideas, or intake. Does not run it |
| Live | Yes or no when a resource is prod-only | Azure settings and recent changes. Azure DevOps work items, open pull requests, and branches. Each fact is a live read. Never data |
| Live failed | Retry or Skip | One prompt. Skip is the repo-only answer, with why the live checks did not run |
| Stop | Glance | Writes nothing. Does not start Specify, Plan, or Build |

Two or more close hits: one line each, then which. It does not guess.

A code-only hit, with no spec and no architecture note, says what the code shows and fills in Unexplained.

## What gets written

Nothing. The answer stays in the chat.

No spec edit. No `plan.md`. No `tasks.md`. No marks. No application code.

The answer leaves out an empty section. It does not pad. A guess is labeled `(inference, not in the docs)`.

## After

When there is no slice, the answer names one next command. This command does not run it.

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Several features, or mixed files: `/crav1-intake-to-specs`

When nothing is written down, it names those three.

Production follows `/crav1-environment-read`: shape and connections only, after the same yes or no. A no leaves that resource unread. This command does not run the environment read.
