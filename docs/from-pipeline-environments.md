# From Azure DevOps pipelines

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user names **Azure DevOps**, the org, and the project, and wants environment marks taken from the release pipelines. A pipeline name is optional.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

The command reads pipeline definitions. It lists and shows with `az pipelines` and `az devops`. It does not run a pipeline. It does not read builds, logs, test runs, or boards. The stage name gives the environment, with the same whole-word rule as `/crav1-environment-read`. A deploy step marks the resource it names. The resource group is context on that line. The rest of the group is not marked.

The line format is [environments-marks.md](environments-marks.md). There is no `shared` word. A resource that both a non-prod stage and a production stage deploy is one line per stage. The next `/crav1-environment-read` treats that disagreement as shared.

If `az` is missing, the `azure-devops` extension is missing, or there is no login, the stop names which. The install page and `az extension add --name azure-devops` are the pointers. The login commands are `az login` and `az devops configure --defaults`. The skill does not install and does not log in.

## First prompt

New chat. Name Azure DevOps, the org, and the project. Name one pipeline only when that is the one to read.

```text
/crav1-pipeline-environments

Azure DevOps. Org: <org>. Project: <project>.
Read the pipeline definitions. Do not run a pipeline. Do not guess the org.
```

That slash command *is* the prompt.

If the message leaves out Azure DevOps, the org, or the project, the command stops. It does not pick an org. Options only. It does not ask for a typed path.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Pointer | Named Azure DevOps, the org, and the project | Stops when one of those is missing. Does not guess. A pipeline name is optional |
| CLI | `az` and the `azure-devops` extension, already logged in | Names whichever is missing. Does not install or log in |
| Definitions | — | YAML stages and classic release stages. List and show only. Secrets stay unprinted |
| Cases | Read every item | One environment, shared, or unclear. A shared resource is two environments, one line each. Unclear proposes no mark |
| Sections | Answer one section, then the next | Every item stays listed. Only a confirmed line is appended |
| Stop | `/crav1-environment-read` next | Does not run that command. Names `/crav1-finalize-commit` when a file changed. Does not commit |

## What gets written

`docs/environments/marks.md` can gain a line the user confirmed. The folder is created only then. The source is `pipeline <name>, stage <stage>`. An existing line stays as it is. A line that disagrees is shown and not rewritten.

Nothing else is written. No `docs/system`. No architecture spec. No feature spec. No left-out file.

## After

The next command is the host read. This command does not run it.

```text
/crav1-environment-read
```

When a file changed and the user wants it in git:

```text
/crav1-finalize-commit
```

That puts the marks lines in git. No push. This command does not commit.
