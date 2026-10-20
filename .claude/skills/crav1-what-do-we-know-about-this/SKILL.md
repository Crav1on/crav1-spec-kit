---
name: crav1-what-do-we-know-about-this
description: >-
  Answer one question about a feature, slice, resource, or not-yet-feature
  from the specs first. Read only. Write nothing. One match pass. Then
  read-only Azure and Azure DevOps checks, each tagged as a live read.
  When the git remote is not Azure Repos and marks do not name the org
  and project, derive them from Azure DevOps URLs in docs/system/repos.md.
  Check default az install paths before reporting az as not installed.
  Production stays shape and connections only, after the same yes or no
  as /crav1-read-environment. Never read data. Does not start Specify,
  Plan, or Build. Does not run another skill. A stale research note is
  shown as stale. Later skill. Not a starter
  option. Not /crav1-explain-existing-system.
disable-model-invocation: true
icon: file-search
color: cyan
---

# What's known about

The user asks about one feature, slice, resource, or not-yet-feature. You answer from the specs first. You read. You write nothing in the project.

Command: `/crav1-what-do-we-know-about-this`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The six starter options stay unchanged.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

This is not `/crav1-explain-existing-system`. Explain reads `docs/system/` first. When the picture has nothing on the question, it quotes the first paragraph of a matching spec, labelled as coming from the spec, and names this command. It does not run this command. This command reads the specs first.

This command does not run another skill. It may name one.

## Input

Everything after `/crav1-what-do-we-know-about-this`, and every `@`, is the question.

Four kinds of question:

1. **A name** — a slug, a spec title, a function name, or a resource name (for example `fn-market-data`). The exact-name match runs first.
2. **A sentence or two** — for example what is happening with a named import, and whether it is still running. Pick out the key words. Match on those.
3. **An `@` pointer** — a spec folder or a code folder. The search stays inside that path.
4. **A focus** — for example just the security bits, or only what is pending. The full read still runs. The answer shows only those sections.

A name and a sentence can sit in the same message. A focus can sit with either. An `@` limits the search.

If the message has no name, no sentence, and no `@`, stop. Ask with options only. Use the questions tool when it is available. The options are only:

1. **Name the feature, slice, or resource**
2. **@ a spec folder or a code folder**

Stop until the user picks. Do not scan the repo to pick a thing. Do not guess.

### Minutes and dumps

Read `references/inputs.md` ("Minutes and dumps") only when the input is minutes or a dump.

## Three cases

1. **A slice exists and the user named it.** They used the slug, the spec title, or `@` of that spec folder. Answer from that spec, its plan, its tasks, its Match, and its open questions.
2. **A slice exists and the user did not name it.** Find it by matching. Answer from it. Name its path.
3. **No slice.** Say so. Show what the repo, the code, and the environment notes do know. Present that as a candidate slice. Name one next command. Do not run it. Do not create a slug.

A hit only in code, in `docs/architecture/spec.md`, or in `docs/environments/marks.md`, with no slice, is case 3.

A code-only hit, with no spec and no architecture note, is also case 3. Show what the code says. Fill in **Unexplained**.

Nothing anywhere: say so. Name `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-bundle-to-specs`. Do not run them.

When case 3 has enough written down to pick one command, name that one:

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Several features, or mixed files: `/crav1-bundle-to-specs`

When nothing is written down, name those three and stop. Do not pick one.

## Match, one pass

Read `references/match.md` ("Match, one pass") only when you match the question against specs and notes.

## Repo answer, then live reads

Build the repo answer first. Then run the live reads. The chat answer waits until the live reads finish, or until the user picks Skip.

Two live reads. Both are read-only. Tag each fact `Live read.`

### Finding `az`

Read `references/live-reads.md` ("Finding `az`") only when a live read is needed.

### Azure resource settings and recent changes

Read `references/live-reads.md` ("Azure resource settings and recent changes") only when the question needs live Azure resource settings or recent changes.

### Production

Read `references/live-reads.md` ("Production") only when the question touches production.

### Azure DevOps

Read `references/live-reads.md` ("Azure DevOps") only when the question needs Azure DevOps (boards, pipelines, repos).

### When a live read fails

Read `references/live-reads.md` ("When a live read fails") only when a live read fails.

## Focus

The full read still runs, including the live reads. The answer shows **Verdict**, **Source**, and the sections the focus names.

- Security bits: guardrails, constraints, non-goals, a Security section, `docs/system/security.md` lines that match, and a live setting that is a security setting.
- What is pending: open questions, unchecked tasks, an open decision, **Either way**, and open work items and open pull requests.

A section outside the focus is left out. An empty section is still left out. Do not pad the answer back out to the full template. **Research marked stale** stays when a mark is there. A focus does not hide it.

## Answer

The chat answer follows this skill’s `assets/answer.md` (drop-in: `.claude/skills/crav1-what-do-we-know-about-this/assets/answer.md`; plugin: this skill’s `assets/answer.md`). Do not print a placeholder. Do not write the file into the project. Leave out a heading that has nothing under it. **Tracked elsewhere** stays when a live read ran, and `none` is a real line. A guess ends with `(inference, not in the docs)`.

1. **Verdict** — one line. Example shape: finished code that is switched off, and the open item is a decision.
2. **What it is** and **Why it's in this state** — two short paragraphs. Use the words the docs already use.
3. **The decision** — when one is still open. Name where it is open (the file, the heading, or the question). Each option the docs already list gets one line for and one line against, then its own checkbox task list. Do not invent an option. When the options are not written, say that, and do not invent the lists.
4. **Either way** — tasks that apply whatever is decided. An `Ask <person>: …` line uses a person, or a role, the docs already name, plus the file and heading. Do not guess a person. Do not turn a role into a name. When a slice exists and this section is shown, the last task updates that slice’s `spec.md`. Those checkboxes stay in the chat. This command does not edit `tasks.md` or `spec.md`.
5. **Do not touch** — guardrails the docs already state. Each one has the date that note or ADR gives. When the note has no date, say the date is not written. Do not invent a date.
6. **Seen only live** — a setting or a change that no doc mentions. Each line says `Live read.` A fact the docs already state stays out of this section.
7. **Research marked stale** — a `Stale since` line under `## Research findings`, or a stale block on a note that section links to. Quote the mark. Name the path. This is not **Stale notes**. Do not clear the mark.
8. **Stale notes** — an older note that disagrees with a later note, or with a live read. Say which note is wrong and what to trust instead. A short note is not stale. A research mark is not this section.
9. **Tracked elsewhere** — work items, open pull requests, and branches. When the live read ran, this section stays, and `none` is a real line. Each line says `Live read.` When the user picked Skip, leave this section out.
10. **Source** — existing slice, found slice, or no slice (candidate). Then the files and the reads used.

**Unexplained** is for a code-only hit with no spec and no architecture note. What the code shows goes there. What the code does not say stays unexplained. Leave that heading out on every other case.

A line that is a guess ends with `(inference, not in the docs)`. A fact the file or the live read shows does not get that label.

Case 3 names the next command in **Source**. It does not run it.

When the user picked Skip, **Source** includes one line: the live checks did not run, and why.

## Stop

Do not write a file. Do not edit a spec, a plan, `tasks.md`, `docs/system/`, `docs/architecture/spec.md`, `docs/environments/marks.md`, or code. Do not commit. Do not push. Do not open a pull request.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-add-to-spec`, `/crav1-explain-existing-system`, `/crav1-read-environment`, `/crav1-map-pipeline-environments`, `/crav1-plan-from-spec`, `/crav1-build-tasks`, or `/crav1-finalize-commit`.

## Hard rules

- Specs first. One feature, slice, resource, or not-yet-feature.
- Exact name first. Key words only when the exact name misses. Spec titles and Match quotes weigh highest.
- One pass. No hunt through the whole codebase. An `@` keeps the search inside that path.
- One winning slice: answer and name the path. Two or more close hits: list every one and ask. Do not guess.
- No slice: say so, show what is known, present a candidate, and name spark, ideas, or intake. Do not run it.
- Minutes or a long dump: name `/crav1-add-to-spec` and stop.
- Live reads come after the repo part. Tag each live fact `Live read.`
- When the git remote is not Azure Repos and `docs/environments/marks.md` does not name the Azure DevOps org and project, derive them from Azure DevOps URLs in `docs/system/repos.md`. Then read work items, open pull requests, and branches the same way. Tag each fact `Live read.`
- Before reporting `az` as not installed, check the default install paths on Windows, macOS, and Linux. Use that path when it is there.
- Production is shape and connections only, after the same yes or no as `/crav1-read-environment`. Never data. Never a secret value. Never a row or a blob.
- A failed live read is one prompt: the issue, a fix when there is one, Retry or Skip. Skip is the repo-only answer, with why the live checks did not run.
- A focus still runs the full read. The answer shows only those sections.
- People come from what is written. A guess is labeled `(inference, not in the docs)`.
- Write nothing. Do not run another skill. Naming one is allowed.
- Do not start Specify, Plan, or Build.
- Later skill. Not a starter option. Asking for startup options names only the six and does not run this command.
