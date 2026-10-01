# Contributing to CRAV1 Spec Kit

## Consumers

Install the kit into a product repo. Paths, what gets copied, and what to run first: [docs/install.md](docs/install.md). A short loop after that: [docs/first-run.md](docs/first-run.md).

Cursor drop-in includes `.cursor/rules/crav1.mdc`. Claude Code drop-in includes `.claude/CLAUDE.md`. Leave `.cursor/rules/kit-maintainer.mdc` in this kit repo. It has no `crav1-` prefix so a `crav1*` folder dump skips it, and it is maintainer guidance for this repository only. Do not copy it into `.claude/`.

Broken install or skill: [SUPPORT.md](SUPPORT.md).

## Contributors

This repo is the kit source. Product work happens in the repo where the kit is installed.

1. Edit the drop-in tree under `.cursor/` (skills in `.cursor/skills/crav1/crav1-<name>/`, agents in `.cursor/agents/crav1-<name>.md`, templates in that skill’s `assets/` and `.cursor/agent-assets/crav1-<name>/`).
2. Run `scripts/sync-crav1-plugin.sh` so `plugins/crav1/` matches and `.claude/` is regenerated. Hand-edits under `plugins/crav1/skills/`, `agents/`, `rules/crav1.mdc`, and `agent-assets/`, and everything under `.claude/`, are overwritten on the next sync.
3. Plugin-only files stay hand-edited: `plugins/crav1/.cursor-plugin/plugin.json` and `plugins/crav1/README.md`. The catalog is `.cursor-plugin/marketplace.json`. There is no Claude Code plugin marketplace in this kit.
4. When install or first-run steps change, update [docs/install.md](docs/install.md) and [plugins/crav1/README.md](plugins/crav1/README.md).
5. When you add, rename, or remove a skill, agent, or cross-cutting helper, update [docs/guild-routing.md](docs/guild-routing.md) in the same pull request. A Claude Code path change does not rename a skill or agent, so that file stays as it is.

Do not put `kit-maintainer.mdc` under `plugins/crav1/` or `.claude/`. CI rejects that. CI also rejects drift between the drop-in tree and the plugin mirror, and a stale `.claude/` tree (`scripts/sync-crav1-claude.sh --check`).

The longer maintainer rule is `.cursor/rules/kit-maintainer.mdc`.

## Pull requests

- One concern per PR when you can.
- Say which skill, doc, or install path changed, and how you checked it (sync script, the workflow diff, or the command you ran).
- Keep the visible author name in `plugins/crav1/.cursor-plugin/plugin.json` and the marketplace owner name in `.cursor-plugin/marketplace.json` as `Crav1`. There is no author email. Questions, bugs, and requests go to GitHub Issues on this repo ([SUPPORT.md](SUPPORT.md)).
- Leave [LICENSE](LICENSE) as MIT unless the owner asks for a change.
- Open a pull request for review with `/crav1-open-pr` (it does not merge). Merge a named pull request only with `/crav1-merge-pr`, and only when that turn explicitly asks. Merging this kit, and any git tag, stays with the owner.
