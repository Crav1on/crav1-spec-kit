# crav1-help: modes

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### 7. Compare two skills

`compare A B`, or `difference between A and B`. A side-by-side table from both `skills.yaml` entries and reference pages: lane and group, purpose, use when, reads, writes, leaves alone, runs by itself, you run next, and their route steps. Then one or two lines on when to pick which, only as the docs say it. For `/crav1-explain-this-code` and `/crav1-explain-existing-system`: explain-this-code reads code (a file, function, selection, or PR diff) and the code it calls; explain-existing-system reads the system notes in `docs/system/` about the whole system. Both are read-only and cross-cutting. A name that matches no skill: say so and list the closest names.

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
