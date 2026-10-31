# report-playbook-full

Every section: how to get one goal from its decisions to work that can be built, using the kit's skills in order. Rules: `reports/common.md`.

Preview (1.109.0).

Answers come first in the report. Write nothing in the project. After the user confirms the answers, the existing skills write them (named in each row and in Steps).

Buckets:
- **Kept:** decisions already made. Do not ask them again. For each, say who decided and when, if the docs say so, with the spec line.
- **Needs your answer:** open points. For each, give a recommended answer and why. Its status is `undecided` or `decided by <person>` when the docs name one. Never write a hand-off such as "for <name> to decide".
- **Compose:** work to put together from what exists: what splits out, or lifts from one branch or pull request into another, from where to where, and why.

Steps: numbered kit commands, no cap, each with its input and what it produces. Mark a step no skill covers as `manual:` in one line. List kit gaps found on the way under Gaps; do not route around them silently.

Diagrams:
- One `gitGraph` or `flowchart` of the dependency order of branches, pull requests and steps.
- A second `flowchart` only when Compose moves work between three or more branches.
- C4 only when the goal changes architecture, and never as the first diagram.

```markdown
# <Goal>: playbook

## Verdict
<one line>

## The 30-second version
<3–5 bullets>

## Goal
<target, due date with its source, acceptance from the spec>

## Where it stands
<open pull requests and branches, missing plan or tasks, blockers; live reads>

## Kept
| Decision | Decided by, date | Spec line |

## Needs your answer
| # | Question | Recommended | Why | Status | Written by, after your yes |

## Compose
| Item | From | To | Why |

## Steps
<numbered kit commands with input and output>

## Order
<diagram>

## Gaps
<steps no kit skill covers, one line each>

## After this playbook
<one line: what comes next for this goal once the steps are done>

## Source
<specs, notes, pull requests, live reads>
```
