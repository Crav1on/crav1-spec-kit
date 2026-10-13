# From specs to Azure Boards

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user wants Azure Boards Features from the specs.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

The list comes from [Feature candidates](from-feature-candidates.md). Reading a Feature back is [From Azure Boards to specs](from-ado-to-specs.md).

## First prompt

New chat.

```text
/crav1-specs-to-ado
```

That slash command *is* the prompt.

## Steps

### Check first

The org and the project come from `docs/environments/marks.md`, or from the Azure DevOps URLs in `docs/system/repos.md`. The command checks that `az` works, including the default install paths, and that the project has the Feature work item type. If the type is missing, it says so and stops. If `az` fails, it states the issue, suggests a fix such as `az login`, and offers a skip. It does not install `az` and it does not log in.

### Work item homes

The specs repo is the source of truth and is not tied to any tracker. Each implementation repo has its own work item home, written in the **Work items go to** column of `docs/system/repos.md` as `ADO: <org>/<project>` (`Jira: <project>` is reserved for later; nothing is built for Jira yet). One home can hold one or many repos. The specs repo never has one.

The first time a command needs a repo's home, it asks: the ADO project the repo lives in (suggested), any other project `az` can read, **same for all N new repos**, or a typed answer. A run with no window uses the two-pass questions file. The cell is written only after that answer, never silently. Change it by editing the row.

A spec whose repos are in several homes gets one Feature in each home, each holding only its own repos' tasks, each previewed and sent on its own yes. In one org they are linked to each other; across orgs each mentions the other in plain text.

### Pick, preview, then send

The user sees the candidate list and picks one or more by number, or all. Before the form, the command reads the project's Feature fields. When that type has Acceptance Criteria, the spec's checks go there. When it does not, the checks go in the Description as an Acceptance checks numbered list, and the preview says so in one line. A failed field read states the issue, suggests a fix, and offers a skip. It does not guess.

Each pick is shown as the Feature form: title, State New, Area default, Value area Business, Iteration and Priority blank, Target Date only when the spec states it, tags for the slice name and the code repos it touches, and a description that stands alone. The checks are the spec's checks and nothing else. Acceptance stays blank when the spec has none. The same field rule applies on an update, so a re-run moves checks that were stored off the form into the Description.

Nothing sent to Azure Boards mentions the repo that holds the specs. No spec path, no link to that repo, no kit name, and no skill name. An `AB#` mention that already exists in a code repo stays as it is.

The preview is not edited in place. A change goes into the spec first through `/crav1-add-to-spec`, and the preview is rebuilt from the spec.

The form is labelled **Create** or **Update #<id>**. An update shows what would change. The `az` command is not shown. Create or update runs only after the user says yes, one at a time or all of the reviewed picks together, because it goes out in the user’s name.

## What gets written

After a Create, writing the new id is required. A spec gets one line in that spec’s `work-item.md`, with the milestone or slice label and its home: `Work item: 52 — October billing (ADO: contoso/bc-operations)`. Older lines without the home are read as the org and project in `docs/environments/marks.md` and get the tag on the next write, without a question. An item with no spec gets a row on `## No spec yet in ADO` in `docs/system/landscape.md`: id, title, and date. When a spec is made later, the id moves into that spec’s `work-item.md`. The command names the file it wrote. That file is not committed yet and must be committed. Without it a later run offers Create again and would make a duplicate. If the write fails, the command says so and prints the line to add. The command reports what was created and what was updated. It does not commit. It names `/crav1-finalize-commit` and does not run it.

## After

Commit the file that holds the new id, so a later run does not offer Create again:

```text
/crav1-finalize-commit
```

Send that spec's tasks as child work items of the Feature with [From tasks to Azure Boards](from-tasks-to-ado.md).

Reading a Feature back onto the specs is [From Azure Boards to specs](from-ado-to-specs.md).

Reference page: [specs-to-ado](reference/skills/crav1-specs-to-ado.md)
