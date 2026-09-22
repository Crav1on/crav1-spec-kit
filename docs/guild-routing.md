# Guild routing

This file is the kit-owned map of which Grok specialist lane owns each `/crav1-…` skill and `*-agent` subagent. **Guildmistress Rhea** (CRAV1 Head) uses it when the kit changes.

Kit source of truth: [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).

Skill slash names are `/crav1-…`. Subagent names end in `-agent`.

| Lane | Owner |
| --- | --- |
| Specify | Spec Scribe Liora |
| Plan | Planwright Sera |
| Build | Build Lead Kael |
| Shared | Guildmistress Rhea — she decides; she may keep the item or hand it to a lane with a note |

## Specify → Spec Scribe Liora

| Kind | Name |
| --- | --- |
| Skill | `/crav1-spark-to-spec` |
| Skill | `/crav1-ideas-to-spec` |
| Skill | `/crav1-intake-to-specs` |
| Skill | `/crav1-architecture-reviewer` |
| Skill | `/crav1-tighten-spec` |
| Skill | `/crav1-resolve-questions` |
| Subagent | `crav1-spec-reviewer-agent` |
| Subagent | `crav1-architecture-reviewer-agent` |
| Subagent | `crav1-intake-slice-agent` |

## Plan → Planwright Sera

| Kind | Name |
| --- | --- |
| Skill | `/crav1-plan-from-spec` |
| Skill | `/crav1-review-plan` |
| Skill | `/crav1-tighten-plan` |
| Subagent | `crav1-plan-reviewer-agent` |

## Build → Build Lead Kael

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

## Shared → Guildmistress Rhea

| Kind | Name |
| --- | --- |
| Skill | `/crav1-feature-branch` |
| Skill | `/crav1-export-spec` |
| Skill | `/crav1-draft-commit-message` |
| Skill | `/crav1-finalize-commit` |

## Maintainer note

When you add, rename, or remove a skill or agent, update this file in the same pull request. The kit notifies Rhea with the routing diff.

## Machine-readable map

```yaml
specify:
  owner: Spec Scribe Liora
  skills:
    - crav1-spark-to-spec
    - crav1-ideas-to-spec
    - crav1-intake-to-specs
    - crav1-architecture-reviewer
    - crav1-tighten-spec
    - crav1-resolve-questions
  subagents:
    - crav1-spec-reviewer-agent
    - crav1-architecture-reviewer-agent
    - crav1-intake-slice-agent
plan:
  owner: Planwright Sera
  skills:
    - crav1-plan-from-spec
    - crav1-review-plan
    - crav1-tighten-plan
  subagents:
    - crav1-plan-reviewer-agent
build:
  owner: Build Lead Kael
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
shared:
  owner: Guildmistress Rhea
  skills:
    - crav1-feature-branch
    - crav1-export-spec
    - crav1-draft-commit-message
    - crav1-finalize-commit
  subagents: []
```
