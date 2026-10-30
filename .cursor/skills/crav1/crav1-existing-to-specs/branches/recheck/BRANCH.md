# Repos vs specs (recheck, preview)

Specs already exist and the code kept moving. You read the named repos, compare them with the specs that are already there, and report two things: code that no spec covers, and spec claims the code no longer shows. You refresh one note in `docs/system/landscape.md`. You write nothing into any spec.

Paths in backticks are relative to the skill folder unless they start with `docs/`.

Preview (1.108.0). The rules can still change after use on a real repo.

This is not the repos and bundle branch (that creates spec folders from repos plus a bundle) and not the code change branch of `/crav1-add-to-spec` (that sorts one pointed change onto specs). This branch runs only when the user calls it. Do not schedule it, hook it, or run it again because new commits appeared.

## Input

Choice words `recheck` or `repos vs specs`. The two opening questions of `SKILL.md` are not asked.

- **Repos:** the repos named after the word, for example `/crav1-existing-to-specs recheck orders-api`. With none named, use every repo row in `docs/system/repos.md`. With no repo named and no `repos.md`, stop and ask for the repos. A headless run stops: `No repos named and no docs/system/repos.md. Name the repos.`
- **Scope (optional):** a path inside one repo (`recheck orders-api src/billing`). Only units under that path are compared. Stale claims are checked only for cited paths under it.
- **Since (optional):** the word `since`. Only code changed after that repo's `Synced at` line in `docs/system/repos.md` is compared. A repo with no `Synced at` line is read whole; say so.

Read each repo from its sibling checkout `../<repo>` (or the open checkout when it is that repo), as skill `crav1-add-to-spec`, `references/branches.md` says under **Sibling checkout**. Ask for a missing path with options; a headless run stops: `No checkout found for <repo>. Name its path.` Never check out, fetch, pull, commit, or write in a repo checkout.

## Specs (no compare yet)

Read every `docs/specs/<slug>/spec.md`. Skip `_template`. Read its `## In the code` paths, `## Match` status and `Repo:` line when present, and its text. Read `docs/architecture/spec.md` when present; its cited paths count as coverage.

Parked and retired specs do not count as coverage (see Report).

If there are no spec folders, stop. Point at the repos and bundle branch (`/crav1-existing-to-specs repos and bundle`). Do not create a slug.

## Large repo

Count the units first (this skill's `branches/recheck/references/units.md`). Over 200 units in one repo with no scope and no `since`: ask one question with options, the scoped run first: **Pick a path (Recommended)** · **Changed since last read** · **Whole repo anyway**. A headless run stops: `<repo> has <n> units. Add a path or since.`

## Compare

Follow this skill's `branches/recheck/references/units.md` to cut the code into units and skip what is not a unit.

1. **Code with no spec.** A unit is covered when a spec's `## In the code` path is the unit's path or a folder above it, or the spec text names the unit (route, job, module, or feature name) and the code confirms it. A unit cited by two specs is covered. A unit no spec covers is a gap. A unit you cannot describe from the code is listed as `unclear: <path>`, not guessed.
2. **Stale claims.** A path under a spec's `## In the code` that no longer exists in that repo is a stale claim. A `done` or `partial` slice whose cited paths are all gone is a stale slice. Report them; change nothing in the spec.
3. A folder citation covers everything under it. Report it once as `broad citation: <slug> <path>`.

This is not a spec-quality check. Wording stays with `/crav1-tighten-spec`.

## Landscape note

When `docs/system/landscape.md` exists, refresh `## Code with no slice` with the format in skill `crav1-existing-to-specs`, `branches/repos-and-bundle/references/landscape.md` (repo, path, one line). Only for the repos and scope this run read:

- A line still true stays as it is. Do not reword it.
- A line now covered by a spec comes off.
- A new gap gets a new line.
- Lines under `## Dismissed` in that note stay and are never offered again.
- Lines for repos or paths outside this run stay as they are.

Add the heading when it is missing and there is a gap. When `docs/system/` is missing, write nothing and say no note was written. Stale claims are not written to the note.

Set the `Synced at` line in `docs/system/repos.md` for each repo read whole (no scope, no `since`), as skill `crav1-add-to-spec`, `branches/code-change/references/synced-at.md` says. A scoped or `since` run does not move it.

## Hard rules

- Write nothing into any `spec.md`: no quote, no heading, no `## Open questions` line, no Match status change.
- Never add an open question to a spec, in any mode, even when asked here. Point at `/crav1-add-to-spec` instead.
- Do not create a spec folder, slug, `plan.md`, or `tasks.md`.
- Do not touch application code, branches, or Azure Boards.
- Do not invent a purpose or a link the code does not show.
- The only writes are the landscape note and `Synced at` lines.

## Report

Per repo, in this order:

1. **Code with no spec:** `repo · path · what it does (one line) · nearest spec, if any`. Units covered only by a parked or retired spec say `covered only by parked/retired <slug>`.
2. **Stale claims:** `slug · cited path · gone` and stale slices.
3. `unclear` units and broad citations.
4. Counts: units compared, gaps, stale claims, skipped (generated, vendor, test, build).
5. The landscape note: lines added, removed, kept, or `no note written: <why>`. `Synced at` lines set, or why not.

Then, when there is at least one gap, follow this skill's `branches/recheck/references/handoff.md` for the per-gap choices.

When nothing is found: `No gaps and no stale claims in <repos/scope>.` and the note changes, if any.

## Stop

Stop after the report and the handoff choices. Do not start Specify, Plan, or Build. Next steps the user may run: `/crav1-add-to-spec` for a gap they want in a spec, `/crav1-tighten-spec` for a stale claim they want fixed in the spec, `/crav1-spark-to-spec` for a new feature.
