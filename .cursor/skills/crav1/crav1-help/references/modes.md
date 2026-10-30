# crav1-help: modes

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 (modes 7, 8, notices) and 1.86.2 (sources case Neither, modes 2 to 5); the rules are unchanged.

## Neither: no kit docs

Only the skill folders were copied. Answer only from the `SKILL.md` files next to this skill, say that `crav1-docs/` is missing, and that a full install copies it. Do not guess an order: for a route question, say "the kit doesn't say here" and name `docs/reference/workflow.md` in the kit repo.

### 2. A skill name

The message is a skill name, with or without `/` and `crav1-`. From its `reference/index.yaml` entry and its page `reference/skills/<name>.md` (not the whole skills list):

- What it does (purpose) and when to use it (`use_when`).
- What it reads and what it writes.
- Before and after: the steps before it and after it in each route that has it (`workflow.yaml`), and its `you_run_next`.
- Its walkthrough, when it has one.
- Its choice words, when its page has a Choice words section (the merged skills): every question with its exact words and what each means, plus its `note` line when it has one (such as `After a PR: all`), and an example such as `/crav1-ado-sync push tasks`. Say that a word in the invocation skips the question, and that a headless or bot run without a word stops and names the words.
- For `/crav1-tasks-ready-to-build`, say that it can run any time, not only at its route step.

An old name from before 1.56.0 (in the **Renamed skills** table in `README.md`): answer first, in one line, "`/crav1-<old>` was renamed to `/crav1-<new>`, removed in 1.58.0", with the choice word to use when the table names one (for example `/crav1-ado-sync push tasks`). The old name no longer runs. Then answer for the new skill as above.

"renamed", "renamed skills", or "what are the new names": list the whole **Renamed skills** table (old name, new name, choice word) and say the old names were removed in 1.58.0. Source: `README.md#renamed-skills-1560` and the 1.56.0 and 1.58.0 entries in `CHANGELOG.md`.

A name that matches no skill and no old name: say so and list the closest names. Do not guess.

### 3. "next" or a situation

The message is `next`, or describes where the user is ("new information from a meeting", "a bug", "an outside pull request", "sync with Azure Boards").

1. Pick the route in `workflow.yaml` whose `when` fits. When two fit, ask which, as options. When none fits, say "the kit doesn't say" for that situation and list the routes.
2. Read file state for the slice the user named, or the one slice under `docs/specs/` when there is only one. Ask which slice when there are several. File state is: does `spec.md` have items under `## Open questions`; does `plan.md` exist; does `tasks.md` have ticked (`- [x]`) or unticked tasks; does `verify.md` exist and show a failure; does `work-item.md` have a Feature or task id line. Read only; never run a command that changes anything.
3. Answer with the route's steps in order, numbered. Mark each step done, next, skipped, or to do from the file state, with one reason each (for example "skipped: no `work-item.md`"). Keep every step, including optional ones, and say why an optional one applies or not.
4. Name the first step to run. Do not run it.
5. When the route reaches building tasks, add one line: `/crav1-tasks-ready-to-build` can run any time to list which tasks are ready and why the others are blocked. For a question about which tasks are ready, name that command instead of judging the tasks yourself.

### 4. A concept

The message names a kit word or file, such as `work item homes`, `choice words`, `Recommended option`, `marks.md`, `stale marks`, `route`, `ready`, or `Synced at`. Answer from its entry in `concepts/glossary.md`, then the section in `concepts/` that explains it (data layout, method, data policy) or a page it links to, such as `environments-marks.md`. Quote or closely paraphrase. Name the skills that write and read it when that page says so. A word with no entry: "the kit doesn't say", and the closest entries.

### 5. List, or one lane

`list`: every skill grouped by lane (Specify, Plan, Build, Cross-cutting) and, inside each lane, by its group (phase), in the order of `reference/skills.md`. One line each: the command and its `use_when`. Mark the six starter options. `list <lane>` (`specify`, `plan`, `build`, `cross-cutting`): that lane only, with its subagents. The lanes come from `reference/index.yaml` and must match `guild-routing.md`; when they differ, say so and cite both.

### 7. Compare two skills

`compare A B`, or `difference between A and B`. A side-by-side table from both `reference/skills/<name>.md` pages: lane and group, purpose, use when, reads, writes, leaves alone, runs by itself, you run next, and their route steps. Then one or two lines on when to pick which, only as the docs say it. For `/crav1-explain-this-code` and `/crav1-explain-existing-system`: explain-this-code reads code (a file, function, selection, or PR diff) and the code it calls; explain-existing-system reads the system notes in `docs/system/` about the whole system. Both are read-only and cross-cutting. A name that matches no skill: say so and list the closest names.

### 8. What's new

`whats new`: the `CHANGELOG.md` section for the installed version (see **Newer-version notice** for how it is found). `whats new since x.y` or `since x.y.z`: every section after that version, newest first, up to the installed one. Summarize each release in a few bullets and cite its heading anchor, for example `Source: CHANGELOG.md#1540-2026-10-14`. Never read a newer version's notes from GitHub; when a newer tag exists, only the one notice line names it.

## Newer-version notice

At most once per chat, in the first answer:

1. The installed version is `version` in the plugin's `.cursor-plugin/plugin.json` (kit repo: `plugins/crav1/.cursor-plugin/plugin.json`). A drop-in has no `plugin.json`: use the `Kit version:` line at the top of `crav1-docs/reference/workflow.md`. When neither is readable, skip the notice.
2. When the machine is online, read the tag names only, with a short timeout: `git ls-remote --tags --refs https://github.com/Crav1on/crav1-spec-kit` . Take the highest `vX.Y.Z`.
3. When that is newer than the installed version, add one line: `A newer kit version is tagged: vX.Y.Z (installed X.Y.Z).` Nothing else.

Offline, a failed read, or no newer tag: say nothing. Never read a doc, a changelog, or a skill from GitHub, and never answer from a newer version.

## Parked and retired specs (1.60.0)

When the answer lists specs or the next step, skip `docs/specs/retired/` and `Moved:` pointers. List each spec with a `Parked:` line under **Parked**, with its date and reason and the count of notes with that slug in `waiting_for` (from the generated notes indexes in `docs/notes/YYYY-MM/`, or an old `Waiting for <slug> (parked)` line), for example `orders-export (parked 2026-10-16, waiting on partner), 2 notes waiting`. Name `/crav1-retire-spec un-park docs/specs/<slug>/` to pick one up. Do not run it.
