# Installing and using CRAV1 Spec Kit (crav1)

Read this **before** you put **CRAV1 Spec Kit** in a project. It covers what you get, which install path to pick, and where to go next. It is not the full playbook. The thin path after you pick an install is [first-run.md](first-run.md).

Kit home: [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). License: [MIT](../LICENSE).

- After a **plugin** install, open the plugin README (in Cursor: the `crav1` plugin, or [plugins/crav1/README.md](../plugins/crav1/README.md) in this repo).
- For the **process** (why specs, Plan Mode, templates), use [README.md](../README.md), [from-nothing.md](from-nothing.md), [from-ideas.md](from-ideas.md), and [from-intake.md](from-intake.md).

## What this kit is

**CRAV1 Spec Kit** (`crav1`) is a Cursor skill and agent library for spec-driven development. Slash commands are prefixed `crav1-` so they group under `/crav1` and stay separate from Cursor built-ins.

It does **not** create an app for you. It writes and walks specs, plans, tasks, and verify/fix loops **in the repo you already have** (or that you ask the agent to scaffold).

This kit repository is the source. Your product repository is where work happens.

## License

[MIT](../LICENSE). Copyright (c) 2026 Thomas Cronholm.

## What gets installed

| Piece | Role |
| --- | --- |
| Skills (`/crav1-…`) | Playbooks: spark/ideas/intake → spec → plan → review-plan → implement → verify → fix → draft commit |
| Agents | `crav1-spec-reviewer-agent`, `crav1-architecture-reviewer-agent`, `crav1-plan-reviewer-agent` (readonly critics); `crav1-complete-task-agent` and `crav1-intake-slice-agent` (writers) |
| Rule `crav1.mdc` | Short always-on reminder: specs under `docs/specs/`, kit command order |
| Templates | Inside each skill’s `assets/` (and agent-assets). Optional human copies: `docs/specs/_template/`, `docs/system/_template/` |

Not installed by the plugin: this repo’s long README, `AGENTS.md`, `docs/specs/_template/`, or `docs/system/_template/`. Copy those starter folders yourself if you want them in git.

## Prerequisites

- [Cursor](https://cursor.com/) with Agent chat (slash skills).
- A **product git repo** (or this kit repo, which already has the drop-in `.cursor/` tree).
- Optional: Teams or Enterprise, if you want a **team marketplace** (import this repo, then Install). Free/Pro can still **copy files** or load a **local plugin**.

**Import from Repo** for this kit uses [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).

## Pick an install path

### A. Drop-in copy (files in the product repo)

Works on any plan. Skills travel with clones, PRs, and Cloud Agents that use **project** files. Updates are a later copy (or git subtree).

From a clone of this kit:

1. Copy into the **product** repo:
   - `.cursor/skills/crav1/`
   - `.cursor/agents/crav1-*.md`
   - `.cursor/agent-assets/crav1-*`
   - `.cursor/rules/crav1.mdc`
2. Optionally copy `docs/specs/_template/`, `docs/system/_template/`, and add a line to the product `AGENTS.md` pointing at `docs/specs/` and `docs/system/`.
3. Commit those files in the product repo.
4. Reload Cursor if `/crav1` does not show up (`Developer: Reload Window`).

Do **not** copy `.cursor/rules/kit-maintainer.mdc` unless you are forking the kit itself. That rule is for maintainers of this repository (no `crav1-` prefix on purpose, so a `crav1*` dump skips it).

### B. Cursor plugin (install from this repo)

The plugin lives at [`plugins/crav1/`](../plugins/crav1/) with manifest [`plugin.json`](../plugins/crav1/.cursor-plugin/plugin.json). The catalog is [`.cursor-plugin/marketplace.json`](../.cursor-plugin/marketplace.json).

**Team marketplace (Teams / Enterprise)**

1. Cursor Dashboard → **Plugins & MCPs** → **Team Marketplaces** → **Add Marketplace** → **Import from Repo**, and use [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).
2. Confirm plugin `crav1`. Set access and Default Off / Default On / Required. Save. Enable Auto Refresh on GitHub if you want pushes to re-index.
3. In the IDE: **Customize** → find **crav1** → **Install** → project or user scope.

**Public Cursor Marketplace**

Optional: submit this repo at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Team marketplace, drop-in copy, and local plugin do not require that.

**CLI**

`cursor-agent plugin marketplace add <repository-url>` adds a marketplace. Installing a plugin is still interactive (Customize or `/plugin`). There is no reliable non-interactive `plugin install` for CI yet.

**Scope**

- **Project** — this workspace. Prefer this so Cloud Agents and teammates see the same kit.
- **User** — follows you across repos; does not put files in git.

### C. Local plugin (kit development)

1. Copy or symlink **inside** `~/.cursor/plugins/local/` only (Cursor ignores symlinks that point outside that folder):

   ```bash
   mkdir -p ~/.cursor/plugins/local
   cp -a plugins/crav1 ~/.cursor/plugins/local/crav1
   ```

2. Reload the window. Confirm **crav1** in **Customize**.
3. Teams/Enterprise admins may disable local plugin imports.

After you change the kit, re-copy or re-run the sync script, then reload.

## After install

New to the loop? [First 15 minutes](first-run.md): open the product repo → `/crav1` → `/crav1-spark-to-spec` → tighten → plan → one task.

1. Open Agent chat in the **product** repo.
2. Type `/crav1` and run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs`. Brownfield: expect a branch prompt (`feat/<slug>` or `spec/<slug>`).
3. Follow the plugin README’s short loop. Do not start in Plan Mode or by picking a stack.

`/crav1-complete-tasks`, standalone `/crav1-complete-task`, and `/crav1-complete-features` **pause once** with Settings directions (Run Everything vs Auto-review), wait for `continue` / `click`, then remind you how to restore the previous mode when the run ends. Workers launched by those orchestrators do not pause again. The skill cannot change Settings for you.

If this window is the **kit repo**, drop-in skills are already under `.cursor/` — no extra install.

## Keeping the kit updated

| You installed with | Update by |
| --- | --- |
| Drop-in copy | Copy the same folders again from a newer kit; commit in the product repo |
| Team marketplace | Auto Refresh or Dashboard **Refresh**, then update/reinstall the plugin if Cursor asks |
| Local plugin | `scripts/sync-crav1-plugin.sh` in the kit, copy `plugins/crav1` to `~/.cursor/plugins/local/crav1`, reload |

Kit maintainers: edit `.cursor/` first, run `scripts/sync-crav1-plugin.sh`, keep this file and `plugins/crav1/README.md` accurate. Rule: `.cursor/rules/kit-maintainer.mdc`.

## Using the kit without “installing”

Clone this repository and work here. Commands work because `.cursor/skills/crav1/` is already present. Use that to learn; copy or plugin-install when a **product** repo should get the same commands.

## Clone

```bash
git clone https://github.com/Crav1on/crav1-spec-kit.git
```

The kit is at [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). After clone, use **drop-in copy** or **local plugin**.

## What to read next

| Situation | Doc |
| --- | --- |
| Just installed; want install through one task | [first-run.md](first-run.md) |
| Plugin just installed, want the command order | [plugins/crav1/README.md](../plugins/crav1/README.md) |
| One-sentence idea | [docs/from-nothing.md](from-nothing.md) |
| Pile of ideas + tech hunches | [docs/from-ideas.md](from-ideas.md) |
| Mixed files / several features or repos | [docs/from-intake.md](from-intake.md) |
| How Cursor + SDD fit together | [README.md](../README.md) |
| Which lane owns a `/crav1-…` skill or `*-agent` | [guild-routing.md](guild-routing.md) |
| Cursor plugin format | [Plugins](https://cursor.com/docs/plugins) · [Plugins reference](https://cursor.com/docs/reference/plugins) |
