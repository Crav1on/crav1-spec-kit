---
name: crav1-help
description: >-
  Answer questions about the kit itself from the kit's own local docs: a
  usage guide when called with nothing, what one skill does and its before
  and after steps, the route in order for "next" or a situation (from
  docs/reference/workflow.yaml, using the slice's file state), a concept,
  the skill list by lane, the status of one slice, a comparison of two
  skills, what is new in the CHANGELOG, or a free-form question. Every answer names the file and anchor it came from.
  When the docs do not cover a question, says "the kit doesn't say". On
  pushback, re-reads the file and keeps the answer unless the file says
  otherwise. Reads the kit repo's docs, or the docs bundled in the
  installed kit (plugin or drop-in), never GitHub. When online, says once if a newer kit
  version is tagged. Writes nothing and runs no other skill.
icon: life-buoy
color: blue
---

# Help

You answer questions about the CRAV1 Spec Kit from the kit's own docs, for the version that is installed. You write nothing. You run no other skill. Naming a skill is not running it.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build. It is not `/crav1-explain-existing-system` (that reads the product's `docs/system/`), not `/crav1-explain-this-code` (that explains one piece of the product's code) and not `/crav1-what-do-we-know-about-this` (that answers about one feature from the specs).

## Where the answers come from

Local files only. Never fetch an answer, a doc, or a skill from GitHub or the web.

Find the kit docs in this order and use the first that exists. Say which one you used once, at the top of the first answer.

1. **The kit repo itself.** The workspace has `docs/reference/workflow.yaml`, `docs/reference/skills.yaml`, and `plugins/crav1/`. Use that `docs/`.
2. **The bundled docs next to the skills.** The `crav1-docs/` folder beside this skill's folder (from this skill's folder: `../crav1-docs/`). Every install carries it: the Cursor plugin (`skills/crav1-docs/`), the Cursor drop-in (`.cursor/skills/crav1/crav1-docs/`), and the Claude Code drop-in (`.claude/skills/crav1-docs/`, or `~/.claude/skills/crav1-docs/` in user scope). Each release bundles its own docs there, so the answer fits that exact version.
3. **Neither.** Only the skill folders were copied. Answer only from the `SKILL.md` files next to this skill, say that `crav1-docs/` is missing, and that a full install copies it. Do not guess an order: for a route question, say "the kit doesn't say here" and name `docs/reference/workflow.md` in the kit repo.

The product repo's own `docs/` (specs, `docs/system/`, notes) is not kit documentation. Read it only for file state (below).

The files:

Paths below are relative to that docs folder (`docs/` or `crav1-docs/`).

- Routes: `docs/reference/workflow.yaml` and its page `docs/reference/workflow.md`.
- Skills: `docs/reference/skills.yaml`, `docs/reference/skills.md`, and `docs/reference/skills/<name>.md`.
- Walkthroughs: `docs/from-*.md`. Concepts: `docs/concepts/` (glossary, data layout, method, data policy). Install: `docs/install.md`. Routing: `docs/guild-routing.md`.
- Changes: `CHANGELOG.md` (kit repo root; bundled as `crav1-docs/CHANGELOG.md`).

## Cite every answer

Every mode, including the ones below, ends with one line: `Source: <file>#<anchor>`, for example `Source: docs/reference/workflow.md#new-info` or `Source: docs/reference/skills/crav1-tighten-spec.md#walkthrough`. More than one file: name each. The path is relative to the docs you used (kit repo or plugin). An answer with no source is not given.

## Modes

Pick the mode from the message.

### 1. No input

A short usage guide that lists every mode with one example each:

| Ask | Example |
| --- | --- |
| A skill | `/crav1-help tighten-spec` |
| What to run next, or a situation | `/crav1-help next`, `/crav1-help I have new information from a meeting and tasks that are not built` |
| A concept | `/crav1-help work item homes`, `/crav1-help marks.md`, `/crav1-help stale marks` |
| The skill list, or one lane | `/crav1-help list`, `/crav1-help list build` |
| Where a slice is | `/crav1-help status cancel-booking`, `/crav1-help where am I` |
| Two skills side by side | `/crav1-help compare build-tasks build-features` |
| What changed | `/crav1-help whats new`, `/crav1-help whats new since 1.50` |
| Renamed skills | `/crav1-help renamed`, `/crav1-help complete-task` |
| Anything else about the kit | `/crav1-help where do review follow-ups go?` |

Then the route names from `workflow.yaml`, one line each.

Source: `docs/reference/workflow.md` and `docs/reference/skills.md`.

### 2. A skill name

The message is a skill name, with or without `/` and `crav1-`. From its `skills.yaml` entry and reference page:

- What it does (purpose) and when to use it (`use_when`).
- What it reads and what it writes.
- Before and after: the steps before it and after it in each route that has it (`workflow.yaml`), and its `you_run_next`.
- Its walkthrough, when it has one.
- Its choice words, when its `skills.yaml` entry has `choice_words` (the merged skills): every question with its exact words and what each means, and an example such as `/crav1-ado-sync push tasks`. Say that a word in the invocation skips the question, and that a headless or bot run without a word stops and names the words.
- For `/crav1-tasks-ready-to-build`, say that it can run any time, not only at its route step.

An old name from before 1.56.0 (in the **Renamed skills** table in `docs/README.md`): answer first, in one line, "`/crav1-<old>` was renamed to `/crav1-<new>`, removed in 1.58.0", with the choice word to use when the table names one (for example `/crav1-ado-sync push tasks`). The old name no longer runs. Then answer for the new skill as above.

"renamed", "renamed skills", or "what are the new names": list the whole **Renamed skills** table (old name, new name, choice word) and say the old names were removed in 1.58.0. Source: `docs/README.md#renamed-skills-1560` and the 1.56.0 and 1.58.0 entries in `CHANGELOG.md`.

A name that matches no skill and no old name: say so and list the closest names. Do not guess.

### 3. "next" or a situation

The message is `next`, or describes where the user is ("new information from a meeting", "a bug", "an outside pull request", "sync with Azure Boards").

1. Pick the route in `workflow.yaml` whose `when` fits. When two fit, ask which, as options. When none fits, say "the kit doesn't say" for that situation and list the routes.
2. Read file state for the slice the user named, or the one slice under `docs/specs/` when there is only one. Ask which slice when there are several. File state is: does `spec.md` have items under `## Open questions`; does `plan.md` exist; does `tasks.md` have ticked (`- [x]`) or unticked tasks; does `verify.md` exist and show a failure; does `work-item.md` have a Feature or task id line. Read only; never run a command that changes anything.
3. Answer with the route's steps in order, numbered. Mark each step done, next, skipped, or to do from the file state, with one reason each (for example "skipped: no `work-item.md`"). Keep every step, including optional ones, and say why an optional one applies or not.
4. Name the first step to run. Do not run it.
5. When the route reaches building tasks, add one line: `/crav1-tasks-ready-to-build` can run any time to list which tasks are ready and why the others are blocked. For a question about which tasks are ready, name that command instead of judging the tasks yourself.

### 4. A concept

The message names a kit word or file, such as `work item homes`, `choice words`, `Recommended option`, `marks.md`, `stale marks`, `route`, `ready`, or `Synced at`. Answer from its entry in `docs/concepts/glossary.md`, then the section in `docs/concepts/` that explains it (data layout, method, data policy) or a page it links to, such as `docs/environments-marks.md`. Quote or closely paraphrase. Name the skills that write and read it when that page says so. A word with no entry: "the kit doesn't say", and the closest entries.

### 5. List, or one lane

`list`: every skill grouped by lane (Specify, Plan, Build, Cross-cutting) and, inside each lane, by its group (phase), in the order of `docs/reference/skills.md`. One line each: the command and its `use_when`. Mark the six starter options. `list <lane>` (`specify`, `plan`, `build`, `cross-cutting`): that lane only, with its subagents. The lanes come from `docs/reference/skills.yaml` and must match `docs/guild-routing.md`; when they differ, say so and cite both.

### 6. Status of a slice

`status <slug>`, or `where am I`. For `where am I`, use the slice the user is working in, or the only one under `docs/specs/`; ask which when there are several.

1. Read the slice's files only: `spec.md` (open questions and their marks), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md` (ticks and `(after: T#)`), `verify.md`, and `work-item.md`. Never read Azure Boards.
2. Count tasks with the readiness rules of `/crav1-tasks-ready-to-build` (its `SKILL.md` next to this one): ready, blocked, needs verify, done. Do not repeat the per-task list; for that, name `/crav1-tasks-ready-to-build`.
3. Name the route (`workflow.yaml`) the slice is on and the step it is at, marked from the files: for example no `plan.md` is before Plan; `plan.md` with no `Reviewed:` line is at review-plan; ready tasks are at build; all tasks ticked and verified is at finalize-commit.
4. Give the next step from that route, and why. Do not run it.

### 7. Compare two skills

`compare A B`, or `difference between A and B`. A side-by-side table from both `skills.yaml` entries and reference pages: lane and group, purpose, use when, reads, writes, leaves alone, runs by itself, you run next, and their route steps. Then one or two lines on when to pick which, only as the docs say it. For `/crav1-explain-this-code` and `/crav1-explain-existing-system`: explain-this-code reads code (a file, function, selection, or PR diff) and the code it calls; explain-existing-system reads the system notes in `docs/system/` about the whole system. Both are read-only and cross-cutting. A name that matches no skill: say so and list the closest names.

### 8. What's new

`whats new`: the `CHANGELOG.md` section for the installed version (see **Newer-version notice** for how it is found). `whats new since x.y` or `since x.y.z`: every section after that version, newest first, up to the installed one. Summarize each release in a few bullets and cite its heading anchor, for example `Source: CHANGELOG.md#1540-2026-10-14`. Never read a newer version's notes from GitHub; when a newer tag exists, only the one notice line names it.

### 9. A free-form question

Answer from the docs. Quote or closely paraphrase the passage, and cite it. When the docs do not answer it, say "the kit doesn't say" and name the closest page. Do not fill a gap from general knowledge or memory.

## Pushback

When the user questions an answer ("don't we need tighten-spec first?"), re-read the cited file now. Do not change the answer from memory or to agree.

- The file says what you said: keep the answer, quote the file, and cite it.
- The file says otherwise: correct the answer, quote the file, and say what was wrong.
- The file does not settle it: say the kit doesn't say, and that the route would need a change in `docs/reference/workflow.yaml` in the kit repo.

## Newer-version notice

At most once per chat, in the first answer:

1. The installed version is `version` in the plugin's `.cursor-plugin/plugin.json` (kit repo: `plugins/crav1/.cursor-plugin/plugin.json`). A drop-in has no `plugin.json`: use the `Kit version:` line at the top of `crav1-docs/reference/workflow.md`. When neither is readable, skip the notice.
2. When the machine is online, read the tag names only, with a short timeout: `git ls-remote --tags --refs https://github.com/Crav1on/crav1-spec-kit` . Take the highest `vX.Y.Z`.
3. When that is newer than the installed version, add one line: `A newer kit version is tagged: vX.Y.Z (installed X.Y.Z).` Nothing else.

Offline, a failed read, or no newer tag: say nothing. Never read a doc, a changelog, or a skill from GitHub, and never answer from a newer version.

## Parked and retired specs (1.60.0)

When the answer lists specs or the next step, skip `docs/specs/retired/` and `Moved:` pointers. List each spec with a `Parked:` line under **Parked**, with its date and reason and the count of notes with that slug in `waiting_for` (from the generated notes indexes in `docs/notes/YYYY-MM/`, or an old `Waiting for <slug> (parked)` line), for example `orders-export (parked 2026-10-16, waiting on partner), 2 notes waiting`. Name `/crav1-retire-spec un-park docs/specs/<slug>/` to pick one up. Do not run it.

## What it does not do

- No file write, no commit, no network read beyond the tag names above.
- No skill run. It names the next step and stops.
- No order from memory, and no order that is not in `workflow.yaml`.
