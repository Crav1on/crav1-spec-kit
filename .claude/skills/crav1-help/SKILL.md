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
  version is tagged. `todo` ranks what to do next.
  Writes nothing and runs no other skill.
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
2. **The bundled docs next to the skills.** The `crav1-docs/` folder beside this skill's folder (from this skill's folder: `../crav1-docs/`). Every install carries it: the Cursor plugin (`skills/crav1-docs/`), the Cursor drop-in (`.claude/skills/crav1-docs/`), and the Claude Code drop-in (`.claude/skills/crav1-docs/`, or `~/.claude/skills/crav1-docs/` in user scope). Each release bundles its own docs there, so the answer fits that exact version.
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
| What to do now | `/crav1-help todo next pr71` |
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
- Its choice words, when its `skills.yaml` entry has `choice_words` (the merged skills): every question with its exact words and what each means, plus its `note` line when it has one (such as `After a PR: all`), and an example such as `/crav1-ado-sync push tasks`. Say that a word in the invocation skips the question, and that a headless or bot run without a word stops and names the words.
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

Read `references/status.md` ("6. Status of a slice") only when the user asks for the status of a slice.

Read `references/todo.md` only on `todo`.

### 7. Compare two skills

Read `references/modes.md` ("7. Compare two skills") only when the user asks to compare two skills.

### 8. What's new

Read `references/modes.md` ("8. What's new") only when the user asks what's new.

### 9. A free-form question

Answer from the docs. Quote or closely paraphrase the passage, and cite it. When the docs do not answer it, say "the kit doesn't say" and name the closest page. Do not fill a gap from general knowledge or memory.

## Pushback

When the user questions an answer ("don't we need tighten-spec first?"), re-read the cited file now. Do not change the answer from memory or to agree.

- The file says what you said: keep the answer, quote the file, and cite it.
- The file says otherwise: correct the answer, quote the file, and say what was wrong.
- The file does not settle it: say the kit doesn't say, and that the route would need a change in `docs/reference/workflow.yaml` in the kit repo.

## Newer-version notice

Read `references/modes.md` ("Newer-version notice") only when a newer kit version may exist.

## Parked and retired specs (1.60.0)

Read `references/modes.md` ("Parked and retired specs (1.60.0)") only when a slice is parked or retired.

## What it does not do

- No file write, no commit, no network read beyond the tag names above, except a `todo` PR lookup after a yes.
- No skill run. It names the next step and stops.
- No order from memory, and no order that is not in `workflow.yaml`.


## Choice words (1.69.0)

- Todo: `todo` / `todo next` / `todo top N`, then an optional scope.
- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
