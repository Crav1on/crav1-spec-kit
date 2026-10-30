# Agent instructions for this repo

This repository is a **process guide** for spec-driven development, not an application. Cursor and Claude Code installs are in [docs/install.md](docs/install.md).

Per-skill behavior lives in each skill's `SKILL.md` and in [docs/reference/skills.yaml](docs/reference/skills.yaml) (rendered as [docs/reference/skills.md](docs/reference/skills.md) and one page per skill under `docs/reference/skills/`). Routes live in [docs/reference/workflow.yaml](docs/reference/workflow.yaml). This file does not repeat them (1.106.0). When you need one skill's rules, open that skill's page, not the whole reference.

## Starters

- When the user asks for startup options, name only these six: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane.
- Each starter keeps its own entry rule: `/crav1-existing-to-specs` only when the user names repos, `/crav1-read-environment` only when the user names the host (naming production, prod, or live stops), `/crav1-fix-bug` only when the user names a real bug.
- Do not scaffold an app unless the user explicitly asks for one. Do not code before a spec exists.

## Layout

- Per-change work goes under `docs/specs/<change-id>/`, started from `docs/specs/_template/`. The system picture is `docs/system/` (landscape, diagrams, repos, glossary, security), started from `docs/system/_template/`. Notes go to `docs/notes/YYYY-MM/`, imported originals to `docs/sources/YYYY-MM-DD-<slug>/`, research to `docs/research/`, environments to `docs/environments/`.
- Writers add what is new and do not rewrite what is already there. New glossary rows go in sorted place by term; a meaning the source does not state is `to be researched`.
- `docs/system/repos.md` has a `## Synced at` section, one line per repo and branch. Whole-repo reads update that repo's line; one-slice reads write the slice's `Synced at:` line in its `spec.md` instead. Details: [docs/concepts/data-layout.md](docs/concepts/data-layout.md).
- Skills carry copies of the templates in their `assets/`; keep them byte-identical (`scripts/check-template-copies.py`).

## The route, in one line each

Specify: spark, ideas, bundle, or existing-to-specs; later information through `/crav1-add-to-spec`; critique with `/crav1-review-architecture` and `/crav1-review-security`; `/crav1-tighten-spec`; `/crav1-resolve-open-questions`. Plan: `/crav1-plan-from-spec`, optional `/crav1-review-plan` and `/crav1-tighten-plan`. Build: `/crav1-build-tasks` or `/crav1-build-features`, `/crav1-verify-build-against-spec`, `/crav1-fix-build-gaps`. Ship: `/crav1-finalize-commit`, `/crav1-open-pr`, `/crav1-review-pr`, `/crav1-pr-status`, `/crav1-merge-pr` (merge only on an explicit ask). Cross-cutting skills (help, glossary, explain, what-do-we-know, refresh-system-notes, ado-sync, environments, exploratory test, suggest tests, open questions, retire, export) run from any lane and do not move work into a lane. The exact order and when each applies is `workflow.yaml`; `/crav1-help next` reads it.

- Prefer editing the spec or plan over long patch-prompt threads when implementation drifts.
- No skill pushes, merges, posts, or writes to Azure Boards without the user's yes in that turn.

## Editing the kit

- When adding or updating a crav1 skill or agent, edit `.cursor/skills/crav1/crav1-<name>/` (agents: `.cursor/agents/crav1-<name>.md`, templates: that skill's `assets/` and `.cursor/agent-assets/crav1-<name>/`), then run `scripts/sync-crav1-plugin.sh` so `plugins/crav1/` and the generated `.claude/` tree match. `scripts/sync-crav1-claude.sh --check` fails if `.claude/` is stale. See `.cursor/rules/kit-maintainer.mdc`.
- Load paths: a skill routes first and loads only the chosen branch or reference. `SKILL.md` stays near 1,500 words (CI limit 2,000); the description is trigger text only, at most 60 words (`scripts/check-kit-docs.py`).
- A behavior change updates `docs/reference/skills.yaml`, then `scripts/gen-skill-docs.py` regenerates the pages and `docs/reference/index.yaml`.
- Keep the README a short landing page: intro, the six starter options, the lanes, and links. The method is [docs/concepts/method.md](docs/concepts/method.md). Every page is listed in [docs/README.md](docs/README.md); add a new page there. Host file locations belong in [docs/install.md](docs/install.md).
- Keep [docs/install.md](docs/install.md) and [plugins/crav1/README.md](plugins/crav1/README.md) current when install or first-run steps change.
