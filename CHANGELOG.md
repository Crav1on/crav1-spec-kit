# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

## Unreleased

### Kit

- Cross-cutting skill `/crav1-open-pr` pushes the change branch only after an explicit yes, then opens one pull request against the default branch. It does not commit, merge, force-push, or delete the branch. `/crav1-finalize-commit`, `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` may name it as an optional next step; they do not run it. Workers stay no push / no PR.
- Subagent files and `name:` values now end in `-agent` (`crav1-architecture-reviewer-agent`, `crav1-complete-task-agent`, `crav1-intake-slice-agent`, `crav1-plan-reviewer-agent`, `crav1-spec-reviewer-agent`) so the Cursor slash picker can tell them apart from skills. Skill commands stay `/crav1-architecture-reviewer` and `/crav1-complete-task`. Descriptions start with `Subagent.`

### Docs

- Guild routing map added: [docs/guild-routing.md](docs/guild-routing.md). Lanes are Specify, Plan, Build, and Cross-cutting for public reuse.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-open-pr` under Cross-cutting.

## 1.0.0

First release of the public-facing kit: the skills, dual install, and sync check on `main`, plus the product-name, first-run, contributing, and support docs shipped with this changelog. The GitHub repository stays private until the owner changes visibility. This changelog does not create a git tag.

### Kit

- MIT license. Copyright (c) 2026 Thomas Cronholm.
- Dual install, documented in [docs/install.md](docs/install.md):
  - Drop-in copy into a product repo: `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc`.
  - Cursor plugin at `plugins/crav1/` with catalog `.cursor-plugin/marketplace.json` (team marketplace or local plugin).
- Skill loop under `/crav1`: spark, ideas, or intake → spec → architecture review and tighten → resolve questions → plan → review-plan and tighten-plan → one task (`/crav1-implement-task`) or an isolated worker (`/crav1-complete-task`, `/crav1-complete-tasks`, serial `/crav1-complete-features`) → verify → fix-from-verify (and fix-live) → draft or finalize a commit message.
- Maintainer sync: edit `.cursor/`, then run `scripts/sync-crav1-plugin.sh`. GitHub Actions (`.github/workflows/drop-in-plugin-sync.yml`) fails the check when the drop-in tree and `plugins/crav1/` drift, and when `kit-maintainer.mdc` is present under the plugin.

### Docs

- README leads with the product name **CRAV1 Spec Kit** (`crav1`) and keeps the spec-driven playbook.
- [docs/first-run.md](docs/first-run.md) — install through one task.
- [CONTRIBUTING.md](CONTRIBUTING.md) — consumers install from [docs/install.md](docs/install.md); contributors edit `.cursor/` and sync.
- [SUPPORT.md](SUPPORT.md) — GitHub Issues for a broken skill or install.
