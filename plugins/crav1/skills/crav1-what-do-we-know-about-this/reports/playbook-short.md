# report-playbook-short

One screen: how to get one goal (a milestone, a release, a set of agreed changes) from its decisions to work that can be built, using the kit's skills in order. Rules: `reports/common.md`.

Preview (1.109.0).

Plain-language rules (1.109.1):
- Write for someone using the kit for the first time. Say the spec, the plan, the tasks; never a file name ending in `.md` in prose.
- **Kept** is not frozen. Each Kept item may be challenged: number them K1, K2, … and print the change block below under Kept.
- Go-live or a due date is one fact among the others, not the whole story.
- Merging: offer a **merge order** (merge commits), marked **suggested, can change**. Never offer rebase as the kit's way. If someone in the sources suggested a rebase, name it as their suggestion only.
- Compose takes items from the docs only, never invented. When `docs/` describes a deploy kept apart from the others (for example a DEV Bicep deploy separate from TEST and PROD), it goes in Compose with the doc it came from.

Live reads: keep everything you read. Items outside this goal stay in, under a last block headed **Out of scope**, at the end of the live-reads section; never drop them.

Answers come first in the report. Write nothing in the project. After the user confirms the answers, the existing skills write them (named in Steps).

Buckets:
- **Kept:** decisions already made. Do not ask them again. For each, say who decided and when, if the docs say so.
- **Needs your answer:** open points. For each, give a recommended answer and why. Its status is `undecided` or `decided by <person>` when the docs name one. Never write a hand-off such as "for <name> to decide".
- **Compose:** work to put together from what exists: what splits out, or lifts from one branch or pull request into another, and why.

Answer blocks (1.109.2). Print each block word for word under its heading, with the report's real numbers, the real skill and a real example drawn from this report. One instruction per line; never squeeze them into one line.

Under **Kept**, after the table:

> **To change a decision under Kept** (skip if all stay as they are)
> These are decisions already made. You can still change any of them:
> 1. Nothing needs to run first.
> 2. Write in this chat, one line per change: `change: K<n> <new decision>`
> 3. Then run the steps under Steps. The step that names K<n> runs the skill that writes the change (for example `/crav1-add-to-spec`); it shows the change and asks you to confirm.
>
> Example:
> ```
> change: K2 DEV deploy runs from the shared pipeline, not its own Bicep
> ```

Under **Needs your answer**, after the table:

> **To answer the questions under Needs your answer**
> 1. Before you answer: nothing needs to run first. <If a question needs a pull request or branch read first, name it here.>
> 2. Write in this chat, in one message:
>    - to accept every recommended answer: `yes N1–N<last>`
>    - to accept some and give your own for others, one line each: `yes N1–N4, N6–N<last>`, then `N5: <your answer>`
> 3. Then run the steps under Steps, from step 1. The step that writes each answer names its number.
>
> Example:
> ```
> yes N1–N4, N6–N12
> N5: keep TEST and PROD on the same release branch
> ```

Compose table: keep columns balanced. **From** and **To** hold a short name only (a branch, `PR #<n>` or a folder; about 30 characters at most). Put the full path or long title under **Source doc** and the reasoning under **Why**.

Step layout: each step is its own small block, never one paragraph:

> ### Step <n>: <short title>
> **Type:**
> ```
> <exact command with its real input>
> ```
> **You should see:** <one line>
>
> **Done when:** <one line>

Steps, for a first-time user. Start the section with this line, in bold: **First confirm your answers under Needs your answer. Then run these steps in order, one at a time.** Each step has:
- **Type:** the exact command, with its real input (a named spec, branch, pull request number or answer number). Never a vague pointer such as "the three under Kept" or "the tasks on feat/...": name the items and the work.
- **You should see:** what the command shows or asks.
- **Done when:** the check that tells you to move on.
Mark a step no skill covers as `manual:`, with the same three lines.
At most 8 steps. If there are more, the last line says `More steps: report-playbook-full`.

Diagrams: one `flowchart` of the dependency order, only when 3 or more steps depend on each other. No C4.

```markdown
# <Goal>: playbook

## Verdict
<one line: what stands between the goal and buildable work>

## Goal
<target, due date with its source>

## Kept
<numbered K1, K2, …>
<change block>

## Needs your answer
<numbered N1, N2, …: question, recommended answer, why, status>
<answer block>

## Compose
<bullets: item, from → to as short names, why, source doc>

## Merge order
<suggested, can change: pull requests or branches in merge order, merge commits>

## Steps
<bold confirm-first line, then one block per step (Step layout above); at most 8>

## Order
<diagram, if any>

## What we read
<live reads; Out of scope block last>

## Source
<specs, notes, pull requests, live reads>
```
