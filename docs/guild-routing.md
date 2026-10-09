# Guild routing

This file maps each `/crav1-…` skill and `*-agent` subagent to a lane — Specify, Plan, Build, or Cross-cutting — and records cross-cutting helpers, so a kit consumer can route work when the kit changes. Cross-cutting skills may be invoked from any phase, and cross-cutting helpers may be flagged from any phase. Neither is owned by Specify, Plan, or Build alone, and neither by itself moves work into another lane.

Kit source of truth: [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).

Skill slash names are `/crav1-…`. Subagent names end in `-agent`.

## Starter options

When the user asks for startup options, these seven are the only ways in. That ask names the list. It does not run a skill. It does not move work into a lane. Each starter still follows the rules it already has. Every other skill is a later skill.

| Starter | Runs when |
| --- | --- |
| `/crav1-spark-to-spec` | The user brings one or two sentences |
| `/crav1-ideas-to-spec` | The user brings a pile of ideas and technical hunches |
| `/crav1-intake-to-specs` | The user brings mixed files, or more than one v0 feature |
| `/crav1-match-to-specs` | The user brings existing repos plus a dump to match |
| `/crav1-repos-to-spec` | The user names the repos |
| `/crav1-environment-read` | The user names the host |
| `/crav1-fix-bug` | The user names a real bug |

The same list is where a lone user sees the ways to start: [plugins/crav1/README.md](../plugins/crav1/README.md) and [first-run.md](first-run.md).

## Specify

| Kind | Name |
| --- | --- |
| Skill | `/crav1-spark-to-spec` |
| Skill | `/crav1-ideas-to-spec` |
| Skill | `/crav1-intake-to-specs` |
| Skill | `/crav1-match-to-specs` |
| Skill | `/crav1-match-dump-to-specs` |
| Skill | `/crav1-code-into-specs` |
| Skill | `/crav1-add-to-spec` |
| Skill | `/crav1-architecture-reviewer` |
| Skill | `/crav1-tighten-spec` |
| Skill | `/crav1-resolve-questions` |
| Subagent | `crav1-spec-reviewer-agent` |
| Subagent | `crav1-architecture-reviewer-agent` |
| Subagent | `crav1-intake-slice-agent` |

`/crav1-tighten-spec` reads `spec.md`, diagrams, ADRs, reviewer findings already in the chat, and, when the slice is partial or `## In the code` names paths, the committed code on the repo and branch that spec names. It writes only the picked issue in `spec.md` and, when that pick says so, the named diagram, ADR, or export. It writes a branch onto the spec only after a yes. It leaves application code and unpicked issues alone. A spec with no code behind it skips that read. The user calls it. It calls no skill.

Exception: a different open repo or branch, a missing branch, a stub, or a spec too thin for that read stops and does not tighten. `suggest` does not patch. A disagreement with the code is called out and the spec is not rewritten to match the code. Finish, add a test, and leave are not choices here.

## Plan

| Kind | Name |
| --- | --- |
| Skill | `/crav1-plan-from-spec` |
| Skill | `/crav1-review-plan` |
| Skill | `/crav1-tighten-plan` |
| Subagent | `crav1-plan-reviewer-agent` |

`/crav1-plan-from-spec` reads the accepted spec, diagrams, ADRs, exports, kept security findings already written, and, when the spec is partial or `## In the code` names paths, that same committed repo and branch before any task is written. It writes `plan.md` and `tasks.md`, and matching OpenSpec export files when those already exist. A built piece that already matches v0 is marked already there and gets no rebuild task. A piece the user leaves gets one line in the plan and no task. It leaves `spec.md`, application code, and any linter install alone. The user calls it. It calls no skill.

Exception: when `## Linter` says this repo has no linter for the code the tasks will touch, it stops before Build until the user chooses. A line under `## Dismissed test suggestions` is not a task. A kept test suggestion that is already an acceptance line maps to a task. A gap or a disagreement is finish, add a verify test, or leave before any task exists. A later run does not turn a left piece into work unless the user says so.

`/crav1-review-plan` reads `spec.md`, `plan.md`, and `tasks.md`. It writes nothing. It leaves the plan and code alone. The user calls it. It calls no skill.

Exception: the parent delegates the critique and does not review in its own voice. It names `/crav1-tighten-plan` and does not run it. A piece marked already there or left as committed is not a missing task.

## Build

| Kind | Name |
| --- | --- |
| Skill | `/crav1-implement-task` |
| Skill | `/crav1-complete-task` |
| Skill | `/crav1-complete-tasks` |
| Skill | `/crav1-complete-features` |
| Skill | `/crav1-verify-spec` |
| Skill | `/crav1-fix-from-verify` |
| Skill | `/crav1-fix-live` |
| Subagent | `crav1-complete-task-agent` |

## Cross-cutting

| Kind | Name |
| --- | --- |
| Skill | `/crav1-feature-branch` |
| Skill | `/crav1-security-review` |
| Skill | `/crav1-repos-to-spec` |
| Skill | `/crav1-environment-read` |
| Skill | `/crav1-pipeline-environments` |
| Skill | `/crav1-explain` |
| Skill | `/crav1-whats-known-about` |
| Skill | `/crav1-keep-current` |
| Skill | `/crav1-fix-bug` |
| Skill | `/crav1-exploratory-test` |
| Skill | `/crav1-suggest-tests-for-code` |
| Skill | `/crav1-meeting-to-specs` |
| Skill | `/crav1-feature-candidates` |
| Skill | `/crav1-specs-to-ado` |
| Skill | `/crav1-ado-to-specs` |
| Skill | `/crav1-export-spec` |
| Skill | `/crav1-draft-commit-message` |
| Skill | `/crav1-finalize-commit` |
| Skill | `/crav1-open-pr` |
| Skill | `/crav1-review-pr` |
| Skill | `/crav1-merge-pr` |
| Helper | Research |

`/crav1-merge-pr` may run from any lane, and only when the user explicitly asks in that turn to merge a named pull request. It does not move work into Specify, Plan, or Build.

`/crav1-review-pr` may run from any lane, and only when the user names an open pull request (number or URL) in that turn, or clearly asks to review that pull request. It does not move work into Specify, Plan, or Build. It only names the lane for a finding. A pull request with no `plan.md` or `tasks.md` for its slug was built outside the kit. That is an info note, not a fix finding. It does not report a missing `verify.md`. It reads the test results that pull request's own pipeline already recorded and does not run tests. It names `/crav1-keep-current` after that pull request merges and does not run it. A pull request that has a plan keeps the plan and `verify.md` checks. Spark, specify, and verify do not run it.

`/crav1-security-review` may run from any lane, and only after architecture already exists (`docs/system/` or a spec that already describes the design). The same command reviews the whole system, one existing spec, or the change in front of us. It does not move work into Specify, Plan, or Build. Spark, plan, and verify do not run it.

`/crav1-repos-to-spec` is a starter option. Asking for startup options names it and does not run it. It may run from any lane. The user names one or more repos. It still runs only when the user names repos. It reads those repos and writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) when that file is missing, and the system notes in `docs/system/` that `/crav1-explain` reads when those notes are missing. When a real system note is already there, it leaves those notes except the `Synced at` cell of a repo it read, and writes the missing architecture spec and `docs/architecture/left-out.md`. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there, except that `Synced at` cell. A fact the code shows is confirmed. Before any file is written, the confirmation stays in sections: one per named repo for confirmed facts, one for inferred guesses, one for links, and one for left-out. Each section has its own question and its own answer. Every item stays listed. A guess stays out until that section’s answer accepts it, and then it is accepted from a guess, not a code fact. Confirming a guess does not turn it into a link. A guess that stays left out is written to `docs/architecture/left-out.md`, beside the architecture spec. That file stays in `docs/architecture/`. A later re-read reads it and checks the code for every line. When the code shows the fact or a real link, the line comes off that file and is written as a fact or a link. When the code still does not show it, the line stays. The left-out answer can accept a line, keep it left out, or dismiss it. Dismiss means it is not offered again. A link is written only when the code shows it. If none is found, that section says so and does not offer a guessed link. It does not invent links. It does not design the next feature, write application code, or start Specify, Plan, or Build. It is not `/crav1-code-into-specs`. It does not move work into Specify, Plan, or Build.

`/crav1-environment-read` is a starter option. Asking for startup options names it and does not run it. It may run from any lane. The user names the host at the start. It still runs only when the user names the host. Examples: Azure, AWS, Google Cloud. Naming production, prod, or live stops. It does not guess the host. It never reads production data. One pass reads every non-prod environment. Each seen line keeps its own environment. A prod-only line says `Seen in <host> prod.` and `prod only`. Each host has its own reader. A host with no reader stops and says so. It does not pretend to read it. This build has readers for Azure, AWS, and Google Cloud. Any other named host stops with no reader. It does not read Azure DevOps, GitHub, or CI. The user names the host, not the subscription, the account, or the project. Marks come from the name, the group, the tags, and `docs/environments/marks.md` when that file exists. Non-prod tokens are dev, development, test, testing, stage, staging, uat, and qa. Pre-prod, a resource marked both non-prod and production by different sources, and a prod-only resource are shape and connections only, after one yes. The mixed resource is labelled `shared with prod`. Prod-only means the only mark is production, so there is no non-prod twin on that resource. A no lists them as not read. A declined prod-only resource stays skipped. Look-inside never opens production. An unmarked resource can be marked from shown evidence, strongest first. What is still unmarked is asked, then left unread, marked by the user, or stops the read. The skill appends only confirmed lines to `docs/environments/marks.md`. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment, not as something the code shows. A link, including a trigger definition, is added only when the environment shows the connection. After the first read, and before any section, it can look inside a database or storage when the user says yes. SQL is metadata only. Storage is structure only, prefix depth 2. It never reads a row or a blob, and it never reports a file count or a size. Production is never opened. When the databases have no clear environment, it says there are no clear database environments and asks, options only, one question at a time. It does not install a tool, and it does not create a login, a firewall rule, a role, or a key. Missing access stops that look-inside and names the gap. Facts still say seen in that environment and join the sections that already exist. If the CLI or the login is missing, the stop names which. The skill does not install a CLI and does not log in. Confirmation is one section at a time, with its own question and answer, and nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system` through `/crav1-keep-current`. Architecture facts go to `docs/architecture/spec.md` through `/crav1-repos-to-spec`. A slice Match already owns goes on that feature spec through `/crav1-add-to-spec`. A left-out line the environment now shows comes off `docs/architecture/left-out.md` through `/crav1-repos-to-spec`. Lines that are already there are not rewritten. It does not start Specify, Plan, or Build. It does not move work into Specify, Plan, or Build. After `docs/environments/marks.md` lines are added, it asks once whether to run `/crav1-keep-current` and does not run that refresh from the question.

`/crav1-pipeline-environments` may run from any lane. The user names Azure DevOps, the org, and the project. A pipeline name is optional. If any of those three is missing, it stops and asks. Options only. It does not guess. It reads pipeline definitions with `az pipelines` and `az devops` and does not run a pipeline. The stage name gives the environment, with the same whole-word rule as `/crav1-environment-read`. It appends only confirmed lines to `docs/environments/marks.md`. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. It does not move work into Specify, Plan, or Build. It does not start those lanes. It names `/crav1-environment-read` and does not run it. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it.

`/crav1-explain` may run from any lane. It reads the system notes already in `docs/system/`. The first answer is a short TLDR. Longer goes one level deeper from the same notes. It stays read-only. On every run it compares the feature index with each slice's node in `docs/system/diagrams.md` and its line in `## How the parts connect`. Names match only by slug, spec title, or main resource name. It lists each slice missing entirely or partly, including done and retired, with status, and names `/crav1-keep-current`. It does not run it. When the picture has nothing on the question, it quotes the first paragraph of the matching spec, labelled as coming from the spec, and names `/crav1-whats-known-about`. When no spec matches either, it says so and names that skill. It does not move work into Specify, Plan, or Build. It does not write a file.

`/crav1-whats-known-about` may run from any lane. The user asks about one feature, slice, resource, or not-yet-feature. The answer comes from the specs first. It reads only. It writes nothing. One pass matches an exact name first, then key words, with spec titles and Match quotes weighted highest. One winning slice is the answer, and the path is named. Two or more close hits are listed and it asks which. It does not guess. No slice: it says so and presents a candidate slice. It names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run them. Pasted minutes or a long dump names `/crav1-meeting-to-specs` or `/crav1-match-dump-to-specs` and stops. After the repo part it runs read-only Azure and Azure DevOps checks. Production is shape and connections only, after the same yes or no as `/crav1-environment-read`. It never reads data. A failed live read offers Retry or Skip. It may name one skill. It does not run another skill. It does not move work into Specify, Plan, or Build. It does not start those lanes. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. It is not `/crav1-explain`. Spark, specify, plan, and verify do not run it.

`/crav1-keep-current` may run from any lane, on its own. The passes that already append a glossary row also run this picture update. Spark, ideas, intake, match, match-dump, code-into-specs, and repos-to-spec update the picture in their own pass. It adds what is new to the short description, the diagram, and how the parts connect. When this run reads a whole repo, it sets that repo's `Synced at` cell and touches only those repos. When this run reads only one slice, it leaves the column alone and writes the slice line. It does not move work into Specify, Plan, or Build. It does not design the change and does not build it. `/crav1-complete-features` asks when a slice is marked done or retired. `/crav1-fix-bug` and `/crav1-fix-live` ask when the fix changes how the parts connect. `/crav1-environment-read` asks after marks lines are added. `/crav1-add-to-spec` asks once at the end of an environment-read or suggest-tests handoff. Those asks do not run this command. `/crav1-implement-task` and `/crav1-complete-task` do not ask.

`/crav1-fix-bug` may run from any lane, and only when the user names a real bug in that turn. A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside. If they have not named one, it stops. It does not go hunting. It names the lane and does not move work into Specify, Plan, or Build. It does not start that lane. A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build. Spark, specify, plan, and verify do not run it. It is not a stretch of verify. When the user asks for startup options, this skill is one of the seven starter options above. That ask names the list and does not run this skill. It is an intake for a bug that already exists. It still runs only when the user names a real bug. It is not a skill that runs because a repo is new, and it is not started automatically. When the bug changes how the parts connect, it asks once whether to run `/crav1-keep-current` and does not run it.

`/crav1-exploratory-test` may run from any lane, after a build of a slice already exists. Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness and follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. The user does not set a clock. It writes bugs to `docs/specs/<slug>/explore.md`. It does not write the checks the plan already named. It does not move work into Specify, Plan, or Build. It does not start those lanes. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. Spark, specify, plan, and verify do not run it.

`/crav1-suggest-tests-for-code` may run from any lane. The user points at code that already exists, one repo or one area, not the whole system. It reads that code and suggests tests for what that code can actually break. A function gets a few checks. A page gets a browser check. A boundary gets an integration check. It does not dump every test type. Every suggestion stays listed. Nothing is dropped to keep the list short. The user takes them one at a time: keep, leave, or dismiss. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. It does not write the tests, change the code, or start Specify, Plan, or Build. It does not move work into a lane. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it.

`/crav1-meeting-to-specs` may run from any lane. Everything after the command, and every `@`, is the input. An email or a chat thread is accepted as well as minutes or a transcript. If there is no pointer, it stops and asks. Options only. It does not guess. The kind is `meeting`, `email`, or `chat`, from what the input shows. If the kind is not clear, it asks once per run, options only. The date comes from the input. It does not invent one. When the input shows no date, it asks once per run, options only: give a date, or skip. One kind and one date apply to every item. It extracts requirements, decisions, changes, open questions, and bugs as quotes, with speaker and time when the input shows them, and drops small talk. It matches each item to existing `docs/specs/<slug>/` folders, skipping `_template`. Cases are an addition, a possible new feature, a bug, or unclear. When more than one existing spec could fit, every candidate stays listed. Nothing is dropped to keep the list short. Each item that matches an existing spec shows one line, `State: <state>.`, and a short reason that names the evidence, in the item block and in the question. The states are built, partly built, planned, and not built. `Fits: none` has no state line. Evidence is that slice’s `spec.md` (including `## Match`), `plan.md`, `tasks.md` checkboxes, and `verify.md` when present. When those do not settle it, one read-only look at the code that spec or plan points to. A code-based or uncertain state is labeled `(inference, not in the docs)`. The line does not change keep, leave, or dismiss. It is not written and it is not passed to `/crav1-add-to-spec` as quote text. The user takes items one at a time: keep, leave, or dismiss. Dismiss is for this run only. The next run starts fresh. It does not write a dismissals file. A kept addition is handed to `/crav1-add-to-spec` for that slug. The handoff passes the kind, the date, and the source folder when one was written. The quote starts with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` The impact check still runs there. A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run it. A kept bug names `/crav1-fix-bug` and does not run it. When a kept addition imports a source, it writes `docs/sources/YYYY-MM-DD-<slug>/` following the imported-sources convention and does not write the spec. It does not commit. It does not move work into Specify, Plan, or Build. It does not start those lanes. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it.

`/crav1-feature-candidates` may run from any lane. It reads the landscape, the specs, research, and sources, and lists Feature candidates. A dated milestone or slice is one candidate. An undated spec with open work is one candidate. A spec that holds only open questions is marked questions only. An item with no spec is marked no spec yet. It skips a spec that is done or retired with nothing open. It shows a recorded Azure Boards id. It gives a target date only when the docs state it. It writes nothing unless the user asks for a file. It does not call Azure Boards. It does not move work into Specify, Plan, or Build. It does not start those lanes. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it. `/crav1-specs-to-ado` runs it.

`/crav1-specs-to-ado` may run from any lane. It takes the Azure DevOps org and project from `docs/environments/marks.md` or from the Azure DevOps URLs in `docs/system/repos.md`. It checks `az`, including the default install paths, and that the project has the Feature work item type. Before the preview it reads the Feature fields. When that type has Acceptance Criteria, the checks go there. When it does not, the checks go in the Description as an Acceptance checks list, that field is not sent, and the preview says so. A failed field read states the issue, suggests a fix, and offers a skip. It does not guess. It runs `/crav1-feature-candidates` and the user picks by number or all. It previews the Feature form. It creates or updates a Feature only after the user says yes. The same field rule applies on an update. After a Create, writing the new id into that spec’s `work-item.md`, or a row on the landscape `## No spec yet in ADO` table when the item has no spec, is required. The closing output names that file, says it is not committed yet, names `/crav1-finalize-commit`, and says a later run would offer Create again. If the write fails, it prints the line to add. Nothing it sends mentions the specs repo. A preview edit goes into the spec through `/crav1-add-to-spec` first. It does not move work into Specify, Plan, or Build. It does not start those lanes. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it.

`/crav1-ado-to-specs` may run from any lane. It reads the Features whose ids are recorded in `work-item.md` files and the landscape table, or only the ids the user names. It shows what differs from the spec or is new. It reads the checks from Acceptance Criteria when the Feature type has that field, and from the Acceptance checks list in the Description when it does not, so a match is not a change. Discussion comments use an api version current `az` can parse (`7.1-preview`). A missing id stays missing. The user keeps or dismisses each change. Dismissals start fresh each run. A kept change goes to the spec through `/crav1-add-to-spec`. A no-spec-yet Feature names a starter such as `/crav1-spark-to-spec` and does not run it. A reply comment is posted only after the user says yes, and only when the spec already answers the question. It does not move work into Specify, Plan, or Build. It does not start those lanes. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. The seven starter options stay unchanged. Spark, specify, plan, and verify do not run it.

Research is a cross-cutting helper with no slash command. Flag it when a run hits a technical question that needs research before Specify or Plan can proceed: choosing a technology or service, changing the architecture, scaling or modernizing, or judging an idea nobody has built yet.

Any lane that hits this flags it to the process orchestrator or guild lead, who pauses that lane and sends the researcher the question, the product or feature slug, and any constraints.

The researcher treats the project's existing specs, plans, and code as the current state. For parts those do not cover, the researcher may use `/crav1-repos-to-spec`. Running that command is the skill writing the architecture spec, and the system notes when those notes are not already there. The researcher does not hand-edit those files.

The full study lives wherever the team keeps its research. The researcher writes a short `docs/specs/<slug>/research.md` with the recommendation, trade-offs, confidence, and a link to the full study, and returns the recommendation to the process orchestrator or guild lead with a suggested lane. That role routes it.

Aside from that `research.md`, the researcher does not edit specs, plans, or code, and does not change the lane.

## Maintainer note

When you add, rename, or remove a skill, agent, or cross-cutting helper, update this file in the same pull request. Notify your process orchestrator or guild lead, if you have one, with the routing diff.

## Machine-readable map

```yaml
starters:
  - crav1-spark-to-spec
  - crav1-ideas-to-spec
  - crav1-intake-to-specs
  - crav1-match-to-specs
  - crav1-repos-to-spec
  - crav1-environment-read
  - crav1-fix-bug
specify:
  skills:
    - crav1-spark-to-spec
    - crav1-ideas-to-spec
    - crav1-intake-to-specs
    - crav1-match-to-specs
    - crav1-match-dump-to-specs
    - crav1-code-into-specs
    - crav1-add-to-spec
    - crav1-architecture-reviewer
    - crav1-tighten-spec
    - crav1-resolve-questions
  subagents:
    - crav1-spec-reviewer-agent
    - crav1-architecture-reviewer-agent
    - crav1-intake-slice-agent
plan:
  skills:
    - crav1-plan-from-spec
    - crav1-review-plan
    - crav1-tighten-plan
  subagents:
    - crav1-plan-reviewer-agent
build:
  skills:
    - crav1-implement-task
    - crav1-complete-task
    - crav1-complete-tasks
    - crav1-complete-features
    - crav1-verify-spec
    - crav1-fix-from-verify
    - crav1-fix-live
  subagents:
    - crav1-complete-task-agent
cross_cutting:
  skills:
    - crav1-feature-branch
    - crav1-security-review
    - crav1-repos-to-spec
    - crav1-environment-read
    - crav1-pipeline-environments
    - crav1-explain
    - crav1-whats-known-about
    - crav1-keep-current
    - crav1-fix-bug
    - crav1-exploratory-test
    - crav1-suggest-tests-for-code
    - crav1-meeting-to-specs
    - crav1-feature-candidates
    - crav1-specs-to-ado
    - crav1-ado-to-specs
    - crav1-export-spec
    - crav1-draft-commit-message
    - crav1-finalize-commit
    - crav1-open-pr
    - crav1-review-pr
    - crav1-merge-pr
  subagents: []
  helpers:
    - research
```
