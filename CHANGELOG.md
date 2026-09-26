# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

## Unreleased

### Kit

- Cross-cutting skill `/crav1-merge-pr` merges one named pull request only when that turn explicitly asks (number or URL). Always a merge commit: GitHub `gh pr merge <n> --merge`; Azure Repos `az repos pr update --id <n> --status completed --merge-strategy noFastForward`. No squash, no rebase, no `--admin`, no `--bypass-policy`. A draft is marked ready only as part of that ask. If `az` is missing, or it rejects `--merge-strategy`, the skill prints the REST PATCH (`status` completed, `completionOptions.mergeStrategy` `noFastForward`, `lastMergeSourceCommit` set) and the web UI steps. It uses the existing git credential or `az login` and does not handle tokens. After a merge it reports the merge commit hash and, when the tree is clean, fast-forwards local `main`. It does not delete a branch unless asked, and it does not change work-item links. `/crav1-open-pr` names it as a later explicit step and does not run it.
- Optional Azure Boards linking via `docs/specs/<slug>/work-item.md` (`Work item: <id>`). `/crav1-draft-commit-message` leaves the subject and description as drafted, then appends a blank line and the mention as the last description line (GitKraken paste includes it). `/crav1-finalize-commit` keeps that line through the HEAD check and the Cursor-attribution strip. `/crav1-open-pr` adds a `## Work item` section when the file resolves a mention, and its Spec section links that slug’s `spec.md`, `plan.md`, and `tasks.md`. The mention is `#<id>` on Azure Repos, `AB#<id>` on GitHub, and omitted on any other host unless the file already contains a full token. A missing file does not block. On Azure Repos only, the skills print one hint. `/crav1-open-pr` still does not pass `--work-items`.
- Cross-cutting skill `/crav1-open-pr` pushes the change branch only after an explicit yes, then opens one pull request against the default branch. It does not commit, merge, force-push, or delete the branch. `/crav1-finalize-commit`, `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` may name it as an optional next step; they do not run it. Workers stay no push / no PR.
- `/crav1-open-pr` creates an Azure DevOps pull request with `az repos pr create` when the remote is `dev.azure.com` or `*.visualstudio.com` and the Azure CLI is available. GitHub still uses `gh`. If `az` is missing, not logged in, or create fails, the skill prints commands and GitKraken GUI paste fields and does not claim a pull request was opened.
- Subagent files and `name:` values now end in `-agent` (`crav1-architecture-reviewer-agent`, `crav1-complete-task-agent`, `crav1-intake-slice-agent`, `crav1-plan-reviewer-agent`, `crav1-spec-reviewer-agent`) so the Cursor slash picker can tell them apart from skills. Skill commands stay `/crav1-architecture-reviewer` and `/crav1-complete-task`. Descriptions start with `Subagent.`

### Docs

- [docs/from-ideas.md](docs/from-ideas.md) documents the optional `docs/specs/<slug>/work-item.md` mention. Starter: [docs/specs/_template/work-item.md](docs/specs/_template/work-item.md).
- Guild routing map added: [docs/guild-routing.md](docs/guild-routing.md). Lanes are Specify, Plan, Build, and Cross-cutting for public reuse.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-open-pr` under Cross-cutting.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-merge-pr` under Cross-cutting (any lane, only on an explicit ask to merge a named pull request). Specify, Plan, and Build lane ownership is unchanged.
- Plugin author and marketplace owner display name is **Crav1**. The contact email is unchanged. [LICENSE](LICENSE) is unchanged.
- [docs/guild-routing.md](docs/guild-routing.md) adds Research as a cross-cutting helper (no slash command). A lane that must answer a technical question before Specify or Plan flags the process orchestrator or guild lead, who pauses that lane. The researcher writes `docs/specs/<slug>/research.md` (recommendation, trade-offs, confidence, link to the full study) and does not edit specs, plans, or code, or change the lane.

## 1.0.0

First release of the public-facing kit: the skills, dual install, and sync check on `main`, plus the product-name, first-run, contributing, and support docs shipped with this changelog. The GitHub repository stays private until the owner changes visibility. This changelog does not create a git tag.

### Kit

- MIT license. The copyright notice is in [LICENSE](LICENSE).
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
