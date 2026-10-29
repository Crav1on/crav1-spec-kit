# report-feature-full

The whole picture of one feature. Rules: `reports/common.md`.

Diagrams: a `flowchart` per main path; a `sequenceDiagram` for each hand-off between parts; a `stateDiagram-v2` when the docs name states. C4 always: level 1 (system context) and level 2 (containers) as Mermaid `C4Context` / `C4Container`, level 3 only for a part the docs describe inside. A deployment view when environments are written down.

```markdown
# <Feature>: functionality, flow and architecture

## Verdict
## What it is
## Why it's in this state
## At a glance            (table: status, parts, inputs, outputs, environments)
## How it works           (one ### per path or rule, each with its diagram)
### When things go wrong
## Architecture
### C4 level 1: system context
### C4 level 2: containers
### C4 level 3: <part>    (only when described)
### Deployment view       (only when environments are written)
### Configuration
### Key decisions         (ADR or note, with date)
## Do not touch
## Delivery: tasks and milestones   (dependency order, as `/crav1-tasks-ready-to-build` sorts it)
## Seen only live
## Research marked stale
## Stale notes
## Tracked elsewhere
## Source
```

The sections from **Do not touch** on follow `references/answer.md` ("Answer sections").
