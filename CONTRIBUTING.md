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
   - **CI check:** `scripts/check-skill-docs-touched.py` fails a pull request that changes a `SKILL.md` (in `.cursor/skills/crav1/`, `plugins/crav1/skills/`, or `.claude/skills/`) when no change under `docs/`, outside `docs/reference/`, covers that skill. The skill's walkthrough counts, and so does any changed line that names the skill. When a change really needs no docs update, such as a typo fix, opt out with the `docs-not-needed` label or a line in the pull request body: `Docs-not-needed: <reason>`.
7. The order of commands lives in one place, [docs/reference/workflow.yaml](docs/reference/workflow.yaml). Change a route or a next step there, then run `scripts/gen-workflow.py`, `scripts/gen-skill-docs.py`, and `scripts/sync-crav1-plugin.sh`. Do not edit `you_run_next` in `skills.yaml`, the order block in `crav1.mdc`, or `docs/reference/workflow.md` by hand. `scripts/gen-workflow.py --check` fails when they drift, when a route names a missing skill, when a skill has no next steps, when the `/crav1-help` rule is missing from `crav1.mdc` or its copies, or when a walkthrough `## After` section names a skill that `workflow.yaml` does not.
8. Every release carries its own docs in the plugin. `scripts/sync-crav1-plugin.sh` copies `docs/` to `plugins/crav1/docs/`, and CI fails when the two differ.
9. A release sets `version` in `plugins/crav1/.cursor-plugin/plugin.json` to the number of its new `## X.Y.Z` heading in [CHANGELOG.md](CHANGELOG.md). `scripts/check-kit-docs.py` fails when they differ.

Do not put `kit-maintainer.mdc` under `plugins/crav1/` or `.claude/`. CI rejects that. CI also rejects drift between the drop-in tree and the plugin mirror, a stale `.claude/` tree (`scripts/sync-crav1-claude.sh --check`), a stale skills reference (`scripts/gen-skill-docs.py --check`), and a skill description over 1,024 characters or a `plugin.json` version that differs from the newest CHANGELOG release (`scripts/check-kit-docs.py`), and a changed `SKILL.md` with no docs for it (`scripts/check-skill-docs-touched.py`, see item 6). Both scripts need PyYAML (`python3 -m pip install pyyaml`).

The longer maintainer rule is `.cursor/rules/kit-maintainer.mdc`.

## Pull requests

- One concern per PR when you can.
- Say which skill, doc, or install path changed, and how you checked it (sync script, the workflow diff, or the command you ran).
- Keep the visible author name in `plugins/crav1/.cursor-plugin/plugin.json` and the marketplace owner name in `.cursor-plugin/marketplace.json` as `Crav1`. There is no author email. Questions, bugs, and requests go to GitHub Issues on this repo ([SUPPORT.md](SUPPORT.md)).
- Leave [LICENSE](LICENSE) as MIT unless the owner asks for a change.
- Open a pull request for review with `/crav1-open-pr` (it does not merge). Review a named pull request with `/crav1-review-pr` (it does not edit, comment, or merge). Merge a named pull request only with `/crav1-merge-pr`, and only when that turn explicitly asks. Merging this kit, and any git tag, stays with the owner.
