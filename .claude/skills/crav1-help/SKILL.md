---
name: crav1-help
description: >-
  Answer questions about the kit itself from the kit's own local docs: a
  usage guide when called with nothing, what one skill does and its before
  and after steps, the route in order for "next" or a situation (from
  docs/reference/workflow.yaml, using the slice's file state), or a
  free-form question. Every answer names the file and anchor it came from.
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

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build. It is not `/crav1-explain` (that reads the product's `docs/system/`) and not `/crav1-whats-known-about` (that answers about one feature from the specs).

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

## Cite every answer

End every answer with one line: `Source: <file>#<anchor>`, for example `Source: docs/reference/workflow.md#new-info` or `Source: docs/reference/skills/crav1-tighten-spec.md#walkthrough`. More than one file: name each. The path is relative to the docs you used (kit repo or plugin). An answer with no source is not given.

## Modes

Pick the mode from the message.

### 1. No input

A short usage guide:

- What this command answers: what a skill does, what to run next, the order for a situation, and questions about the kit.
- Four or five example questions, such as `/crav1-help`, `/crav1-help tighten-spec`, `/crav1-help next`, `/crav1-help I have new information from a meeting and tasks that are not built`, `/crav1-help where do review follow-ups go?`.
- The route names from `workflow.yaml`, one line each.

Source: `docs/reference/workflow.md` and `docs/reference/skills.md`.

### 2. A skill name

The message is a skill name, with or without `/` and `crav1-`. From its `skills.yaml` entry and reference page:

- What it does (purpose) and when to use it (`use_when`).
- What it reads and what it writes.
- Before and after: the steps before it and after it in each route that has it (`workflow.yaml`), and its `you_run_next`.
- Its walkthrough, when it has one.
- For `/crav1-tasks-ready-to-build`, say that it can run any time, not only at its route step.

A name that matches no skill: say so and list the closest names. Do not guess.

### 3. "next" or a situation

The message is `next`, or describes where the user is ("new information from a meeting", "a bug", "an outside pull request", "sync with Azure Boards").

1. Pick the route in `workflow.yaml` whose `when` fits. When two fit, ask which, as options. When none fits, say "the kit doesn't say" for that situation and list the routes.
2. Read file state for the slice the user named, or the one slice under `docs/specs/` when there is only one. Ask which slice when there are several. File state is: does `spec.md` have items under `## Open questions`; does `plan.md` exist; does `tasks.md` have ticked (`- [x]`) or unticked tasks; does `verify.md` exist and show a failure; does `work-item.md` have a Feature or task id line. Read only; never run a command that changes anything.
3. Answer with the route's steps in order, numbered. Mark each step done, next, skipped, or to do from the file state, with one reason each (for example "skipped: no `work-item.md`"). Keep every step, including optional ones, and say why an optional one applies or not.
4. Name the first step to run. Do not run it.
5. When the route reaches building tasks, add one line: `/crav1-tasks-ready-to-build` can run any time to list which tasks are ready and why the others are blocked. For a question about which tasks are ready, name that command instead of judging the tasks yourself.

### 4. A free-form question

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

## What it does not do

- No file write, no commit, no network read beyond the tag names above.
- No skill run. It names the next step and stops.
- No order from memory, and no order that is not in `workflow.yaml`.
