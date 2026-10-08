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

## Check first

The org and the project come from `docs/environments/marks.md`, or from the Azure DevOps URLs in `docs/system/repos.md`. The command checks that `az` works, including the default install paths, and that the project has the Feature work item type. If the type is missing, it says so and stops. If `az` fails, it states the issue, suggests a fix such as `az login`, and offers a skip. It does not install `az` and it does not log in.

## Pick, preview, then send

The user sees the candidate list and picks one or more by number, or all. Each pick is shown as the Feature form: title, State New, Area default, Value area Business, Iteration and Priority blank, Target Date only when the spec states it, tags for the slice name and the code repos it touches, a description that stands alone, and acceptance criteria only from the spec’s checks. Acceptance stays blank when the spec has none.

Nothing sent to Azure Boards mentions the repo that holds the specs. No spec path, no link to that repo, no kit name, and no skill name. An `AB#` mention that already exists in a code repo stays as it is.

The preview is not edited in place. A change goes into the spec first through `/crav1-add-to-spec`, and the preview is rebuilt from the spec.

The form is labelled **Create** or **Update #<id>**. An update shows what would change. The `az` command is not shown. Create or update runs only after the user says yes, one at a time or all of the reviewed picks together, because it goes out in the user’s name.

## What it writes

A new id is one line in that spec’s `work-item.md`, with the milestone or slice label. An item with no spec gets a row on `## No spec yet in ADO` in `docs/system/landscape.md`: id, title, and date. When a spec is made later, the id moves into that spec’s `work-item.md`. The command reports what was created and what was updated. It does not commit.
