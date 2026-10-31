---
name: crav1-what-do-we-know-about-this
description: >-
  Use when the user asks what we know about a feature, slice, resource, or
  idea. Answers from the specs first with read-only live checks; a
  report-<type>-<depth> word writes one Markdown report outside the project.
  Writes nothing in the project. Does not run another skill.
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

## Report words (1.104.0)

Route first, load second. Check the message for one word `report-<type>-<depth>`:

- **No report word:** the free-form answer below, unchanged. Do not open `reports/`.
- **One report word:** type `feature` (what it does, flow, architecture), `change` (a pull request or branch, its pipelines, the discussion), `build` (ready to build, what is missing, finish order), or `playbook` (1.109.0, preview: what is kept, what needs your answer, what to compose, and the kit skills in order to reach buildable work; answers stay in the report until the user confirms); depth `short` or `full`. Read only `reports/common.md` and `reports/<type>-<depth>.md`. Never the other report files. The rest of the message is the question, matched as below.

That one report file names its sections and the only diagrams to draw. The report is the one file this command writes, outside the project; the chat always links or attaches it.

## Input

Everything after `/crav1-what-do-we-know-about-this`, and every `@`, is the question.

Four kinds of question:

1. **A name** — a slug, a spec title, a function name, or a resource name (for example `fn-market-data`). The exact-name match runs first.
2. **A sentence or two** — for example what is happening with a named import, and whether it is still running. Pick out the key words. Match on those.
3. **An `@` pointer** — a spec folder or a code folder. The search stays inside that path.
4. **A focus** — for example just the security bits, or only what is pending. The full read still runs. The answer shows only those sections.

A name and a sentence can sit in the same message. A focus can sit with either. An `@` limits the search.

If the message has no name, no sentence, and no `@`, stop. Ask with options only. The options are only:

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

Read `references/live-reads.md`, only the section you need:

- "Finding `az`": when a live read is needed.
- "Azure resource settings and recent changes": when the question needs live Azure resource settings or recent changes.
- "Production": when the question touches production.
- "Azure DevOps": when the question needs Azure DevOps (boards, pipelines, repos).
- "When a live read fails": when a live read fails.

## Focus

A focus still runs the full read, including the live reads, and shows only **Verdict**, **Source**, and the focused sections. Read `references/focus.md` ("Focus") only when the question names a focus.

## Answer

The chat answer follows this skill’s `assets/answer.md` (this skill's `assets/answer.md`). Do not print a placeholder. Do not write the file into the project. Leave out a heading that has nothing under it. **Tracked elsewhere** stays when a live read ran, and `none` is a real line. A guess ends with `(inference, not in the docs)`.

Read `references/answer.md` ("Answer sections") when you write the answer: what each section holds (Verdict through Source, and **Unexplained**), the guess label, the open-question `Next:` line, and the Skip line in **Source**. Case 3 names the next command in **Source**. It does not run it.

## Stop

Do not write a file, except the one report a `report-*` word asks for, outside the project. Do not edit a spec, a plan, `tasks.md`, `docs/system/`, `docs/architecture/spec.md`, `docs/environments/marks.md`, or code. Do not commit. Do not push. Do not open a pull request.

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
- Write nothing in the project. A `report-*` word writes one report outside it and links it in chat. Do not run another skill. Naming one is allowed.
- Do not start Specify, Plan, or Build.
- Later skill. Not a starter option. Asking for startup options names only the six and does not run this command.
