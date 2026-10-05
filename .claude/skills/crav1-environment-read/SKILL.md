---
name: crav1-environment-read
description: >-
  Read the host the user named. Each host has its own reader. This build
  has readers for Azure, AWS, and Google Cloud. Another named host stops
  with no reader. Never production. One pass reads every non-prod
  environment. Pre-prod and resources shared with prod are shape and
  connections only, after one yes. After that read, and before any
  section, optional SQL metadata and storage structure, only when the
  user says yes. Never rows. Never blobs. Never production. Appends
  confirmed lines to docs/environments/marks.md. Does not write
  docs/system,
  docs/architecture/spec.md, feature specs, or
  docs/architecture/left-out.md. After the user confirms a section, the
  skill that already owns the file adds only what is new. A fact is seen
  in that environment. A link only when the environment shows the
  connection. Does not start Specify, Plan, or Build.
disable-model-invocation: true
icon: cloud
color: cyan
---

# Environment read

The user names the host at the start. You read every non-prod environment on that host in one pass. You do not guess the host. You never read production.

Command: `/crav1-environment-read`.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill. This command still runs only when the user names the host. Naming production, prod, or live stops.

This is cross-cutting. It is not a lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

Cloud commands stay read-only. This skill does not create, update, delete, deploy, start, stop, or set a cloud resource. It does not install a CLI. It does not log in. The only file this skill writes is `docs/environments/marks.md`, and only by appending a line the user confirmed. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. After the user confirms a section, the skill that already owns that file adds only what is new. A fact is marked seen in that environment. It is not marked as something the code shows. It does not become a link unless the environment actually shows the connection.

This is not `/crav1-repos-to-spec`. That command reads repos. This command reads a host. This is not `/crav1-match-to-specs`. Match needs a dump and writes one spec per slice. This command does not create a slug. This is not `/crav1-code-into-specs`. `/crav1-pipeline-environments` proposes pipeline lines for `docs/environments/marks.md`. This command does not run it and does not write those lines.

The host readers list a database and a storage account. They do not open them. After the first read, and before any section, this command can look inside. SQL metadata is [references/sql.md](references/sql.md). Storage structure is [references/storage.md](references/storage.md). Drop-in: `.claude/skills/crav1-environment-read/references/`. Plugin: this skill’s `references/`. Both run only when the user says yes. A no leaves them unopened. The first read does not list tables, columns, prefixes, or blobs as facts.

## Start

Everything after `/crav1-environment-read`, and every `@`, is the pointer.

The user names the host in that message. Examples: Azure, AWS, Google Cloud. They do not pick dev or test. The user names the host, not the subscription, the account, or the project.

If they named no host, stop. Ask them to name the host. An environment word is not a host. Do not guess. Do not pick a host because it has a reader. Do not read.

If they named production, prod, or live, stop. Say this skill never reads production. Do not list resources. Do not call a reader. A non-prod word in the same message does not make a production read safe.

If they named the host and also a non-prod word, such as Azure dev, do not stop and do not narrow the pass. Say once that this pass reads every non-prod environment. Then read.

If they named only an environment word and no host, stop. Ask them to name the host. Do not treat that word as the host. Do not read.

Use the questions tool when it is available. Options only. Do not ask them to type a path. One question at a time. Do not ask the next question in the same questions call.

**No host named.** Options:

1. **Azure**
2. **Google Cloud**
3. **AWS**
4. **I will name the host.**

Stop until they pick. A pick of Azure, Google Cloud, or AWS is the host. Do not ask dev or test. **I will name the host** waits for that name. Do not read between the answers. If that name is production, prod, or live, stop as above.

## Reader

Each host has its own reader. The reader lists what that host actually has, then the marks decide what is taken, skipped, or not read. A host with no reader stops. Say this host has no reader. Do not pretend to read it. Do not borrow another host’s reader.

This build has three readers.

- **Azure** — [references/azure.md](references/azure.md) (drop-in: `.claude/skills/crav1-environment-read/references/azure.md`; plugin: this skill’s `references/azure.md`).
- **AWS** — [references/aws.md](references/aws.md) (drop-in: `.claude/skills/crav1-environment-read/references/aws.md`; plugin: this skill’s `references/aws.md`). Amazon Web Services is AWS.
- **Google Cloud** — [references/google-cloud.md](references/google-cloud.md) (drop-in: `.claude/skills/crav1-environment-read/references/google-cloud.md`; plugin: this skill’s `references/google-cloud.md`). GCP is Google Cloud.

Check the host name before any read.

- **GitHub, CI, Azure DevOps, or Azure Pipelines** — stop. This skill does not read them. Do not pretend to. Do not treat Azure DevOps as Azure.
- **Azure** — follow the Azure reader. The host name is Azure, not Azure DevOps. The user names the host, not the subscription.
- **AWS** — follow the AWS reader. The user names the host, not the account.
- **Google Cloud** — follow the Google Cloud reader. The user names the host, not the project.
- **Any other named host** — stop. This host has no reader.

If the CLI is missing, or the login is not present, stop before any resource list. Name exactly what is missing. Do not invent a resource. Do not install the CLI. Do not log in.

- **`az` is not installed.** Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. This skill does not install it.
- **`az` has no login.** Say `az` has no login. The login command is `az login`. This skill does not log in.
- **`aws` is not installed.** Say `aws` is not installed. Point at `https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html`. This skill does not install it.
- **`aws` has no login.** Say `aws` has no login. The login command is `aws sso login` or `aws configure`. This skill does not log in.
- **`gcloud` is not installed.** Say `gcloud` is not installed. Point at `https://cloud.google.com/sdk/docs/install`. This skill does not install it.
- **`gcloud` has no login.** Say `gcloud` has no login. The login command is `gcloud auth login`. This skill does not log in.

The command is not installed when it is not on the path. The login is missing when the command runs and the reader’s identity check fails. If both are true, name the missing CLI. Do not also ask them to log in to a CLI that is not installed.

A failed resource list stops the read. Say the reader cannot list resources. An optional evidence command that fails means that evidence is absent. It does not stop the read.

## Marks

Four sources, in this order: the resource name, the group, the tags, then a matching line in `docs/environments/marks.md`. The file is used after name, group, and tag. It does not replace them. The reader file says what the name, the group, and the tag are on that host. Google Cloud has no resource group. That absence is not a mark. Do not infer a mark from the subscription, the account, the project, the region, or a neighbor. A similar name is not a mark.

Split name, group, tag key, tag value, and the environment field of a marks line on every character that is not a letter. Those letter runs are the tokens. Compare tokens without regard to case. `Dev`, `DEV`, and `dev` are the same word. The whole-word rule still holds.

| Tokens | Class | Environment on the Seen line |
| --- | --- | --- |
| `dev`, `development` | non-prod | dev |
| `test`, `testing` | non-prod | test |
| `stage`, `staging` | non-prod | stage |
| `uat` | non-prod | uat |
| `qa` | non-prod | qa |
| `preprod`, or the neighboring tokens `pre` then `prod` | pre-prod | pre-prod |
| `prod`, `production`, `live` | production | none (skipped, unless another source disagrees) |

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

Inside one source, a production token wins over a non-prod token. That source says prod. The pre-prod pair is the exception: that `prod` is not a production token.

Across sources:

- **Skipped.** The only environment class is production. List it as skipped: name, group, and the mark. Do not show the rest of the resource. A resource whose own name, group, or tag says prod, with no other source, stays skipped.
- **Shared.** One source says production and another source says non-prod or pre-prod. Treat it like pre-prod. Label it `shared with prod`. The line shows both sources, like `tag says dev; marks.md (pipeline X, stage Prod) says prod`.
- **Pre-prod.** A source says pre-prod, and no source says production. A non-prod token on another source does not make it a full read. The stricter class wins. Cite both sources.
- **Taken.** One or more non-prod environments, and no production or pre-prod class. The resource is read in full for those environments. Cite every source. One line can carry more than one `Seen in <host> <environment>.` when sources name different non-prod environments.
- **No mark.** No source has a token in the table. Do not read that resource yet. Evidence below may still mark it.

Do not read further properties on a resource that is still unmarked, except the private endpoint, VNet, or subnet id when testing connection evidence.

## marks.md

Path: `docs/environments/marks.md` in the project repo. The format note for people is `docs/environments-marks.md` in this kit. The skill defines the format here. Do not write the kit note into the project.

Each line has four fields, separated by ` | ` (space, pipe, space). Split on the first three separators only. The source is the rest of the line.

```text
<resource-id-or-name> | <group> | <environment> | <source>
```

- The first field is the resource id or the resource name.
- The second field is the group. Use `-` when the host has no group.
- The third field is one environment word. The same tokenizer maps it. `development` maps to dev. `pre-prod` and `preprod` map to pre-prod. `production` and `live` map to production.
- The source is `pipeline <name>, stage <stage>`, or `marked by the user`, or `marked by the user, suggested by group`.

A blank line is ignored. A line that starts with `#` is ignored. A line this skill cannot parse, or whose environment word is not in the table, is not used. List it as not used. Do not guess. Do not rewrite it.

A line matches a resource when the first field equals the resource id, or when the first field equals the name and the second field equals the group. Compare without regard to case. A similar name does not match. `app` does not match `app-api`. If a name and group match more than one resource, do not apply that line. List it as not used.

This skill creates `docs/environments/` and `marks.md` only when the user has confirmed at least one mark. It appends those lines. It never rewrites an existing line. It does not append a line that is already there. A second environment for the same resource is a new line.

Confirmed group suggestions use `marked by the user, suggested by group`. Marks the user names on the leftovers question use `marked by the user`. Prefer the resource id in the first field and the group in the second. Evidence marks are cited on the Seen line. They are not written to this file.

## Evidence

Before the leftovers question, the reader may mark a resource that is still unmarked. Use shown evidence only. Try the three kinds strongest first. The first kind that marks the resource wins. A weaker kind does not replace that environment. If a weaker kind says production, the resource is shared instead of a full read. Cite both. A similar name is not evidence. Cite the evidence on the line.

1. **A connection from a marked resource.** A setting on a taken non-prod resource that names this resource’s id or hostname, or the same private endpoint, VNet, or subnet. The environment is that marked resource’s environment. To test the network, the reader may read only the private endpoint, VNet, or subnet id on the unmarked resource. For a skipped production resource, the reader may read only those connection fields, to see if production also connects. Do not show the rest of that production resource. If a non-prod resource connects and a production resource also connects, the unmarked resource is shared. If only production connects, the mark is production and the resource is skipped. Do not use a pre-prod or shared resource as the source of this evidence.
2. **Deployment history, when the deployment that created it is named for an environment.** Azure: `az deployment group list` for a resource group the list already showed, then `az deployment operation group list` for the target resource id only. Do not print the request, the response, or outputs. AWS: CloudFormation stack name, from `aws cloudformation list-stacks` and `aws cloudformation list-stack-resources`, for a stack that still exists. Google Cloud: Deployment Manager deployment name, from `gcloud deployment-manager deployments list` and `gcloud deployment-manager resources list`. If that command fails or the API is disabled, this evidence is absent. Do not enable an API. Tokenize the deployment or stack name with the mark table. A name with no environment token is not evidence.
3. **Infrastructure code in the project’s repos** that creates this resource per environment. Bicep, ARM, and Terraform. The file has to create this resource, and the environment has to be a parameter, a directory, a workspace, or a name token in that file. Cite the repo-relative path. Read a checkout that is already here. Do not clone. A repo named in `docs/system/repos.md` that is not checked out is not evidence. A comment, a README, or a similar name is not evidence. Code that creates it for both a non-prod environment and production makes it shared.

Map the class the same way as any other source. Cite it like `connection from <resource id> says dev`, `deployment <name> says dev`, or `<path> says dev`.

## Group suggestion

After evidence, whatever is still unmarked in a group where other resources have a mark is one question. List every such resource. Each line says `probably <env>, same group as <marked resource or pipeline>`. Cite the pipeline when that sibling’s mark is a pipeline line. Otherwise cite the marked resource. When the sibling’s mark is a deployment, cite that marked resource, not the deployment name.

Suggest an environment only when every marked resource in that group agrees on one class. A shared resource does not agree with the others. When they do not agree, do not suggest. Those resources stay unmarked. Google Cloud has no resource group. Do not invent one from the project. A suggestion there does not apply. AWS uses an AWS resource group. The account and the region are not a group.

Options:

1. **Accept every suggestion.**
2. **Accept none.**
3. **I will edit this list.**

Accept appends a line for each accepted resource: `marked by the user, suggested by group`. Then classify those resources again. **I will edit this list** stops this question. Wait for the edited list. A line they kept is accepted. A resource they add that was not suggested stays out.

When nothing is suggested, do not ask. Go on to leftovers.

## Leftovers

Everything still unmarked is one question. List every unmarked resource. List every group that still has one. Do not drop one to keep the question short.

Options:

1. **Leave every unmarked resource unread and continue.**
2. **Stop the read.**
3. **I'll mark these myself.**

Continue leaves those resources unread and goes on to the pre-prod question, when that question is needed, then look inside, then the sections. Stop asks no further question, does not look inside, and asks no section. It does not read further. Marks already confirmed stay appended. Do not append anything else. Pre-prod and shared resources that were not asked stay not read.

**I'll mark these myself** waits for the reply, the same way an edited section waits. The reply names an environment for a resource or for a group. Do not invent an environment they did not name. The environment word has to be one this skill knows. Map it with the mark table. A group reply writes one line per still-unmarked resource in that group. The source is `marked by the user`. A resource that was not listed stays unmarked. Naming prod or live on one leftover does not stop the whole read. That resource is then production, and it is skipped unless another source disagrees. Then classify again and go on to the pre-prod question, when that question is needed, then look inside, then the sections.

When nothing is unmarked, do not ask. Go on to the pre-prod question, when that question is needed, then look inside.

## Pre-prod and shared

Before any pre-prod or shared resource is read for shape, ask one yes/no question. Ask it after evidence, the group suggestion, and the leftovers question, so a mark the user just confirmed is included. If leftovers stopped the read, do not ask. List every pre-prod resource and every shared resource. Do not drop one to keep the question short. Do not read their properties before the answer. A connection-field look at a skipped production resource, for evidence, is not this read.

Use the questions tool when it is available. Options only.

1. **Yes. Read these for shape and connections only.**
2. **No. List them as not read.**

The prompt says: read pre-prod resources for shape and connections only? Say that shared resources are in the same question.

A yes reads type, the settings that name another resource id or hostname, links, and triggers. Never data. Never secrets. A no lists them as not read. They are not seen. Look inside does not open a pre-prod or shared database or store that this answer left unread.

Then run Look inside. Then ask the sections.

## Look inside

Run this after the pre-prod question, when that question is needed, and before any section. If leftovers stopped the read, skip it. Do not ask a section in the same step.

Two readers, in this order. One question at a time. Do not ask the next question in the same questions call.

- **SQL** — [references/sql.md](references/sql.md) (drop-in: `.claude/skills/crav1-environment-read/references/sql.md`; plugin: this skill’s `references/sql.md`). Metadata only. Never a row.
- **Storage** — [references/storage.md](references/storage.md) (drop-in: `.claude/skills/crav1-environment-read/references/storage.md`; plugin: this skill’s `references/storage.md`). Structure only. Prefix depth is 2. Never a blob, a file count, or a size.

When the databases this pass found have no clear environment, say `There are no clear database environments.` Then ask that reader’s questions. Options only.

Before the question that opens a database or a store, say how to reach it and how much setup is needed. This skill does not install a tool. It does not create a login, a user, a firewall rule, a role, a SAS token, or a key. If access is missing, stop that reader and name what is missing. Do not open it. The other reader still runs. The sections still run.

A schema, a table, a container, or a prefix is evidence only when the whole-word token rule matches. Cite it on the Seen line. A similar name is not evidence. Do not write that cite into `docs/environments/marks.md`.

Production is never opened. Pre-prod and shared follow the yes already given, and stay shape and connections only.

What a yes finds joins the sections below. Do not add a section. Each fact says `Seen in <host> <environment>.`

## Sections

Show one section at a time. Each section has its own question and its own answer. Do not merge sections into one list. Do not collapse the questions into one write-or-not question. List every item. Do not drop a resource, a skipped line, a link, a trigger, a fact, or a left-out line to keep a section short.

A fact already written in the destination file stays in its section and is marked already written. The owner does not add it again.

Use only these sections, in this order. Do not invent another section. Resources the user left unread, and pre-prod or shared resources they declined, stay out of these sections. The counts at the end name them.

**Skipped.** Every resource whose only mark is production. Each line is the resource name, the group, and the mark that said production. The line says skipped. It is not a fact and not a link. When none are marked production, the section says nothing was skipped.

**Seen.** Every resource this pass took, plus every SQL or storage fact a yes on look inside returned. A full non-prod resource is in this list. A pre-prod or shared resource is in this list only after the user said yes. Each line cites the resource id, the name, the group, and every source. A schema, table, column, container, or prefix line cites that name and the token when one matched. Each line says `Seen in <host> <environment>.` Use the environment column in the mark table. A shared line also says `shared with prod` and shows both sources. A pre-prod or shared line also says `Shape and connections only.` It does not say the code shows it. When nothing was taken, the section says this host shows no non-prod resource. Do not invent one.

**Links.** A connection the environment shows on a seen resource: a field that names another resource id or hostname, and a trigger. Cite the resource id and the field. A trigger line shows the definition only: what starts the work, what it runs, and the schedule when it has one. A SQL job or trigger, and a storage trigger, use that same line when look inside reached them. Never a payload. Never a secret. Never command text. The reader file lists the trigger kinds for that host. A similar name is not a connection. A seen resource does not become a link by itself. When no field and no trigger shows a connection, the section says no connection is shown. Do not offer a guessed link.

**System.** Seen facts, and links the environment shows, that belong in `docs/system`. When `docs/system/` is missing, the section says so. This command does not create that folder. When every line is already in the picture, the section says the picture is current.

**Architecture.** Seen facts, and links the environment shows, that belong in `docs/architecture/spec.md`. When that file is missing, the section says so. This command does not create it. When every line is already there, the section says the architecture spec is current.

**Match.** A seen fact that belongs on a slice Match already owns. That slice is a `docs/specs/<slug>/spec.md` (skip `_template`) that already has `## Match` for this fact. When no such spec exists, the section says no slice Match owns this. Do not create a slug. When more than one Match spec could take the fact, list each slug in the section. Do not drop one.

**Left out.** Every line under `## Left out` in `docs/architecture/left-out.md` that this environment now shows. A similar name is not enough. The environment has to show that fact. When the file is missing, or no line is shown, the section says no line comes off. A `## Dismissed` line stays dismissed. Do not offer it.

Stop. Do not write those files yourself. Ask the section in front of you. Stop until that section has an answer. Then the owner adds. Then ask the next section. Do not ask the next section in the same questions call.

Use the questions tool when it is available. Options only. Put that section’s items in the question prompt. Do not shorten the prompt by dropping an item.

**Skipped, when it lists resources.** Options:

1. **Keep every resource in this section skipped.**
2. **I will edit this section.**

Do not offer an option that reads a production resource.

**Skipped, when nothing was skipped.** Options:

1. **Nothing was skipped.**
2. **I will edit this section.**

**Seen, when it lists resources.** Options:

1. **These are seen in these environments.**
2. **None of this section.**
3. **I will edit this section.**

**Seen, when it shows no resource.** Options:

1. **This host shows no non-prod resource.**
2. **I will edit this section.**

**Links, when the environment shows at least one.** Options:

1. **The environment shows every connection in this section.**
2. **I will edit this section.**

**Links, when none is shown.** Options:

1. **No connection is shown.**
2. **I will edit this section.**

Do not add an option that accepts a guessed link.

**System, Architecture, or Match, when it lists new lines.** Options:

1. **Add every new line in this section.**
2. **Add none of this section.**
3. **I will edit this section.**

**System, when the folder is missing.** Options:

1. **Add none. The folder is missing.**
2. **I will edit this section.**

**Architecture, when the file is missing.** Options:

1. **Add none. The file is missing.**
2. **I will edit this section.**

**Match, when no slice owns this.** Options:

1. **Add none. No slice Match owns this.**
2. **I will edit this section.**

**System or Architecture, when the file is current.** Options:

1. **Nothing new.**
2. **I will edit this section.**

**Left out, when it lists lines the environment shows.** Options:

1. **Take every shown line off left-out.md.**
2. **Take none off.**
3. **I will edit this section.**

**Left out, when no line comes off.** Options:

1. **No line comes off.**
2. **I will edit this section.**

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not ask that section again. Sections already answered stay answered. A line they struck stays out. A resource they add that the reader did not take stays out. A link they add that the environment does not show stays out. Say the environment does not show it. Omitting a listed item does not drop it.

A skipped confirm writes no file. The skipped lines stay skipped.

## The owner adds

You do not write those files. The skill that already owns the file adds only what is new, after that section’s answer. The handoff is the confirmed lines. It is not that skill’s interview, branch prompt, or first write. Do not start Specify, Plan, or Build.

Mark every added line `Seen in <host> <environment>.` Keep `shared with prod` when the confirmed line says it. Keep `Shape and connections only.` when the confirmed line says it. Do not mark it as something the code shows. Do not rewrite a line that is already there. A connection is added only when the links section says the environment shows it.

**System.** `/crav1-keep-current` owns the picture in `docs/system` (drop-in: `.claude/skills/crav1-keep-current/SKILL.md`; plugin: sibling `skills/crav1-keep-current/SKILL.md`). It adds only a new sentence, node, edge, or connection line. If `docs/system/` is missing, it writes nothing.

**Architecture.** `/crav1-repos-to-spec` owns `docs/architecture/spec.md` (drop-in: `.claude/skills/crav1-repos-to-spec/SKILL.md`; plugin: sibling `skills/crav1-repos-to-spec/SKILL.md`). It appends only a new line when that file is already there. If the file is missing, it writes nothing. It does not create the file from the environment.

**Match.** `/crav1-add-to-spec` owns the quote on a feature spec that already exists (drop-in: `.claude/skills/crav1-add-to-spec/SKILL.md`; plugin: sibling `skills/crav1-add-to-spec/SKILL.md`). It adds the quote only on a slice Match already owns. If none does, it writes nothing. It does not create a slug.

**Left out.** `/crav1-repos-to-spec` owns `docs/architecture/left-out.md`. A line the environment now shows comes off that file. A line that stays is not rewritten. The line that comes off is not written back as a guess.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-feature-branch`, `/crav1-finalize-commit`, or `/crav1-pipeline-environments`.

Output only:

- Host, or that the read stopped before a reader
- The reader used (Azure, AWS, or Google Cloud), or that this host has no reader, or the exact CLI or login that is missing
- Counts: seen, shape only, skipped, not read, connections shown, databases opened, storage accounts opened. A look-inside that did not open says not opened.
- Files this skill appended (`docs/environments/marks.md`) and files the owners changed, or that nothing was written
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Hard rules

- No host named: stop. Do not guess the host.
- The user names the host, not the subscription, the account, or the project. They do not pick dev or test. One pass reads every non-prod environment.
- Naming production, prod, or live stops the read. Do not list resources.
- Never read production data. A resource whose only mark is production is skipped and listed as skipped.
- `live` is production when it is a whole word.
- A host with no reader stops. This build reads Azure, AWS, and Google Cloud. Do not pretend to read any other host.
- Do not read Azure DevOps, GitHub, or CI.
- Name the missing CLI or the missing login. Do not install a CLI. Do not log in.
- Pre-prod, and a resource shared with prod, are shape and connections only, and only after the one yes. A no lists them as not read.
- Sources that disagree between non-prod and production make the resource shared. Cite both sources.
- Evidence is the three kinds above, strongest first. A similar name is not evidence.
- This skill’s only write is an append to `docs/environments/marks.md` of a line the user confirmed. Create that file only after at least one confirmed mark. Never rewrite an existing line.
- This skill does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.
- A fact is seen in that environment. It is not something the code shows.
- A link, including a trigger definition, is added only when the environment shows the connection. Do not invent a link. Do not show a payload or a secret.
- After the first read, and before any section, SQL and storage look-inside run only when the user says yes. SQL is metadata only. Storage is structure only, prefix depth 2. Never a row. Never a blob, a file count, or a size. Never a connection string, a key, or a secret.
- No clear database environment: say `There are no clear database environments.` Then ask. Options only. One question at a time.
- Production databases and production storage are never opened. Pre-prod and shared follow the earlier yes and stay shape and connections only.
- A schema, a name, or a prefix is evidence only when the whole-word token rule matches. A similar name is not evidence.
- Do not install a tool. Do not create a login, a user, a firewall rule, a role, a SAS token, or a key. Missing access stops that look-inside and names the gap. The sections of the first read still run.
- Look-inside facts use the sections that already exist. They say `Seen in <host> <environment>.`
- One question at a time. Every item stays listed.
- The owner adds only what is new. Do not rewrite a line that is already there.
- A slice Match does not already own is not a new slug.
- Do not start Specify, Plan, or Build.

## Style

Be concise. Cite the resource id. Prefer the smaller fact. Do not fill a gap with an architecture you invented.
