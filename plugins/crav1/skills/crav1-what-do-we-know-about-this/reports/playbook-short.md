# report-playbook-short

One screen: how to get one goal (a milestone, a release, a set of agreed changes) from its decisions to work that can be built, using the kit's skills in order. Rules: `reports/common.md`.

Preview (1.109.0).

Answers come first in the report. Write nothing in the project. After the user confirms the answers, the existing skills write them (named in Steps).

Buckets:
- **Kept:** decisions already made. Do not ask them again. For each, say who decided and when, if the docs say so.
- **Needs your answer:** open points. For each, give a recommended answer and why. Its status is `undecided` or `decided by <person>` when the docs name one. Never write a hand-off such as "for <name> to decide".
- **Compose:** work to put together from what exists: what splits out, or lifts from one branch or pull request into another, and why.

Steps: at most 8 numbered kit commands, each with its input. Mark a step no skill covers as `manual:` in one line. If there are more steps, the last line says `More steps: report-playbook-full`.

Diagrams: one `flowchart` of the dependency order, only when 3 or more steps depend on each other. No C4.

```markdown
# <Goal>: playbook

## Verdict
<one line: what stands between the goal and buildable work>

## Goal
<target, due date with its source>

## Kept
<bullets>

## Needs your answer
<numbered: question, recommended answer, why, status>

## Compose
<bullets>

## Steps
<numbered kit commands, at most 8>

## Order
<diagram, if any>

## Source
<specs, notes, pull requests, live reads>
```
