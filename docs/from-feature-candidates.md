# Feature candidates

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user wants a list of work that could become an Azure Boards Feature.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

The command writes nothing unless the user asks for a file. It does not call Azure Boards. `/crav1-specs-to-ado` runs it when that command needs the list.

## First prompt

New chat.

```text
/crav1-feature-candidates
```

That slash command *is* the prompt.

## What it reads

`docs/system/landscape.md` (the spec index and its statuses, Ideas, Way of working, and code with no slice), `docs/system/repos.md`, the glossary, every `docs/specs/<slug>/spec.md`, and `plan.md`, `tasks.md`, and `verify.md` where they exist. It also reads `docs/research/` and `docs/sources/`, and each fact from those folders is labelled by where it came from. It reads each spec’s `work-item.md` and the landscape table `## No spec yet in ADO`.

## What one row is

A dated milestone or slice is one candidate. An undated spec with open work is one candidate. A spec that holds only open questions is marked `questions only`, and the questions are in the description so they can be handled in the Feature discussion. An item with no spec, from sources, the landscape, or code with no slice, is marked `no spec yet`. A spec that is done or retired, with nothing open, is skipped.

A target date appears only when the docs state it, and the list names the source. The command does not infer a date. A recorded id is shown. Dated rows are ordered by date. Undated rows are left for the user’s team to prioritize.

## What the user sees

A numbered table: title, target date and its source, spec (or `no spec yet` or `questions only`), and the id already recorded. Under it, a short block per row: a description that stands alone, the open blockers and questions, and the order. The description does not invent facts.

Sending a row to Azure Boards is [From specs to Azure Boards](from-specs-to-ado.md).
