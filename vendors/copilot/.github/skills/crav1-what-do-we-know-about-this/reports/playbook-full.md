# report-playbook-full

Every section: how to get one goal from its decisions to work that can be built, using the kit's skills in order. Rules: `reports/common.md`.

Preview (1.109.0). Answers through the normal skills, `apply` for a filled file (1.110.0).

Plain-language rules (1.109.1):
- Write for someone using the kit for the first time. Say the spec, the plan, the tasks; never a file name ending in `.md` in prose.
- **Kept** is not frozen. Each Kept item may be challenged: number them K1, K2, … and print the change block above the Kept items.
- Go-live or a due date is one fact among the others, not the whole story.
- Merging: offer a **merge order** (merge commits), marked **suggested, can change**. Never offer rebase as the kit's way. If someone in the sources suggested a rebase, name it as their suggestion only.
- Compose takes items from the docs only, never invented. When `docs/` describes a deploy kept apart from the others (for example a DEV Bicep deploy separate from TEST and PROD), it goes in Compose with the doc it came from.

Live reads: keep everything you read. Items outside this goal stay in, under a last block headed **Out of scope**, at the end of the live-reads section; never drop them.

Answers come first in the report. The first write stays outside the project; apply copies a filled file to docs/playbooks. The existing skills write the answers, each in the Step its row names.

Buckets:
- **Kept:** decisions already made. Do not ask them again. For each, say who decided and when, if the docs say so, with the spec line.
- **Needs your answer:** open points. For each, give a recommended answer and why. Its status is `undecided` or `decided by <person>` when the docs name one. Never write a hand-off such as "for <name> to decide".
  Conflicts (1.112.0) also go here: every `**Conflict:**` line in a covered spec, numbered C1, C2, … after the N items. For each: the decided line and the newer quote (each with its source), the recommended answer and why, and `Recorded in Step <n>` (the answer step). None found: no C items.
- **Compose:** work to put together from what exists: what splits out, or lifts from one branch or pull request into another, from where to where, and why.

Answer blocks (1.110.0). The report only lists. After writing it, ask `Walk through it now?` (1.116.0); the walk is in `references/walk.md`, read only on yes. Answers go through the normal skills, whenever the user comes back, or the filled file is read back with `apply`. Print each block word for word ABOVE its items, with the report's real numbers, the real skill and a real example drawn from this report. One instruction per line; never squeeze them into one line.

Items (1.115.1): K, N and C items are bullet blocks, never tables, so each answer sits right under its item. Item layout, one block per item, the fill-in line last and left empty:

> - **N1:** <the question in one line>. Recommended: <answer>, because <why>.
>   - From: <who raised it, date>; <status>
>   - Where: <spec section>; Recorded in Step <n>
>   - Change: <what the recommended answer changes in the spec; empty when nothing changes>
>   - Answer:

- **K items:** `**K<n>:** <the decision in one line>`, then From (who decided, date), Where, and the fill-in line `Change:` (no Answer line; an empty Change keeps the decision).
- **C items:** `**C<n>:** <the clash in one line>. Recommended: <answer>, because <why>.`, then `Decided:` and `Newer:` (each quote with its source), Where, Change, and `Answer:`.
- No separate list of fill-in lines at the end of a section.

Above the **Kept** items:

> **To change a decision under Kept** (skip if all stay as they are)
> These are decisions already made. You can still change any of them, now or later:
> 1. Nothing needs to run first.
> 2. Either run the Step named in the item (it uses `/crav1-add-to-spec` and shows the change before writing), or write the new decision on the `Change:` line right under the item in this file.
> 3. A filled file, also one others filled in, is read back with `/crav1-resolve-open-questions apply <this file>`.
>
> Example:
> ```
> - **K2:** DEV deploy has its own Bicep
>   - Change: DEV deploy runs from the shared pipeline, not its own Bicep
> ```

Above the **Needs your answer** items:

> **To answer the questions under Needs your answer**
> 1. Nothing needs to run first. <If a question needs a pull request or branch read first, name it here.>
> 2. Answer them in Step <n> (the answer step) with `/crav1-resolve-open-questions <spec>`, whenever you are ready; or write each answer on the `Answer:` line right under its item in this file (`yes` takes the recommended answer). Conflicts (C items) are settled the same way: the answer step runs `/crav1-resolve-open-questions <spec>`, which lists them, or the filled file is read back with `apply`.
> 3. A filled file, also one sent out and returned, is read back with `/crav1-resolve-open-questions apply <this file>`. It checks what changed in the specs since this report and asks about any clash before writing.
>
> Example:
> ```
> - **N1:** …
>   - Answer: yes
> - **N5:** …
>   - Answer: keep TEST and PROD on the same release branch
> - **C1:** …
>   - Answer: take the newer quote
> ```

Compose: written-out bullets, never a table. One bullet per item, 1-2 sentences: what moves, from which pull request or branch to which (short names: a branch, `PR #<n>` or a folder), and why; end with `Source: <doc>`.

Step layout: each step is its own small block, never one paragraph:

> ### Step <n>: <short title>
> **Type:**
> ```
> <exact command with its real input>
> ```
> **You should see:** <one line>
>
> **Done when:** <one line>

Steps, for a first-time user. Start the section with this line, in bold: **Run these steps in order, one at a time. You can stop and come back later.** The answer step comes first or right after the Kept changes: it runs `/crav1-resolve-open-questions <spec>` for the Needs your answer questions (or `apply <this file>` when the file was filled in), and names every N and every C it covers, noting that `/crav1-resolve-open-questions <spec>` (or `apply <this file>`) settles the C items too. Each step has:
- **Type:** the exact command, with its real input (a named spec, branch, pull request number or answer number). Never a vague pointer such as "the three under Kept" or "the tasks on feat/...": name the items and the work.
- **You should see:** what the command shows or asks.
- **Done when:** the check that tells you to move on.
Mark a step no skill covers as `manual:`, with the same three lines.
No cap on steps: as many as the work needs. List kit gaps found on the way under Gaps; do not route around them silently. No guessed range; an unnamed command goes under Gaps.

Diagram syntax (1.110.0), so every viewer renders it, also one that escapes quotes (mermaid 11.4.1 and later): node ids are plain ASCII letters and digits, never `end`, `graph` or a branch name; labels in square brackets, plain ASCII words only: letters, digits, spaces, `-`, `,`, `.`, `/` (no double quotes, parentheses, colons, `#`, `&`, backticks, `→` or `–`; write steps as `Steps 1-14`, a pull request as `PR 74`); edge labels as `-->|plain words|`; a blank line before and after each fence.

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
<change block>
<K1, K2, … as item blocks, each ending with an empty Change: line>

## Needs your answer
<answer block>
<N1, N2, …, then C1, C2, … when any, as item blocks, each ending with an empty Answer: line>

## Compose
<one bullet per item: what moves, from → to, why; Source: doc>

## Merge order
Suggested, can change.
| # | Pull request or branch | Into | Waits for |

## Steps
<bold run-in-order line, then one block per step (Step layout above)>

## Order
<diagram>

## Gaps
<steps no kit skill covers, one line each>

## After this playbook
<one line: what comes next for this goal once the steps are done>

## Source
<specs, notes, pull requests, live reads>
```
