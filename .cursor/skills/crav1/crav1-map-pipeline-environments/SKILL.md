---
name: crav1-map-pipeline-environments
description: >-
  Read Azure DevOps pipeline definitions for the org and project the user
  named. Optional: one pipeline. List and show only. Propose marks for the
  resources each deploy step names, from the stage name, using the same
  whole-word rule as /crav1-read-environment. Append confirmed lines to
  docs/environments/marks.md, and branch-to-environment lines to
  docs/environments/promotion.md. Do not write docs/system, the architecture
  spec, feature specs, or left-out. Do not start Specify, Plan, or Build.
disable-model-invocation: true
icon: workflow
color: blue
---

# Pipeline environments

The user names Azure DevOps, the org, and the project. You read pipeline definitions and propose environment marks for the resources those definitions deploy. You do not guess the org or the project.

Command: `/crav1-map-pipeline-environments`.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The six starter options stay unchanged.

This is cross-cutting. It is not a lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This skill reads pipeline definitions. It does not read cloud resources. A stage whose name says production is still read. The Azure resource is not read.

The only file this skill writes is `docs/environments/marks.md`, and only by appending a line the user confirmed. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.

This is not `/crav1-read-environment`. That command reads a host. It does not read Azure DevOps. This command does not run it. After marks are confirmed, name it. Do not run it.

Commands and task inputs: [references/azure-devops.md](references/azure-devops.md) (drop-in: `.cursor/skills/crav1/crav1-map-pipeline-environments/references/azure-devops.md`; plugin: this skill’s `references/azure-devops.md`).

## Start

Everything after `/crav1-map-pipeline-environments`, and every `@`, is the pointer.

The user names Azure DevOps, the org, and the project in that message. A pipeline name is optional. One named pipeline is the only pipeline you read. No pipeline name means every pipeline in that project.

Azure DevOps is the host for this command. Azure, AWS, and Google Cloud are not this host. A pipeline URL on `dev.azure.com` or `*.visualstudio.com` names Azure DevOps. Read the org and the project from that URL when they are in it. Read one pipeline from that URL when it names one definition. Do not treat a file path as the org or the project.

If they named no host, stop. Ask them to name Azure DevOps. Do not guess. Do not read.

If they named a host that is not Azure DevOps, stop. Say this command reads Azure DevOps. Do not pretend to read another host. Do not read.

If they named Azure DevOps and no org, stop. Ask them to name the org. Do not guess. Do not read a default from `az devops configure` or from the git remote. Do not read.

If they named the org and no project, stop. Ask them to name the project. Do not guess. Do not read.

Use the questions tool when it is available. Options only. Do not ask them to type a path. **Ask less (1.70.0).** Gather the questions that remain into one questions call (several questions in that call when the tool allows, else one message listing them). Skip any question the invocation, the files or an earlier answer already settles, and say what was used.

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

Read `references/cli.md` ("CLI") only when the az CLI is missing, signed out, or behaves oddly.

## What is read

Read definitions only.

- YAML pipelines, including stages, deployment jobs, and `environment:` names.
- Classic release pipelines, including stages. In a classic release the stage is the environment. Its name is the stage name.
- A classic build definition, when `az pipelines show` returns one. Read it for deploy steps. It often has none.

A YAML `template:` or `extends:` that points at another pipeline YAML file is part of the definition. Read that file. Do not read any other file in the repo. Do not clone. A missing template means that part is not read. Say so. Do not guess the targets inside it.

Do not read builds, runs, logs, test runs, boards, wikis, or artifacts. Do not queue, run, approve, edit, or trigger a pipeline.

## Stage name

Read `references/naming.md` ("Stage name") only when a stage name does not map cleanly to an environment word.

## Targets

Read `references/targets.md` ("Targets") only when you map a stage to its deploy targets.

## Cases

Read `references/naming.md` ("Cases") only when a definition is classic, templated, or otherwise unusual.

## marks.md

Read `references/marks.md` ("marks.md") only when you append to docs/environments/marks.md.

## promotion.md (1.69.0)

Read `references/branches.md` ("promotion.md (1.69.0)") only when you propose promotion.md lines (the Branches section).

## Sections

Show every section together (1.70.0). Each section has its own question and its own answer, asked in one questions call. Do not merge sections. List every item. Do not drop a resource, a stage, a group-context line, or an existing line to keep a section short.

Use only these sections, in this order. Do not invent another section.

**One environment.** Every resource in that case, the proposed lines, the group, and the subscription when it was shown. Group-only context for those stages is listed with no line. When none, the section says nothing is in this section.

**Shared.** Every shared resource, both stages, and the proposed lines. Say there is no `shared` word. When none, the section says nothing is shared.

**Unclear.** Every unclear resource and the reason. Say no mark is proposed. When none, the section says nothing is unclear.

**Branches (1.69.0).** Every proposed `promotion.md` line (branch, pattern or tag line, environment, pipeline and stage), and every branch expression left unclear with its reason. When none, the section says no pipeline names a branch.

Stop. Show every section, then ask them in one questions call, one question per section (1.70.0). Stop until every section has an answer, then append the confirmed lines of each section once.

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

**Branches, when it lists proposed lines.** Options:

1. **Append every proposed line in this section** (to `docs/environments/promotion.md`).
2. **Append none of this section.**
3. **I will edit this section.**

**Branches, when nothing is in it.** Options:

1. **No pipeline names a branch.**
2. **I will edit this section.**

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not ask that section again. Sections already answered stay answered. A line they struck is not appended. A resource they add that no pipeline step names stays out. Say the pipeline does not name it. Omitting a listed item does not drop it.

An unclear confirm writes no line. Do not write `marked by the user` from this command.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-create-feature-branch`, `/crav1-read-environment`, or `/crav1-finalize-commit`.

Output only:

- Org, project, and the pipelines read (name and kind), or that the read stopped before a pipeline list
- Counts: one environment, shared, unclear
- Whether `docs/environments/marks.md` changed, and whether `docs/environments/promotion.md` changed
- Next: `/crav1-read-environment` (do not run it). When a file changed, also name `/crav1-finalize-commit` (do not run it). When nothing was written, still name `/crav1-read-environment`, and do not name finalize-commit

## Hard rules

- Azure DevOps, the org, or the project missing: stop. Do not guess. Options only. Do not ask for a typed path.
- A pipeline name is optional. No name means every pipeline in the project. A name that matches nothing stops. A similar name is not a match.
- Use `az pipelines` and `az devops` to list and show only. `--detect false` on every call.
- Do not run, queue, edit, approve, or trigger a pipeline.
- Do not read builds, logs, test runs, boards, or repo files beyond the pipeline definition.
- Name the missing CLI, the missing extension, or the missing login. Do not install. Do not log in. Do not run `az devops configure`.
- The stage name gives the environment. Use the Marks words from `/crav1-read-environment`. Do not keep a different list.
- Mark only the resource the deploy step names. The group is context. Do not mark the whole group.
- A secret is never printed. An unresolved variable is unclear. No mark is proposed for unclear.
- The marks format has no `shared` word. Shared proposes one existing-format line per stage.
- Append only a line the user confirmed, to marks.md or promotion.md. Create the file only then. Never rewrite an existing line. A disagreement is shown and the existing line stays.
- Do not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.
- Every section in one questions call, each with its own answer. Every item stays listed.
- Do not start Specify, Plan, or Build. Name `/crav1-read-environment` and do not run it.

## Style

Be concise. Cite the pipeline, the stage, and the resource. Prefer the smaller fact. Do not fill a gap with a resource the step did not name.
