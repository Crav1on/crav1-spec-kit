# report-playbook-full

Every section: how to get one goal from its decisions to work that can be built, using the kit's skills in order. Rules: `reports/common.md`.

Preview (1.109.0).

Plain-language rules (1.109.1):
- Write for someone using the kit for the first time. Say the spec, the plan, the tasks; never a file name ending in `.md` in prose.
- **Kept** is not frozen. Each Kept item may be challenged: say how to change it (answer `change: <new decision>` in chat; the skill named in Steps writes the change after you confirm).
- Go-live or a due date is one fact among the others, not the whole story.
- Merging: offer a **merge order** (merge commits), marked **suggested, can change**. Never offer rebase as the kit's way. If someone in the sources suggested a rebase, name it as their suggestion only.
- Compose takes items from the docs only, never invented. When `docs/` describes a deploy kept apart from the others (for example a DEV Bicep deploy separate from TEST and PROD), it goes in Compose with the doc it came from.

Live reads: keep everything you read. Items outside this goal stay in, under a last block headed **Out of scope**, at the end of the live-reads section; never drop them.

Answers come first in the report. Write nothing in the project. After the user confirms the answers, the existing skills write them (named in each row and in Steps).

Buckets:
- **Kept:** decisions already made. Do not ask them again. For each, say who decided and when, if the docs say so, with the spec line.
- **Needs your answer:** open points. For each, give a recommended answer and why. Its status is `undecided` or `decided by <person>` when the docs name one. Never write a hand-off such as "for <name> to decide".
- **Compose:** work to put together from what exists: what splits out, or lifts from one branch or pull request into another, from where to where, and why.

Steps, for a first-time user. Start the section with this line, in bold: **First confirm your answers under Needs your answer. Then run these steps in order, one at a time.** Each step has:
- **Type:** the exact command, with its real input (a named spec, branch, pull request number or answer number). Never a vague pointer such as "the three under Kept" or "the tasks on feat/...": name the items and the work.
- **You should see:** what the command shows or asks.
- **Done when:** the check that tells you to move on.
Mark a step no skill covers as `manual:`, with the same three lines.
No cap on steps. List kit gaps found on the way under Gaps; do not route around them silently.

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
<target and acceptance from the spec; the due date as one line among them>

## Where it stands
<open pull requests and branches, missing plan or tasks, blockers; live reads; Out of scope block last>

## Kept
| Decision | Decided by, date | Spec line | To change it |

## Needs your answer
| # | Question | Recommended | Why | Status | Written by, after your yes |

## Compose
| Item | From | To | Why | Source doc |

## Merge order
Suggested, can change.
| # | Pull request or branch | Into | Waits for |

## Steps
<bold confirm-first line, then numbered steps: Type / You should see / Done when>

## Order
<diagram>

## Gaps
<steps no kit skill covers, one line each>

## After this playbook
<one line: what comes next for this goal once the steps are done>

## Source
<specs, notes, pull requests, live reads>
```
