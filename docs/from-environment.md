# From a named host

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user names a **host** and wants that host’s non-prod environments read. Examples: Azure, AWS, Google Cloud. This command is a starter option. Asking for startup options names it and does not run it. It still runs only when the user names the host. Naming production, prod, or live stops.

This is cross-cutting. It is not a lane. It does not guess the host. It never reads production. One pass reads every non-prod environment. Each seen line keeps its own environment, such as `Seen in Azure dev.` or `Seen in Azure test.` Each host has its own reader. A host with no reader stops and says so. It does not pretend to read it. This build has readers for Azure, AWS, and Google Cloud. Any other named host stops with no reader. Azure DevOps, GitHub, and CI are not read. If the CLI is missing, or the login is missing, the stop names which one and points at the install page or the login command. The skill does not install the CLI and does not log in.

The user names the host, not the subscription, the account, or the project. Marks come from the name, the group, the tags, and `docs/environments/marks.md` when that file exists. The line format is [environments-marks.md](environments-marks.md). Non-prod words are dev, development, test, testing, stage, staging, uat, and qa. Pre-prod is read for shape and connections only, after one yes. A resource marked both non-prod and production by different sources is shared with prod and uses that same yes. A resource whose only mark is production is skipped and listed as skipped. What is still unmarked can be marked from shown evidence, then from a group suggestion, then by the user. A similar name is not evidence.

Cloud commands stay read-only. The only file this command writes is `docs/environments/marks.md`, and only by appending a line the user confirmed. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment. It is not marked as something the code shows. It does not become a link unless the environment shows the connection. A trigger is a connection. The line shows what starts the work, what it runs, and the schedule. It does not show a payload or a secret.

After that read, and before any section, the command can look inside a database or storage. It asks first. A no leaves them unopened. SQL is metadata only: schemas, names, columns, keys, procedure and function names, and jobs or triggers when they can be reached. Storage is structure only: containers or buckets, prefixes to depth 2, public or private access, lifecycle, versioning, soft delete, and what points at it. It never reads a row or a blob, and it never reports a file count or a size. It never prints a connection string, a key, or a secret. Production is never opened. Pre-prod and shared follow the yes already given and stay shape and connections only. When the databases have no clear environment, it says there are no clear database environments, then asks whether the environments are in the same database, then whether to read the schema. Before that second question it says how to reach the database and how much setup is needed. The same kind of explanation comes before the storage question. `sqlcmd` is optional and is not installed by this command. The command does not create a login, a firewall rule, a role, or a key. If access is missing, it stops that look-inside and names the gap. A schema or a prefix is evidence only when the whole-word token rule matches. What it found joins the sections that already exist and says it was seen in that environment.

Confirmation is one section at a time. Each section has its own question and its own answer. Nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system` through `/crav1-keep-current`. Architecture facts go to `docs/architecture/spec.md` through `/crav1-repos-to-spec`. A slice Match already owns goes on that feature spec through `/crav1-add-to-spec`. A left-out line the environment now shows comes off `docs/architecture/left-out.md`. Lines that are already there are not rewritten. This command does not start Specify, Plan, or Build.

`/crav1-pipeline-environments` reads Azure DevOps pipeline definitions and appends confirmed lines to the same marks file. Walkthrough: [from-pipeline-environments.md](from-pipeline-environments.md). This command does not run it.

This is not [named repos](from-repos.md) (`/crav1-repos-to-spec`). That command reads code. This command reads a host.

## First prompt

New chat. Not the host plan UI.

Name the host in this message.

```text
/crav1-environment-read

Azure.
List every non-prod environment. Skip production. Do not guess the host.
```

That slash command *is* the prompt.

If the message names no host, the command stops. It does not pick Azure. If the message names production, prod, or live, the command stops. If the message says Azure dev, the pass still reads every non-prod environment.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Host | Named the host, such as Azure | Stops when the host is missing. Does not guess. Naming production, prod, or live stops. Does not ask dev or test |
| Reader | Azure, AWS, and Google Cloud each have a reader. Another host does not | A host with no reader stops. A missing CLI or login is named. Does not install or log in. Does not read Azure DevOps, GitHub, or CI |
| Marks | — | Name, group, tag, then `docs/environments/marks.md`. One pass for every non-prod environment. Production-only is skipped. Disagreeing sources are shared with prod |
| Evidence | — | Still unmarked, strongest first: a connection, a deployment name, then Bicep, ARM, or Terraform. A similar name is not evidence |
| Pre-prod and shared | Yes or no | One question, before those resources are read. Yes is shape and connections only. No lists them as not read |
| Group and leftovers | Accept, mark, leave, or stop | A group suggestion can be accepted. Leftovers can be left unread, stopped, or marked per resource or per group |
| Look inside | Yes or no, after the access explanation | SQL metadata, then storage structure. No clear database environment is asked first. A no does not open it. Production is never opened. Missing access is named |
| Sections | Answer one section, then the next | Skipped, seen, links (including triggers), system, architecture, Match, left out. Look-inside facts join those sections. Every item stays listed |
| Owner | Glance | The skill that owns the other file adds only what is new. This command appends confirmed marks and does not write those other files |
| Stop | `/crav1-finalize-commit` if a file changed | Does not plan, implement, or commit. Does not start Specify, Plan, or Build |

## What can change

`docs/environments/marks.md` can gain a line the user confirmed. The folder is created only then. An existing line stays as it is.

Nothing else changes until a section is confirmed and the owner adds a new line.

`docs/system` changes only through `/crav1-keep-current`, and only when that folder is already there. `docs/architecture/spec.md` and `docs/architecture/left-out.md` change only through `/crav1-repos-to-spec`, and the spec is not created from the environment. A feature spec changes only through `/crav1-add-to-spec`, and only for a slice Match already owns.

A new line says it was seen in that environment. A shared line keeps `shared with prod`. A pre-prod line stays shape and connections only. A line that is already there stays as it is.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the new lines in git. No push. This command does not commit for you. It does not start Specify, Plan, or Build.
