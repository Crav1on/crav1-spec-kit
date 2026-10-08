---
name: crav1-feature-candidates
description: >-
  List Feature candidates from the landscape, the specs, research, and
  sources. One dated milestone or slice is one candidate. Read only.
  Write nothing unless the user asks for a file. A target date only when
  the docs state it. Later skill. Not a starter option. Also called by
  /crav1-specs-to-ado.
disable-model-invocation: true
icon: list
color: cyan
---

# Feature candidates

You list the work that could become an Azure Boards Feature. You read. You write nothing unless the user asks for a file.

Command: `/crav1-feature-candidates`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Other skills do not run this one, except `/crav1-specs-to-ado`, which runs this command and uses the list. Spark, specify, plan, and verify do not run it. It is not started automatically.

This command does not call Azure DevOps. It does not run `az`. It does not create a work item. It does not edit a spec, `docs/system/`, or `work-item.md`.

## Read

Read all of these when they exist. Skip `docs/specs/_template/`.

- `docs/system/landscape.md` — the feature index and its statuses, `## Ideas`, `## Way of working`, and code with no slice (`## Code with no slice` or the same note under another heading). Also the `## No spec yet in ADO` table when that heading is there.
- `docs/system/repos.md` and `docs/system/glossary.md`.
- Every `docs/specs/<slug>/spec.md` — milestones, slices, open questions, and actions.
- `plan.md`, `tasks.md`, and `verify.md` in that folder when they exist.
- `docs/research/` and `docs/sources/`.
- Each spec’s `docs/specs/<slug>/work-item.md`.

A fact from `docs/research/` or `docs/sources/` carries the folder or file it came from, in the chat block. A glossary row is a word. It is not a candidate. A constraint is not a candidate. `## Way of working` is a candidate only when it names a piece of work that has no spec. A practice with no piece of work stays out of the list.

Do not invent a fact the files do not state. A meaning the glossary marks `to be researched` stays that way. Do not expand it.

## What is one candidate

One row is one candidate. A spec folder is not one row when it holds several dated milestones or slices.

- **Dated milestone or slice.** Each dated milestone or slice inside a spec is its own candidate. The date is a calendar date the docs state for that milestone or slice.
- **Undated spec with open work.** A spec with no dated milestone or slice, and with open work, is one candidate. Open work is an unchecked acceptance line, an open action, an unchecked task, or a goal the spec does not mark done.
- **Questions only.** A spec whose only open work is open questions is one candidate. The Spec cell is `questions only (<slug>)`. The description includes those questions so they can be handled in the Feature discussion.
- **No spec yet.** An item with no spec, from `docs/sources/`, from the landscape (Ideas, a piece of work under Way of working, or code with no slice), or from `docs/research/` when that note names work no spec covers, is one candidate. The Spec cell is `no spec yet`.
- **Skip.** Skip a spec that is done or retired and has nothing open. Done or retired comes from the feature-index Notes, or from the spec when it says done or retired. Nothing open means no open question, no unchecked acceptance line, no open action, and no unchecked task. A done or retired spec that still has something open stays on the list.

A source folder or research note that a spec already cites belongs to that spec’s candidate. It is not a second `no spec yet` row. Say where the fact came from in the block.

Do not drop a candidate to keep the list short.

## Target date

Give a target date only when the docs state it. The cell is the date and where it was stated (the file and the heading). A `Synced at` date, a source-folder date, a git date, and a “last updated” date are not a target date. The words have to say it is the target, the milestone date, or the due date.

Never infer a date. An undated candidate has an empty target-date cell.

## Already in ADO

Show an id only when one is recorded.

- A spec candidate uses the line in that spec’s `work-item.md` whose label matches the milestone or slice. The line format is [work-item-mention.md](../crav1-draft-commit-message/references/work-item-mention.md) (plugin: sibling `skills/crav1-draft-commit-message/references/work-item-mention.md`). A file with one unlabeled line is that spec’s id. Several lines and no matching label: the cell says the ids that are recorded, and the block says the label did not match. Do not pick one.
- A `no spec yet` candidate uses the `## No spec yet in ADO` row when the title matches that row. A different title is not a match. Do not guess. A row whose cells are all empty is the template placeholder. It is not an id.

This command does not look the id up in Azure Boards.

## Order

Dated candidates come first, earliest date first. The same date keeps the order the docs listed them.

Undated candidates follow. Leave their order as the docs listed them. The block says the user’s team prioritizes them. Do not rank them.

## Output

The chat list, and the list handed to `/crav1-specs-to-ado`, is this table and then one block per row.

| # | Title | Target date | Spec | Already in ADO |
| --- | --- | --- | --- | --- |
| 1 | Short title | 2026-11-01 (`docs/specs/<slug>/spec.md`, Milestones) | `<slug>` | 52 |

Title is short, in the style of an Azure Boards title: the milestone, slice, or item name the docs use. Do not prefix it with “Feature”. Do not put a spec path in the title.

Spec is the slug, `no spec yet`, or `questions only (<slug>)`.

Already in ADO is the recorded id, or empty.

Under the table, one block per row:

- **Description.** Two to four sentences that stand alone. Cover the goal, the status, and what is open, using only words the docs state. When the source is thinner than two sentences, use only what it states. Do not add filler. A fact from research or sources names that folder in this block.
- **Open blockers and questions.** The open questions, actions, and unchecked work the docs state. Questions-only rows list the questions here and in the description. When none are written, say none are written down.
- **Order.** `dated, <date>` or `undated. The user’s team prioritizes this.`

No invented facts. Do not turn a guess into a row.

When the list is empty, say so. Do not invent a candidate.

## File

Write a file only when the user asks for one. Write the list already shown. Use the path they name. When they ask for a file and name no path, ask where. Options only. Do not commit. Do not write a spec or a landscape file from this command.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-specs-to-ado`, `/crav1-ado-to-specs`, `/crav1-add-to-spec`, or `/crav1-finalize-commit`. Naming `/crav1-specs-to-ado` as the command that sends a picked row to Azure Boards is allowed. Do not run it.
