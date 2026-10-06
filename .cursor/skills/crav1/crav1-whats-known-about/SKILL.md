---
name: crav1-whats-known-about
description: >-
  Answer one question about a feature, slice, resource, or not-yet-feature
  from the specs first. Read only. Write nothing. One match pass. Then
  read-only Azure and Azure DevOps checks, each tagged as a live read.
  Production stays shape and connections only, after the same yes or no
  as /crav1-environment-read. Never read data. Does not start Specify,
  Plan, or Build. Does not run another skill. Later skill. Not a starter
  option. Not /crav1-explain.
disable-model-invocation: true
icon: file-search
color: cyan
---

# What's known about

The user asks about one feature, slice, resource, or not-yet-feature. You answer from the specs first. You read. You write nothing in the project.

Command: `/crav1-whats-known-about`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

This is not `/crav1-explain`. Explain reads `docs/system/` and does not open a spec to answer the question. This command reads the specs first.

This command does not run another skill. It may name one.

## Input

Everything after `/crav1-whats-known-about`, and every `@`, is the question.

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

Pasted minutes, a transcript, or a long dump are out of scope. Do not extract items. Do not answer from the paste.

- Minutes or a transcript: name `/crav1-meeting-to-specs` and stop.
- A dump of notes, tickets, old docs, diagrams, or screenshots: name `/crav1-match-dump-to-specs` and stop.

A sentence or two is in scope. A long dump is not.

## Three cases

1. **A slice exists and the user named it.** They used the slug, the spec title, or `@` of that spec folder. Answer from that spec, its plan, its tasks, its Match, and its open questions.
2. **A slice exists and the user did not name it.** Find it by matching. Answer from it. Name its path.
3. **No slice.** Say so. Show what the repo, the code, and the environment notes do know. Present that as a candidate slice. Name one next command. Do not run it. Do not create a slug.

A hit only in code, in `docs/architecture/spec.md`, or in `docs/environments/marks.md`, with no slice, is case 3.

A code-only hit, with no spec and no architecture note, is also case 3. Show what the code says. Fill in **Unexplained**.

Nothing anywhere: say so. Name `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs`. Do not run them.

When case 3 has enough written down to pick one command, name that one:

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Several features, or mixed files: `/crav1-intake-to-specs`

When nothing is written down, name those three and stop. Do not pick one.

## Match, one pass

One pass. Do not hunt through the whole codebase. Do not open a second search after the first comes back.

Places, in this order when the user did not `@` a path:

- spec titles in `docs/specs/<slug>/spec.md` (skip `_template`)
- `tasks.md` in those folders
- Match quotes (`## Match` in those `spec.md` files)
- `docs/system/`
- `docs/architecture/spec.md`
- `docs/environments/marks.md`
- one exact-name code query, then, only when that exact name misses, one key-word code query

An `@` of a spec folder or a code folder replaces that list. The search stays inside that path. Do not search specs outside a code folder they named. Say that the search stayed in the path.

**Exact name first.** A slug, a spec title, a function name, or a resource name is a whole token. Case-sensitive first. A case-insensitive hit counts only when it is the only hit.

**Key words when the exact name misses.** Match the key words against the same places. Spec titles and Match quotes weigh highest. A glossary row is a word, not a slice. A neighbor name is not a hit.

**One slice clearly wins.** Answer from it (case 1 or case 2) and name the path `docs/specs/<slug>/`.

**Two or more close hits.** List every one, one line each: the path and the title line. Ask which. Use the questions tool when it is available. One option per hit. Do not guess. Do not drop one to keep the list short. Stop until the user picks. Then answer from that slice.

**No slice.** Case 3.

Reading the winning slice is the answer, not a second pass. Read that `spec.md`, `plan.md` and `tasks.md` when they exist, `## Match`, and `## Open questions`. Use the hits the same pass already found in `docs/system/`, `docs/architecture/spec.md`, and `docs/environments/marks.md`.

## Repo answer, then live reads

Build the repo answer first. Then run the live reads. The chat answer waits until the live reads finish, or until the user picks Skip.

Two live reads. Both are read-only. Tag each fact `Live read.`

### Azure resource settings and recent changes

Use `az` to list and show. Do not create, update, delete, deploy, start, stop, or set a resource. Do not switch subscription. One pass on the current account.

- `az account show` for the current account
- `az resource list` for a resource whose name matches the thing
- `az resource show` for that resource’s settings
- `az monitor activity-log list` for recent changes on that resource id

Recent changes are the operation name, the status, the time, and the caller when the log shows a name. No request body. No payload.

Do not print a secret, a key, a password, a connection string, or a token. A secret name may be cited. The secret value is not. A setting value is shown only when it is a resource id or a hostname, or when the resource is non-prod and the value is not a secret.

Do not read request logs, metrics, or traffic. Do not open a database. Do not open storage. Never a row. Never a blob.

A resource name that is not in the question and not in the repo answer: this live read does not apply. Say so. That is not a failure.

### Production

Production follows `/crav1-environment-read` (drop-in: `.cursor/skills/crav1/crav1-environment-read/SKILL.md`, the pre-prod, shared, and prod-only rule; plugin: sibling `skills/crav1-environment-read/SKILL.md`).

Prod-only means the only mark is production. A similar name on another resource is not a twin. Pre-prod, shared-with-prod, and prod-only stay shape and connections only, after the same yes or no.

When a matched resource is pre-prod, shared with prod, or prod-only, ask before it is read. Use the questions tool when it is available. The options are only:

1. **Yes. Read these for shape and connections only.**
2. **No. Leave them unread.**

Stop until the user picks. One answer covers every such resource this pass listed.

Shape and connections means names, types, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Say `prod only` on a prod-only resource. Say `Shape and connections only.` Never data. Never secret values. Never a row or a blob. A yes does not open a production database or production storage.

A no leaves those resources unread. The answer says they were not read.

A non-prod resource (dev, test, stage, uat, qa) is settings and recent changes, as above. It does not need that yes. It is still never data and never a secret value.

### Azure DevOps

Work items, open pull requests, and branches that touch the thing.

This read applies when the git remote is Azure Repos (`dev.azure.com` or `*.visualstudio.com`), or when `docs/environments/marks.md` already names the Azure DevOps org and project. Use that org and project. Do not ask for a typed path. Do not guess an org.

Use `az boards` and `az repos` to list and show. Do not edit a work item, a pull request, or a branch. Do not pass `--work-items`. Do not create a work item.

- work items whose title contains the name
- open pull requests whose title or source branch touches the thing
- branches whose name touches the thing

When the remote is not Azure Repos and the marks file does not name an org and project, this read does not apply. Say so under **Tracked elsewhere**. That is not a failure.

### When a live read fails

The repo part is already done. A failure is `az` missing, `az` not signed in, the `azure-devops` extension missing, or no access to the DevOps project. A read that does not apply is not a failure.

Show one prompt. State each failure. Suggest a fix when there is one. `az login`, then retry, when the login is missing. Name a missing `az` or a missing `azure-devops` extension. Do not install. Do not log in. Do not run `az login`.

Use the questions tool when it is available. The options are only:

1. **Retry**
2. **Skip**

Stop until the user picks.

**Retry** runs the failed reads again. Keep a live fact that already succeeded. Do not ask another question in that turn. If the retry fails, show the same prompt again. Do not answer with a partial live read.

**Skip** gives the repo-only answer. One line says the live checks did not run, and why. Do not mix a partial live read into that answer.

Do not ask the production question in the same turn as the failure prompt. That question comes after the Azure list succeeds.

## Focus

The full read still runs, including the live reads. The answer shows **Verdict**, **Source**, and the sections the focus names.

- Security bits: guardrails, constraints, non-goals, a Security section, `docs/system/security.md` lines that match, and a live setting that is a security setting.
- What is pending: open questions, unchecked tasks, an open decision, **Either way**, and open work items and open pull requests.

A section outside the focus is left out. An empty section is still left out. Do not pad the answer back out to the full template.

## Answer

The chat answer follows this skill’s `assets/answer.md` (drop-in: `.cursor/skills/crav1/crav1-whats-known-about/assets/answer.md`; plugin: this skill’s `assets/answer.md`). Do not print a placeholder. Do not write the file into the project. Leave out a heading that has nothing under it. **Tracked elsewhere** stays when a live read ran, and `none` is a real line. A guess ends with `(inference, not in the docs)`.

1. **Verdict** — one line. Example shape: finished code that is switched off, and the open item is a decision.
2. **What it is** and **Why it's in this state** — two short paragraphs. Use the words the docs already use.
3. **The decision** — when one is still open. Name where it is open (the file, the heading, or the question). Each option the docs already list gets one line for and one line against, then its own checkbox task list. Do not invent an option. When the options are not written, say that, and do not invent the lists.
4. **Either way** — tasks that apply whatever is decided. An `Ask <person>: …` line uses a person, or a role, the docs already name, plus the file and heading. Do not guess a person. Do not turn a role into a name. When a slice exists and this section is shown, the last task updates that slice’s `spec.md`. Those checkboxes stay in the chat. This command does not edit `tasks.md` or `spec.md`.
5. **Do not touch** — guardrails the docs already state. Each one has the date that note or ADR gives. When the note has no date, say the date is not written. Do not invent a date.
6. **Seen only live** — a setting or a change that no doc mentions. Each line says `Live read.` A fact the docs already state stays out of this section.
7. **Stale notes** — an older note that disagrees with a later note, or with a live read. Say which note is wrong and what to trust instead. A short note is not stale.
8. **Tracked elsewhere** — work items, open pull requests, and branches. When the live read ran, this section stays, and `none` is a real line. When the user picked Skip, leave this section out.
9. **Source** — existing slice, found slice, or no slice (candidate). Then the files and the reads used.

**Unexplained** is for a code-only hit with no spec and no architecture note. What the code shows goes there. What the code does not say stays unexplained. Leave that heading out on every other case.

A line that is a guess ends with `(inference, not in the docs)`. A fact the file or the live read shows does not get that label.

Case 3 names the next command in **Source**. It does not run it.

When the user picked Skip, **Source** includes one line: the live checks did not run, and why.

## Stop

Do not write a file. Do not edit a spec, a plan, `tasks.md`, `docs/system/`, `docs/architecture/spec.md`, `docs/environments/marks.md`, or code. Do not commit. Do not push. Do not open a pull request.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-match-dump-to-specs`, `/crav1-meeting-to-specs`, `/crav1-explain`, `/crav1-environment-read`, `/crav1-pipeline-environments`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-add-to-spec`, or `/crav1-finalize-commit`.

## Hard rules

- Specs first. One feature, slice, resource, or not-yet-feature.
- Exact name first. Key words only when the exact name misses. Spec titles and Match quotes weigh highest.
- One pass. No hunt through the whole codebase. An `@` keeps the search inside that path.
- One winning slice: answer and name the path. Two or more close hits: list every one and ask. Do not guess.
- No slice: say so, show what is known, present a candidate, and name spark, ideas, or intake. Do not run it.
- Minutes or a long dump: name `/crav1-meeting-to-specs` or `/crav1-match-dump-to-specs` and stop.
- Live reads come after the repo part. Tag each live fact `Live read.`
- Production is shape and connections only, after the same yes or no as `/crav1-environment-read`. Never data. Never a secret value. Never a row or a blob.
- A failed live read is one prompt: the issue, a fix when there is one, Retry or Skip. Skip is the repo-only answer, with why the live checks did not run.
- A focus still runs the full read. The answer shows only those sections.
- People come from what is written. A guess is labeled `(inference, not in the docs)`.
- Write nothing. Do not run another skill. Naming one is allowed.
- Do not start Specify, Plan, or Build.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
