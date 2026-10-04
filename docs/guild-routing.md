# Guild routing

This file maps each `/crav1-…` skill and `*-agent` subagent to a lane — Specify, Plan, Build, or Cross-cutting — and records cross-cutting helpers, so a kit consumer can route work when the kit changes. Cross-cutting skills may be invoked from any phase, and cross-cutting helpers may be flagged from any phase. Neither is owned by Specify, Plan, or Build alone, and neither by itself moves work into another lane.

Kit source of truth: [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).

Skill slash names are `/crav1-…`. Subagent names end in `-agent`.

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

Research is a cross-cutting helper with no slash command. Flag it when a run hits a technical question that needs research before Specify or Plan can proceed: choosing a technology or service, changing the architecture, scaling or modernizing, or judging an idea nobody has built yet.

Any lane that hits this flags it to the process orchestrator or guild lead, who pauses that lane and sends the researcher the question, the product or feature slug, and any constraints.

The researcher treats the project's existing specs, plans, and code as the current state. For parts those do not cover, the researcher may use an architecture-extraction skill if one is available.

The full study lives wherever the team keeps its research. The researcher writes a short `docs/specs/<slug>/research.md` with the recommendation, trade-offs, confidence, and a link to the full study, and returns the recommendation to the process orchestrator or guild lead with a suggested lane. That role routes it.

Aside from that `research.md`, the researcher does not edit specs, plans, or code, and does not change the lane.

## Maintainer note

When you add, rename, or remove a skill, agent, or cross-cutting helper, update this file in the same pull request. Notify your process orchestrator or guild lead, if you have one, with the routing diff.

## Machine-readable map

```yaml
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
