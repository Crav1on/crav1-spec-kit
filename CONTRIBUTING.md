# Contributing to CRAV1 Spec Kit

## Consumers

Install the kit into a product repo on Cursor or Claude Code. The slash commands are the same. The install is not. Paths, what gets copied, and what to run first: [docs/install.md](docs/install.md). A short loop after that: [docs/first-run.md](docs/first-run.md).

Cursor drop-in includes `.cursor/rules/crav1.mdc`. Claude Code drop-in includes `.claude/CLAUDE.md`. Leave `.cursor/rules/kit-maintainer.mdc` in this kit repo. It has no `crav1-` prefix so a `crav1*` folder dump skips it, and it is maintainer guidance for this repository only. Do not copy it into `.claude/`.

Broken install or skill: [SUPPORT.md](SUPPORT.md).

## Contributors

This repo is the kit source. Product work happens in the repo where the kit is installed.

1. Edit the drop-in tree under `.cursor/` (skills in `.cursor/skills/crav1/crav1-<name>/`, agents in `.cursor/agents/crav1-<name>.md`, templates in that skill’s `assets/` and `.cursor/agent-assets/crav1-<name>/`).
2. Run `scripts/sync-crav1-plugin.sh` so `plugins/crav1/` matches and `.claude/` is regenerated. Hand-edits under `plugins/crav1/skills/`, `agents/`, `rules/crav1.mdc`, and `agent-assets/`, and everything under `.claude/`, are overwritten on the next sync.
3. Plugin-only files stay hand-edited: `plugins/crav1/.cursor-plugin/plugin.json` and `plugins/crav1/README.md`. The catalog is `.cursor-plugin/marketplace.json`. There is no Claude Code plugin and no marketplace in this kit. There is no public Cursor Marketplace listing.
4. When install or first-run steps change, update [docs/install.md](docs/install.md) and [plugins/crav1/README.md](plugins/crav1/README.md). A new docs page gets a line in the [docs index](docs/README.md). Longer reader text for one skill goes in its `in_depth` field in `skills.yaml`, not in the README.
5. When you add, rename, or remove a skill, agent, or cross-cutting helper, update [docs/guild-routing.md](docs/guild-routing.md) in the same pull request. Update [docs/reference/skills.yaml](docs/reference/skills.yaml) in that same pull request and run `scripts/gen-skill-docs.py`, which regenerates [docs/reference/skills.md](docs/reference/skills.md) and the per-skill pages. A Claude Code path change does not rename a skill or agent, so guild routing stays as it is. `skills.yaml` still changes when what a skill reads, writes, or calls changes.
6. A skill change is done only when it is documented. This covers a new skill and a change to an existing skill.
   - **A new skill:** its `skills.yaml` entry and generated reference page, a walkthrough (its own `docs/from-*.md` page or a step in a goal walkthrough) that links back to the reference page, a line in the [docs index](docs/README.md) for a new page, and a CHANGELOG entry. A single-shot command may stay reference only when the pull request says why.
   - **A change to an existing skill:** in the same pull request, update that skill's walkthrough, and its entries in [docs/concepts/](docs/concepts/) (the [glossary](docs/concepts/glossary.md) and the [data layout](docs/concepts/data-layout.md)) when the change adds or changes a word, a file, a column, or a mark. Update `skills.yaml` as item 5 says.
   - **CI check:** `scripts/check-skill-docs-touched.py` fails a pull request that changes a `SKILL.md` (in `.cursor/skills/crav1/`, `plugins/crav1/skills/`, or `.claude/skills/`) when no change under `docs/`, outside `docs/reference/`, covers that skill. The skill's walkthrough counts, and so does any changed line that names the skill. When a change really needs no docs update, such as a typo fix, opt out with the `docs-not-needed` label or a line in the pull request body: `Docs-not-needed: <reason>`. A pull request that regenerates docs or changes anything under `docs/` has no `Docs-not-needed:` line; the release stamp in `docs/reference/workflow.md` alone does not count. `scripts/check-docs-not-needed.py` (workflow `pr-release-checks.yml`) warns when the body has that line and `docs/` changed.
7. The order of commands lives in one place, [docs/reference/workflow.yaml](docs/reference/workflow.yaml). Change a route or a next step there, then run `scripts/gen-workflow.py`, `scripts/gen-skill-docs.py`, and `scripts/sync-crav1-plugin.sh`. Do not edit `you_run_next` in `skills.yaml`, the order block in `crav1.mdc`, or `docs/reference/workflow.md` by hand. `scripts/gen-workflow.py --check` fails when they drift, when a route names a missing skill, when a skill has no next steps, when the `/crav1-help` rule is missing from `crav1.mdc` or its copies, or when a walkthrough `## After` section names a skill that `workflow.yaml` does not.
8. Every mark and line format the kit writes in a product repo lives in one place, [docs/reference/marks.yaml](docs/reference/marks.yaml): name, files, format, a pattern, examples with made-up names, who writes and reads it, and the version it arrived in. Add or change a mark there first, then run `scripts/gen-marks.py` (it writes the marks tables in `docs/concepts/data-layout.md`) and `scripts/sync-crav1-plugin.sh`. `scripts/gen-marks.py --check` fails when the tables drift, when an example does not match its pattern, or when a skill listed as writer or reader never mentions the mark. Public docs and skills use made-up example names (`orders-api`, `feat/orders-retry`), never a real customer's repo, branch, pipeline, or person.
9. Every release carries its own docs in every install. `scripts/sync-crav1-plugin.sh` copies `docs/` and `CHANGELOG.md` to `.cursor/skills/crav1/crav1-docs/`, which the plugin mirror (`plugins/crav1/skills/crav1-docs/`) and the Claude Code drop-in (`.claude/skills/crav1-docs/`, copied verbatim) take from there. Never edit `crav1-docs/` by hand. CI fails when any copy differs from `docs/`.
10. A rename adds the old name to the **Renamed skills** table in [docs/README.md](docs/README.md) with the new name and choice word, so `/crav1-help` can still answer it. Old names do not keep running: the 1.56.0 aliases were removed in 1.58.0. If a later rename needs a transition period, it is a design decision for that release. A merge keeps each old skill's rules verbatim in `branches/<id>/BRANCH.md` (not `SKILL.md`, so hosts do not load it as a skill) and opens with a question with options, not flags. It lists exact choice words for every option under `choice_words` in `skills.yaml` and in its `SKILL.md` (`gen-skill-docs.py --check` checks both); a headless or bot run with no word stops and names them.
11. Keep each `SKILL.md` to the common path, about 1,500 words. A rare case (another host, a fallback, a handoff from another skill, a later phase) goes word for word into the skill's `references/` with a one-line pointer in `SKILL.md` that says when to read it. `scripts/check-kit-docs.py` warns in CI when a `SKILL.md` is over 2,000 words.
11. A release sets `version` in `plugins/crav1/.cursor-plugin/plugin.json` to the number of its new `## X.Y.Z` heading in [CHANGELOG.md](CHANGELOG.md). `scripts/check-kit-docs.py` fails when they differ. After the release pull request merges, the release is a tag plus GitHub release from the CHANGELOG section: put the `vX.Y.Z` tag on the merge commit, then create a GitHub release on that tag, titled `vX.Y.Z`, with that version's `## X.Y.Z` CHANGELOG section as the notes, and mark it latest (for example `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --notes-file <section> --latest`). A docs-only pull request gets no tag and no release. A patch release (only `Z` in `X.Y.Z` goes up) is for moves and fixes. `scripts/check-patch-behavior.py` (workflow `pr-release-checks.yml`) warns, without failing, when a patch release adds a new sentence with never, always, stop, or ask to a `SKILL.md` or a `references/` file; a sentence moved word for word from another skill file is not flagged. On that warning, bump the minor version, or say in the pull request body why the change is still a patch.

A skill's template copy under `assets/` must match the template with the same name in `docs/*/_template/`; change both together. `scripts/check-template-copies.py` fails on drift (a copy that is deliberately a different template is listed in its `DIFFERENT` table with the reason).

Do not put `kit-maintainer.mdc` under `plugins/crav1/` or `.claude/`. CI rejects that. CI also rejects drift between the drop-in tree and the plugin mirror, a stale `.claude/` tree (`scripts/sync-crav1-claude.sh --check`), a stale skills reference (`scripts/gen-skill-docs.py --check`), and a skill description over 1,024 characters or a `plugin.json` version that differs from the newest CHANGELOG release (`scripts/check-kit-docs.py`), and a changed `SKILL.md` with no docs for it (`scripts/check-skill-docs-touched.py`, see item 6). Both scripts need PyYAML (`python3 -m pip install pyyaml`).

The longer maintainer rule is `.cursor/rules/kit-maintainer.mdc`.

## Pull requests

- One concern per PR when you can.
- Say which skill, doc, or install path changed, and how you checked it (sync script, the workflow diff, or the command you ran).
- Keep the visible author name in `plugins/crav1/.cursor-plugin/plugin.json` and the marketplace owner name in `.cursor-plugin/marketplace.json` as `Crav1`. There is no author email. Questions, bugs, and requests go to GitHub Issues on this repo ([SUPPORT.md](SUPPORT.md)).
- Leave [LICENSE](LICENSE) as MIT unless the owner asks for a change.
- Open a pull request for review with `/crav1-open-pr` (it does not merge). Review a named pull request with `/crav1-review-pr` (it does not edit, comment, or merge). See where its threads stand with `/crav1-pr-status` (it drafts replies and never posts). Merge a named pull request only with `/crav1-merge-pr`, and only when that turn explicitly asks. Merging this kit, and any git tag, stays with the owner.

## Load paths (standing rule, 1.104.0)

Every skill added or changed aims for the leanest load path:

- `SKILL.md` routes. It says which word, case, or branch applies and which file to read next. It does not carry templates, long rule sets, or every branch inline.
- Decide first, load second. Pick the path (a mode word, a branch, a case), then read only that path's file. Never read every template or reference up front. The default path (no mode word) opens none of them.
- One file per path: `references/<topic>.md`, `branches/<name>/BRANCH.md`, `reports/<type>-<depth>.md`, `assets/<template>.md`. A path file may share one small `common.md`; it does not point at its siblings.
- Diagrams and heavy output: only what that path or depth needs.
- Keep `SKILL.md` near 1,500 words (CI fails at 2,000). Move a section out, with a one-line pointer, before it grows.
- Add a unit test for the routing when a skill gains paths (see `scripts/tests/test_report_routing.py`).

