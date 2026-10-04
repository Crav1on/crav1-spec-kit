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
| `/crav1-environment-read` | The user names the host and a dev or test environment |
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

## Plan

| Kind | Name |
| --- | --- |
| Skill | `/crav1-plan-from-spec` |
| Skill | `/crav1-review-plan` |
| Skill | `/crav1-tighten-plan` |
| Subagent | `crav1-plan-reviewer-agent` |

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
| Skill | `/crav1-explain` |
| Skill | `/crav1-keep-current` |
| Skill | `/crav1-fix-bug` |
| Skill | `/crav1-exploratory-test` |
| Skill | `/crav1-export-spec` |
| Skill | `/crav1-draft-commit-message` |
| Skill | `/crav1-finalize-commit` |
| Skill | `/crav1-open-pr` |
| Skill | `/crav1-review-pr` |
| Skill | `/crav1-merge-pr` |
| Helper | Research |

`/crav1-merge-pr` may run from any lane, and only when the user explicitly asks in that turn to merge a named pull request. It does not move work into Specify, Plan, or Build.

`/crav1-review-pr` may run from any lane, and only when the user names an open pull request (number or URL) in that turn, or clearly asks to review that pull request. It does not move work into Specify, Plan, or Build. It only names the lane for a finding. Spark, specify, and verify do not run it.

`/crav1-security-review` may run from any lane, and only after architecture already exists (`docs/system/` or a spec that already describes the design). The same command reviews the whole system, one existing spec, or the change in front of us. It does not move work into Specify, Plan, or Build. Spark, plan, and verify do not run it.

`/crav1-repos-to-spec` is a starter option. Asking for startup options names it and does not run it. It may run from any lane. The user names one or more repos. It still runs only when the user names repos. It reads those repos and writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) when that file is missing, and the system notes in `docs/system/` that `/crav1-explain` reads when those notes are missing. When a real system note is already there, it leaves those notes and writes the missing architecture spec and `docs/architecture/left-out.md`. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there. A fact the code shows is confirmed. Before any file is written, the confirmation stays in sections: one per named repo for confirmed facts, one for inferred guesses, one for links, and one for left-out. Each section has its own question and its own answer. Every item stays listed. A guess stays out until that section’s answer accepts it, and then it is accepted from a guess, not a code fact. Confirming a guess does not turn it into a link. A guess that stays left out is written to `docs/architecture/left-out.md`, beside the architecture spec. That file stays in `docs/architecture/`. A later re-read reads it and checks the code for every line. When the code shows the fact or a real link, the line comes off that file and is written as a fact or a link. When the code still does not show it, the line stays. The left-out answer can accept a line, keep it left out, or dismiss it. Dismiss means it is not offered again. A link is written only when the code shows it. If none is found, that section says so and does not offer a guessed link. It does not invent links. It does not design the next feature, write application code, or start Specify, Plan, or Build. It is not `/crav1-code-into-specs`. It does not move work into Specify, Plan, or Build.

`/crav1-environment-read` is a starter option. Asking for startup options names it and does not run it. It may run from any lane. The user names the host and the environment at the start. It still runs only when the user names the host and a dev or test environment. Examples: Azure dev, Google Cloud test, AWS dev. It does not guess the host. It never reads production. Each host has its own reader. The reader lists only what that named environment actually has. A host with no reader stops and says so. It does not pretend to read it. This build has readers for Azure, AWS, and Google Cloud. Any other named host stops with no reader. It does not read Azure DevOps, GitHub, or CI. The user names the environment, not the subscription, the account, or the project. The reader takes only a resource whose name, group, or tag says dev or test. Anything marked production is skipped and listed as skipped. A resource with no environment mark stops and asks. It is not read. The skill only reads. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment, not as something the code shows. It does not become a link unless the environment shows the connection. Confirmation is one section at a time, with its own question and answer, and nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system` through `/crav1-keep-current`. Architecture facts go to `docs/architecture/spec.md` through `/crav1-repos-to-spec`. A slice Match already owns goes on that feature spec through `/crav1-add-to-spec`. A left-out line the environment now shows comes off `docs/architecture/left-out.md` through `/crav1-repos-to-spec`. Lines that are already there are not rewritten. It does not start Specify, Plan, or Build. It does not move work into Specify, Plan, or Build.

`/crav1-explain` may run from any lane. It reads the system notes already in `docs/system/`. The first answer is a short TLDR. Longer goes one level deeper from the same notes. It does not move work into Specify, Plan, or Build. It does not write a file.

`/crav1-keep-current` may run from any lane, on its own. The passes that already append a glossary row also run this picture update. It adds what is new to the short description, the diagram, and how the parts connect. It does not move work into Specify, Plan, or Build. It does not design the change and does not build it.

`/crav1-fix-bug` may run from any lane, and only when the user names a real bug in that turn. A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside. If they have not named one, it stops. It does not go hunting. It names the lane and does not move work into Specify, Plan, or Build. It does not start that lane. A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build. Spark, specify, plan, and verify do not run it. It is not a stretch of verify. When the user asks for startup options, this skill is one of the seven starter options above. That ask names the list and does not run this skill. It is an intake for a bug that already exists. It still runs only when the user names a real bug. It is not a skill that runs because a repo is new, and it is not started automatically.

`/crav1-exploratory-test` may run from any lane, after a build of a slice already exists. Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness and follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. The user does not set a clock. It writes bugs to `docs/specs/<slug>/explore.md`. It does not write the checks the plan already named. It does not move work into Specify, Plan, or Build. It does not start those lanes. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn. It is a later skill. It is not one of the seven starter options. When the user asks for startup options, that ask names the seven and does not run this skill. Spark, specify, plan, and verify do not run it.

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
    - crav1-explain
    - crav1-keep-current
    - crav1-fix-bug
    - crav1-exploratory-test
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
