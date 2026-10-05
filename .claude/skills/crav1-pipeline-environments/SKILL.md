---
name: crav1-pipeline-environments
description: >-
  Read Azure DevOps pipeline definitions for the org and project the user
  named. Optional: one pipeline. List and show only. Propose marks for the
  resources each deploy step names, from the stage name, using the same
  whole-word rule as /crav1-environment-read. Append confirmed lines to
  docs/environments/marks.md. Do not write docs/system, the architecture
  spec, feature specs, or left-out. Do not start Specify, Plan, or Build.
disable-model-invocation: true
icon: workflow
color: blue
---

# Pipeline environments

The user names Azure DevOps, the org, and the project. You read pipeline definitions and propose environment marks for the resources those definitions deploy. You do not guess the org or the project.

Command: `/crav1-pipeline-environments`.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

This is cross-cutting. It is not a lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This skill reads pipeline definitions. It does not read cloud resources. A stage whose name says production is still read. The Azure resource is not read.

The only file this skill writes is `docs/environments/marks.md`, and only by appending a line the user confirmed. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.

This is not `/crav1-environment-read`. That command reads a host. It does not read Azure DevOps. This command does not run it. After marks are confirmed, name it. Do not run it.

Commands and task inputs: [references/azure-devops.md](references/azure-devops.md) (drop-in: `.claude/skills/crav1-pipeline-environments/references/azure-devops.md`; plugin: this skill’s `references/azure-devops.md`).

## Start

Everything after `/crav1-pipeline-environments`, and every `@`, is the pointer.

The user names Azure DevOps, the org, and the project in that message. A pipeline name is optional. One named pipeline is the only pipeline you read. No pipeline name means every pipeline in that project.

Azure DevOps is the host for this command. Azure, AWS, and Google Cloud are not this host. A pipeline URL on `dev.azure.com` or `*.visualstudio.com` names Azure DevOps. Read the org and the project from that URL when they are in it. Read one pipeline from that URL when it names one definition. Do not treat a file path as the org or the project.

If they named no host, stop. Ask them to name Azure DevOps. Do not guess. Do not read.

If they named a host that is not Azure DevOps, stop. Say this command reads Azure DevOps. Do not pretend to read another host. Do not read.

If they named Azure DevOps and no org, stop. Ask them to name the org. Do not guess. Do not read a default from `az devops configure` or from the git remote. Do not read.

If they named the org and no project, stop. Ask them to name the project. Do not guess. Do not read.

Use the questions tool when it is available. Options only. Do not ask them to type a path. One question at a time. Do not ask the next question in the same questions call.

**No host named.** Options:

1. **Azure DevOps**
2. **I will name the host.**

Stop until they pick. **Azure DevOps** still needs the org and the project. Ask the org next. **I will name the host** waits for that name. If that name is not Azure DevOps, stop as above. Do not read between the answers.

**Host named, org missing.** Options:

1. **I will name the org.**

Stop until they name it. Do not offer a typed path. Do not list orgs. Do not read.

**Org named, project missing.** List projects with `az devops project list` after the CLI checks below. Options: one option per project the org shows, then **I will name the project.** List every project. Do not drop one to keep the list short. Stop until they pick. If the org shows no project, say so and stop. If the list fails, say the project list failed and stop. Do not guess a project.

**A named pipeline matches nothing.** List the pipelines the project shows. Options: one option per pipeline, with YAML, classic build, or classic release on the option. List every pipeline. Stop until they pick. A similar name is not a match. Compare without regard to case. If two pipelines share the name, list both with the id. Do not pick one.

## CLI

Follow [references/azure-devops.md](references/azure-devops.md). Use `az pipelines` and `az devops` to list and show only. Pass `--detect false` on every call. The org is `https://dev.azure.com/<org>` unless they already gave the full URL.

If the CLI cannot read, stop before any pipeline list. Name exactly what is missing. Do not invent a pipeline. Do not install. Do not log in. Do not run `az devops configure`.

- **`az` is not installed.** Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. This skill does not install it. Do not also name the extension or the login.
- **The `azure-devops` extension is not installed.** Say the `azure-devops` extension is not installed. The install command is `az extension add --name azure-devops`. Point at `https://learn.microsoft.com/azure/devops/cli/`. This skill does not install it. Do not also ask them to log in.
- **`az` has no login.** Say `az` has no login. The login command is `az login`. Also name `az devops configure --defaults`. This skill does not log in and does not run configure.
- **Azure DevOps rejects the login.** Say the Azure DevOps login is missing. The same two commands. Do not print a token. Do not ask for a PAT.

The command is not installed when it is not on the path. The extension is missing when `az extension show --name azure-devops` fails. The login is missing when `az` is installed and `az account show` fails. Check in that order. A later Azure DevOps call that fails on login, after those checks passed, uses the Azure DevOps login stop.

A failed pipeline list stops the read. Say the pipeline list failed. Do not invent a pipeline.

## What is read

Read definitions only.

- YAML pipelines, including stages, deployment jobs, and `environment:` names.
- Classic release pipelines, including stages. In a classic release the stage is the environment. Its name is the stage name.
- A classic build definition, when `az pipelines show` returns one. Read it for deploy steps. It often has none.

A YAML `template:` or `extends:` that points at another pipeline YAML file is part of the definition. Read that file. Do not read any other file in the repo. Do not clone. A missing template means that part is not read. Say so. Do not guess the targets inside it.

Do not read builds, runs, logs, test runs, boards, wikis, or artifacts. Do not queue, run, approve, edit, or trigger a pipeline.

## Stage name

The stage name gives the environment. Tokenize that name with the Marks rule in `/crav1-environment-read`. The words below are that rule. Do not add a word. Do not drop a word. Do not keep a different list.

Use the stage `displayName` when it is set. Otherwise use the stage identifier. A classic release environment name is the stage name.

Split the stage name on every character that is not a letter. Those letter runs are the tokens. Compare tokens without regard to case. `Dev`, `DEV`, and `dev` are the same word. The whole-word rule still holds.

| Tokens | Class | Environment on the marks line |
| --- | --- | --- |
| `dev`, `development` | non-prod | dev |
| `test`, `testing` | non-prod | test |
| `stage`, `staging` | non-prod | stage |
| `uat` | non-prod | uat |
| `qa` | non-prod | qa |
| `preprod`, or the neighboring tokens `pre` then `prod` | pre-prod | pre-prod |
| `prod`, `production`, `live` | production | prod |

A token is the whole word.

- `device` is not `dev`. `development` is dev.
- `protest`, `latest`, and `contest` are not `test`. `testing` is test.
- `backstage` and `staged` are not `stage`. `staging` is stage.
- `equation` and `equator` are not `uat`.
- `qatar` and `equal` are not `qa`.
- `preprod` is one token, and it is pre-prod.
- `pre-prod`, `pre_prod`, and `pre.prod` split into the neighboring tokens `pre` then `prod`. That pair is one pre-prod mark. The `prod` in that pair is not production. Order matters. `prod-pre` is production.
- `pre-production` splits into `pre` and `production`. `production` is production. That spelling is not pre-prod.
- `product` and `reproduce` are not `prod`.
- `live` is safe as a whole word, and it is production. `alive`, `lives`, `liveness`, `deliver`, `livestock`, and `livestream` are not `live`. `go-live` and `live-api` split to a `live` token and are production.

Inside one stage name, a production token wins over a non-prod token. That stage says prod. The pre-prod pair is the exception: that `prod` is not a production token.

A job name is not the stage name. A deployment slot name is not the stage name. A slot named staging does not make the environment stage.

Read the deployment job `environment:` name and show it on the item. It does not replace the stage name. When the stage name has a token and that `environment:` name has a different class, the resource is unclear. Say the two names disagree. Do not pick one. When the stage name has no token, the resource is unclear even if `environment:` has a token. Show that name in the reason.

## Targets

For each stage, find the Azure targets each deploy step deploys to. The reference file lists the task inputs. A step that is not a deploy step contributes no target.

Record, when the step shows them:

- the resource id, or the app name when no id is shown
- the resource group
- the service connection’s subscription id and name, when the endpoint shows them

The subscription is context on the item. It is not a fifth field on the marks line. Do not print a service principal secret, a password, a key, or a certificate. Do not print the endpoint JSON.

**Marks only what the step names.** A step that deploys into a resource group marks the app or the resource id that step names. It does not mark the other resources in the group. The group is the second field on that resource’s line. That field is the context `/crav1-environment-read` can use later for a group suggestion. A step that names a group and no app and no resource id marks nothing. List the group as context under that stage. Do not write a line whose first field is the group.

Prefer a resource id the step shows. Do not build an id from a subscription and a guessed provider. When the step shows an app name, the first field is that name.

An id and a name are the same resource only when the id’s last segment equals the name and the group is the same. Compare without regard to case. A similar name is not the same resource. `app` does not match `app-api`. When you cannot tell, list them as separate resources. Say they were not merged.

Follow a variable only when the value is plain. Plain means a value written in the pipeline YAML, a parameter default written there, or a variable group value whose `isSecret` is not true. A secret variable, a Key Vault link, a missing name, a cycle, or a runtime expression is unresolved. The target that depends on it is unclear. Do not print the secret. Do not print a plain value that is a connection string, a key, or a password. The resource name inside a plain value can still be the target.

An inline script names a target only when the script text shows an app name or a resource id as a plain value. A script file path is not read. Do not open that file. A target that exists only in that file is unresolved.

A Bicep file, an ARM template file, or a Terraform file is not the pipeline definition. Do not open it. Names that appear as task inputs still count.

## Cases

Group targets by resource across the pipelines you read. A resource is one of these cases.

**One environment.** Every stage that deploys it has the same class, or every stage is non-prod and the words differ. Propose one marks line per stage. Each line uses that stage’s environment word. Several non-prod words are not shared. Shared is the next case. Say on the item when the non-prod words differ. A resource that is only pre-prod is this case. A resource that is only production is this case. The line uses `prod`. Say that the next environment read treats a resource whose only mark is production as prod-only. That read asks once, with pre-prod and shared, before it reads shape and connections. This skill still does not read that Azure resource.

**Shared.** At least one stage is non-prod or pre-prod, and at least one stage is production. List the resource with both stages. The marks format has no `shared` word. Do not write one. Propose one line per stage, each with that stage’s own environment word, in the four-field format `docs/environments-marks.md` already defines. Say that `/crav1-environment-read` treats those lines as shared with prod. Pre-prod with production is this case, because that read already treats pre-prod and production as shared.

**Unclear.** The stage name has no environment word, the stage name and `environment:` disagree, or the target is an unresolved variable. List the resource with the reason. Propose no mark.

A group-only deploy stays with the case of its stage. It has no proposed line.

## marks.md

Path: `docs/environments/marks.md` in the project repo. The format is the four fields in `/crav1-environment-read` and in `docs/environments-marks.md`. Do not write the kit note into the project.

```text
<resource-id-or-name> | <group> | <environment> | pipeline <name>, stage <stage>
```

The second field is the group the step showed. Use `-` when the step shows no group. The source is `pipeline <name>, stage <stage>`. One line per stage. Do not put two stages in one source.

Create `docs/environments/` and `marks.md` only when the user has confirmed at least one line. Append those lines. Never rewrite an existing line. Do not append a line that is already there. Already there means the same resource and the same environment word. `development` on an existing line is the same word as `dev`. Compare the resource the way `/crav1-environment-read` matches: the id, or the name plus the group, without regard to case. List that item as already written. A confirm does not append it again.

When an existing line matches the resource and the environment class differs, show the existing line and the proposed line. Do not rewrite the existing line. A confirmed append leaves the existing line and adds the new one. Say that the next environment read treats that disagreement as shared.

A line the user did not confirm is not written. Unclear items write nothing.

## Sections

Show one section at a time. Each section has its own question and its own answer. Do not merge sections. List every item. Do not drop a resource, a stage, a group-context line, or an existing line to keep a section short.

Use only these sections, in this order. Do not invent another section.

**One environment.** Every resource in that case, the proposed lines, the group, and the subscription when it was shown. Group-only context for those stages is listed with no line. When none, the section says nothing is in this section.

**Shared.** Every shared resource, both stages, and the proposed lines. Say there is no `shared` word. When none, the section says nothing is shared.

**Unclear.** Every unclear resource and the reason. Say no mark is proposed. When none, the section says nothing is unclear.

Stop. Ask the section in front of you. Stop until that section has an answer. Append the confirmed lines from that section, then ask the next section. Do not ask the next section in the same questions call.

Use the questions tool when it is available. Options only. Put that section’s items in the question prompt.

**One environment or shared, when it lists proposed lines.** Options:

1. **Append every proposed line in this section.**
2. **Append none of this section.**
3. **I will edit this section.**

**One environment, when nothing is in it.** Options:

1. **Nothing is in this section.**
2. **I will edit this section.**

**Shared, when nothing is shared.** Options:

1. **Nothing is shared.**
2. **I will edit this section.**

**Unclear, when it lists resources.** Options:

1. **Leave every resource in this section unmarked.**
2. **I will edit this section.**

**Unclear, when nothing is unclear.** Options:

1. **Nothing is unclear.**
2. **I will edit this section.**

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not ask that section again. Sections already answered stay answered. A line they struck is not appended. A resource they add that no pipeline step names stays out. Say the pipeline does not name it. Omitting a listed item does not drop it.

An unclear confirm writes no line. Do not write `marked by the user` from this command.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-feature-branch`, `/crav1-environment-read`, or `/crav1-finalize-commit`.

Output only:

- Org, project, and the pipelines read (name and kind), or that the read stopped before a pipeline list
- Counts: one environment, shared, unclear
- Whether `docs/environments/marks.md` changed
- Next: `/crav1-environment-read` (do not run it). When a file changed, also name `/crav1-finalize-commit` (do not run it). When nothing was written, still name `/crav1-environment-read`, and do not name finalize-commit

## Hard rules

- Azure DevOps, the org, or the project missing: stop. Do not guess. Options only. Do not ask for a typed path.
- A pipeline name is optional. No name means every pipeline in the project. A name that matches nothing stops. A similar name is not a match.
- Use `az pipelines` and `az devops` to list and show only. `--detect false` on every call.
- Do not run, queue, edit, approve, or trigger a pipeline.
- Do not read builds, logs, test runs, boards, or repo files beyond the pipeline definition.
- Name the missing CLI, the missing extension, or the missing login. Do not install. Do not log in. Do not run `az devops configure`.
- The stage name gives the environment. Use the Marks words from `/crav1-environment-read`. Do not keep a different list.
- Mark only the resource the deploy step names. The group is context. Do not mark the whole group.
- A secret is never printed. An unresolved variable is unclear. No mark is proposed for unclear.
- The marks format has no `shared` word. Shared proposes one existing-format line per stage.
- Append only a line the user confirmed. Create the file only then. Never rewrite an existing line. A disagreement is shown and the existing line stays.
- Do not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.
- One section at a time. Every item stays listed.
- Do not start Specify, Plan, or Build. Name `/crav1-environment-read` and do not run it.

## Style

Be concise. Cite the pipeline, the stage, and the resource. Prefer the smaller fact. Do not fill a gap with a resource the step did not name.
