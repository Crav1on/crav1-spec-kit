# From a named environment

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user names a **host and an environment** and wants that environment read. Examples: Azure dev, Google Cloud test, AWS dev. This command is a starter option. Asking for startup options names it and does not run it. It still runs only when the user names the host and a dev or test environment.

This is cross-cutting. It is not a lane. It does not guess the host. It never reads production. Each host has its own reader. The reader lists only what that named environment actually has. A host with no reader stops and says so. It does not pretend to read it. This build has readers for Azure, AWS, and Google Cloud. Any other named host stops with no reader. Azure DevOps, GitHub, and CI are not read.

The user names the environment, not the subscription, the account, or the project. The reader takes only a resource whose name, group, or tag says dev or test. Anything marked production is skipped and listed as skipped. A resource with no environment mark stops and asks. It is not read.

The skill only reads. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment. It is not marked as something the code shows. It does not become a link unless the environment shows the connection.

Confirmation is one section at a time. Each section has its own question and its own answer. Nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system` through `/crav1-keep-current`. Architecture facts go to `docs/architecture/spec.md` through `/crav1-repos-to-spec`. A slice Match already owns goes on that feature spec through `/crav1-add-to-spec`. A left-out line the environment now shows comes off `docs/architecture/left-out.md`. Lines that are already there are not rewritten. This command does not start Specify, Plan, or Build.

This is not [named repos](from-repos.md) (`/crav1-repos-to-spec`). That command reads code. This command reads an environment.

## First prompt

New chat. Not the host plan UI.

Name the host and the environment in this message.

```text
/crav1-environment-read

Azure dev.
List only what that environment has. Skip production. Do not guess the host.
```

That slash command *is* the prompt.

If the message names no host, the command stops. It does not pick Azure. If the message names production, the command stops.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Host and environment | Named both, such as Azure dev | Stops when the host or the environment is missing. Does not guess. Never reads production |
| Reader | Azure, AWS, and Google Cloud each have a reader. Another host does not | A host with no reader stops. Does not pretend to read it. Does not read Azure DevOps, GitHub, or CI |
| Marks | — | Takes a resource whose name, group, or tag says the named environment. Lists production as skipped. An unmarked resource stops the read and is not read |
| Sections | Answer one section, then the next | Skipped, seen, links, system, architecture, Match, left out. Every item stays listed. A fact says seen in that environment. A link only when the environment shows the connection |
| Owner | Glance | The skill that owns the file adds only what is new. This command does not write those files. A missing file is not created here. A slice Match does not own is not a new slug |
| Stop | `/crav1-finalize-commit` if a file changed | Does not plan, implement, or commit. Does not start Specify, Plan, or Build |

## What can change

Nothing, until a section is confirmed and the owner adds a new line.

`docs/system` changes only through `/crav1-keep-current`, and only when that folder is already there. `docs/architecture/spec.md` and `docs/architecture/left-out.md` change only through `/crav1-repos-to-spec`, and the spec is not created from the environment. A feature spec changes only through `/crav1-add-to-spec`, and only for a slice Match already owns.

A new line says it was seen in that environment. A line that is already there stays as it is.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the new lines in git. No push. This command does not commit for you. It does not start Specify, Plan, or Build.
