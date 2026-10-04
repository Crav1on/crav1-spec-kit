# Installing and using CRAV1 Spec Kit (crav1)

Read this **before** you put **CRAV1 Spec Kit** in a project. It covers what you get, which host and scope to pick, and where files go. It is not the full playbook. The thin path after you pick an install is [first-run.md](first-run.md).

The method (specs, `plan.md`, `tasks.md`, verify) is [README.md](../README.md), [from-nothing.md](from-nothing.md), [from-ideas.md](from-ideas.md), [from-intake.md](from-intake.md), [from-match.md](from-match.md), [from-match-dump.md](from-match-dump.md), [from-code.md](from-code.md), [from-add.md](from-add.md), [from-security.md](from-security.md), [from-review-pr.md](from-review-pr.md), and [from-fix-bug.md](from-fix-bug.md). This file is the host detail those pages leave out.

Kit home: [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). License: [MIT](../LICENSE).

- After a **Cursor plugin** install, open the plugin README (in Cursor: the `crav1` plugin, or [plugins/crav1/README.md](../plugins/crav1/README.md) in this repo). Plugin id: `crav1`. There is no public Cursor Marketplace listing. Install that plugin from this GitHub repo (team marketplace import or a local plugin), or copy the `.cursor/` drop-in below.
- **Claude Code** has no plugin and no marketplace. The slash commands are the same. Copy the generated `.claude/` drop-in below into a repository you own, or into `~/.claude` for a client project. Cloning this kit does not install it into another product.

## What this kit is

**CRAV1 Spec Kit** (`crav1`) is a skill and agent library for spec-driven development. Slash commands are prefixed `crav1-` so they group under `/crav1`.

It does **not** create an app for you. It writes and walks specs, plans, tasks, and verify/fix loops **in the repo you already have** (or that you ask the agent to scaffold).

This kit repository is the source. Your product repository is where work happens. Cursor drop-in plus `plugins/crav1/` is the source of the playbooks. `.claude/` is generated from that source (`scripts/sync-crav1-plugin.sh`). Do not keep a second hand-written copy of the skills.

## License

[MIT](../LICENSE). The copyright notice is in that file.

## What gets installed

| Piece | Role |
| --- | --- |
| Skills (`/crav1-…`) | Playbooks: spark/ideas/intake → spec → plan → review-plan → implement → verify → fix → draft commit → `/crav1-open-pr` → `/crav1-review-pr` (named pull request only) → `/crav1-merge-pr` (explicit ask, merge commit only). Plan names a linter when the repo has one and stops before Build when it does not. Cross-cutting `/crav1-security-review` after architecture exists (whole system, one spec, or the change in front of you). Cross-cutting `/crav1-fix-bug` when a real bug is already named (one of the startup options; not a new lane; not a stretch of verify). Spark, plan, and verify do not run the security review. Spark, specify, and verify do not run the pull request review. Spark, specify, plan, and verify do not run the bug intake |
| Agents | `crav1-spec-reviewer-agent`, `crav1-architecture-reviewer-agent`, `crav1-plan-reviewer-agent` (read-only critics); `crav1-complete-task-agent` and `crav1-intake-slice-agent` (writers) |
| Project instruction | Cursor: rule `crav1.mdc`. Claude Code: `.claude/CLAUDE.md` (same short text, not the README) |
| Templates | Inside each skill’s `assets/` (and agent-assets). Optional human copies: `docs/specs/_template/`, `docs/system/_template/` |

Not installed by the Cursor plugin: this repo’s long README, `AGENTS.md`, `docs/specs/_template/`, or `docs/system/_template/`. Copy those starter folders yourself if you want them in git.

## Project drop-in or user scope

**Project drop-in** — commit `.cursor/` or `.claude/` in a repository you own. Clones and teammates get the same kit.

**User scope** — the kit follows you and is not committed into the repo. Cursor: user-scoped plugin (below). Claude Code: `~/.claude/`.

**Client project** — install into the user Claude config (`~/.claude`), not committed into the client repo, unless that project asked for the kit in git. The same idea on Cursor is a user-scoped plugin, not a commit of `.cursor/` into the client repo, unless they asked.

## Host plan UI is not `plan.md`

Cursor Plan Mode and Claude Code plan mode are each host’s plan UI. Neither one is `docs/specs/<slug>/plan.md`. `/crav1-plan-from-spec` writes `plan.md` and `tasks.md` itself. Use the UI only when you want a plan that stays in the chat and not in those files.

## Slash commands

After install, type `/crav1` to list the kit. Each skill folder’s `name:` is `crav1-<short-name>`, and the command is `/crav1-<short-name>`.

- **Cursor** project skills live under `.cursor/skills/crav1/`. If `/crav1` is missing, `Developer: Reload Window`.
- **Claude Code** project skills live under `.claude/skills/<name>/SKILL.md`. User skills live under `~/.claude/skills/<name>/SKILL.md`. If a skills or agents directory was created after the session started, restart Claude Code so it picks the new directory up. Checked against [Claude Code skills](https://code.claude.com/docs/en/skills) and [subagents](https://code.claude.com/docs/en/sub-agents).

## Cursor

### Prerequisites

- [Cursor](https://cursor.com/) with Agent chat (slash skills).
- A **product git repo** (or this kit repo, which already has the drop-in `.cursor/` tree).
- Optional: Teams or Enterprise, if you want a **team marketplace** (import this repo, then Install). Free/Pro can still **copy files** or load a **local plugin**.

**Import from Repo** for this kit uses [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).

### A. Drop-in copy (files in the product repo)

Works on any plan. Skills travel with clones, PRs, and Cloud Agents that use **project** files. Updates are a later copy (or git subtree).

From a clone of this kit:

1. Copy into the **product** repo:
   - `.cursor/skills/crav1/`
   - `.cursor/agents/crav1-*.md`
   - `.cursor/agent-assets/crav1-*`
   - `.cursor/rules/crav1.mdc`
2. Optionally copy `docs/specs/_template/`, `docs/system/_template/`, and add a line to the product `AGENTS.md` pointing at `docs/specs/` and `docs/system/`.
3. Commit those files in the product repo when you own it.
4. Reload Cursor if `/crav1` does not show up (`Developer: Reload Window`).

Do **not** copy `.cursor/rules/kit-maintainer.mdc` unless you are forking the kit itself. That rule is for maintainers of this repository (no `crav1-` prefix on purpose, so a `crav1*` dump skips it).

Cursor rules: [Rules](https://cursor.com/docs/rules). Cursor skills: [Skills](https://cursor.com/docs/skills).

### B. Cursor plugin (install from this repo)

The plugin lives at [`plugins/crav1/`](../plugins/crav1/) with manifest [`plugin.json`](../plugins/crav1/.cursor-plugin/plugin.json). Plugin id: `crav1`. The catalog is [`.cursor-plugin/marketplace.json`](../.cursor-plugin/marketplace.json). That catalog is **Cursor-only**. There is no public Cursor Marketplace listing.

**Team marketplace (Teams / Enterprise)**

1. Cursor Dashboard → **Plugins & MCPs** → **Team Marketplaces** → **Add Marketplace** → **Import from Repo**, and use [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit).
2. Confirm plugin `crav1`. Set access and Default Off / Default On / Required. Save. Enable Auto Refresh on GitHub if you want pushes to re-index.
3. In the IDE: **Customize** → find **crav1** → **Install** → project or user scope.

**No public listing**

There is no public Cursor Marketplace listing for plugin `crav1`. Install it from this GitHub repo: team marketplace import (above) or a local plugin (below). A drop-in copy of `.cursor/` is the other Cursor path (section A).

**CLI**

`cursor-agent plugin marketplace add <repository-url>` adds this repo as a Cursor marketplace. It does not publish a public listing. Installing a plugin is still interactive (Customize or `/plugin`). There is no reliable non-interactive `plugin install` for CI yet.

**Scope**

- **Project** — this workspace. Prefer this so Cloud Agents and teammates see the same kit.
- **User** — follows you across repos; does not put files in git. Use this on a client project unless that project asked for the kit in git.

### C. Local plugin (kit development)

1. Copy or symlink **inside** `~/.cursor/plugins/local/` only (Cursor ignores symlinks that point outside that folder):

   ```bash
   mkdir -p ~/.cursor/plugins/local
   cp -a plugins/crav1 ~/.cursor/plugins/local/crav1
   ```

2. Reload the window. Confirm **crav1** in **Customize**.
3. Teams/Enterprise admins may disable local plugin imports.

After you change the kit, re-copy or re-run the sync script, then reload.

Cursor plugin format: [Plugins](https://cursor.com/docs/plugins) · [Plugins reference](https://cursor.com/docs/reference/plugins).

## Claude Code

Claude Code has no plugin and no marketplace. The same slash commands as on Cursor live in the generated `.claude/` tree. Copy that tree into a repository you own, or into `~/.claude` for a client project. Cloning this kit does not install it into another product.

Checked against current Claude Code docs (not a guessed layout):

| What | Project (repo you own) | User (`~/.claude/`) | Doc |
| --- | --- | --- | --- |
| Skills | `.claude/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` | [Skills](https://code.claude.com/docs/en/skills) |
| Subagents | `.claude/agents/*.md` | `~/.claude/agents/*.md` | [Subagents](https://code.claude.com/docs/en/sub-agents) |
| Project instruction | `.claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | [Memory](https://code.claude.com/docs/en/memory) |
| Commit-style persist rule | `.claude/rules/*.md` | `~/.claude/rules/*.md` | [Memory](https://code.claude.com/docs/en/memory) |

Docs also allow a project instruction at `./CLAUDE.md`. This kit uses `.claude/CLAUDE.md` so the drop-in is one directory and does not replace a product’s root `CLAUDE.md`. Both paths are loaded ([directory overview](https://code.claude.com/docs/en/claude-directory)).

`.claude/agent-assets/` is **not** a directory Claude Code loads by itself. The subagent prompts tell the model to read those template files. They are not under `.claude/agents/` because Claude Code scans that tree recursively and would treat extra markdown as subagents.

### Project drop-in

From a clone of this kit, copy into a repository you own and commit it when that project asked for the kit in git:

- `.claude/skills/`
- `.claude/agents/`
- `.claude/agent-assets/`
- `.claude/CLAUDE.md`

Do not copy `.cursor/rules/kit-maintainer.mdc`.

### User scope (client project)

Copy into the user config. Do not commit these files into the client repo unless that project asked for the kit in git.

```bash
mkdir -p ~/.claude
cp -a .claude/skills ~/.claude/skills
cp -a .claude/agents ~/.claude/agents
cp -a .claude/agent-assets ~/.claude/agent-assets
```

Append `.claude/CLAUDE.md` to `~/.claude/CLAUDE.md` if you want the short kit instruction in every project. Do not overwrite an existing `~/.claude/CLAUDE.md`.

Playbooks name project paths (`.claude/skills/…`). If that file is not in the repo, read the same path under `~/.claude/`. The generated `CLAUDE.md` says this.

Onward commit style on a client repo writes `~/.claude/rules/draft-commit-style.md` or `draft-commit-gitlog.md` (user rules, loaded for every project). A repo that committed the kit writes `.claude/rules/` instead, same idea as Cursor’s `.cursor/rules/draft-commit-*.mdc`.

### Agents

Cursor `model: inherit` is omitted. Claude Code’s default is the parent model ([subagents](https://code.claude.com/docs/en/sub-agents)). The three reviewers (`crav1-spec-reviewer-agent`, `crav1-architecture-reviewer-agent`, `crav1-plan-reviewer-agent`) set `tools: Read, Grep, Glob` instead of Cursor `readonly: true`. The two writers omit `tools`, so they can edit.

### Tried on Claude Code

On Claude Code 2.1.286, in a private throwaway git repo, the generated `.claude/` drop-in ran `/crav1-spark-to-spec`, `/crav1-plan-from-spec`, one implement task, and `/crav1-verify-spec`. The trial feature was a root `hello.txt` of exactly the five bytes `68 65 6c 6c 6f`. Verify passed. Nothing from that repo was pushed. Two frictions: a PowerShell byte-dump that uses a script block was blocked by Claude Code’s permission check, and the same bytes were checked another way; the feature-branch skill wants a clean tree, and the branch was created with the kit files still untracked.

## After install

New to the loop? [First 15 minutes](first-run.md): open the product repo → `/crav1` → `/crav1-spark-to-spec` → tighten → plan → one task.

1. Open a chat in the **product** repo. On Cursor that is Agent chat. On Claude Code, open a session in that repo.
2. Type `/crav1` and run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, or `/crav1-match-to-specs`. Brownfield: expect a branch prompt (`feat/<slug>` or `spec/<slug>`). A bug that already exists is `/crav1-fix-bug`, one of the startup options. It is not a skill that runs because a repo is new, and it is not started automatically.
3. Follow the command loop. Do not start in the host plan UI or by picking a stack. `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`.

`/crav1-complete-tasks`, standalone `/crav1-complete-task`, and `/crav1-complete-features` **pause once** before the first worker, wait for `continue` / `click`, then remind you how to restore the previous gate when the run ends. On Cursor that gate is Approvals & Execution. On Claude Code it is the permission prompt (`/permissions`); the skill does not set a permission mode. Workers launched by those orchestrators do not pause again. The skill cannot change host settings for you.

If this window is the **kit repo**, drop-in skills are already under `.cursor/` and `.claude/` — no extra install.

## Keeping the kit updated

| You installed with | Update by |
| --- | --- |
| Cursor drop-in copy | Copy the same `.cursor/` folders again from a newer kit; commit in the product repo |
| Claude Code drop-in | Copy the same `.claude/` tree again (project) or into `~/.claude/` (user) |
| Cursor team marketplace | Auto Refresh or Dashboard **Refresh**, then update/reinstall the plugin if Cursor asks |
| Cursor local plugin | `scripts/sync-crav1-plugin.sh` in the kit, copy `plugins/crav1` to `~/.cursor/plugins/local/crav1`, reload |

Kit maintainers: edit `.cursor/` first, run `scripts/sync-crav1-plugin.sh` (plugin mirror and `.claude/`). `scripts/sync-crav1-claude.sh --check` fails if `.claude/` is stale. Keep this file and `plugins/crav1/README.md` accurate. Rule: `.cursor/rules/kit-maintainer.mdc`.

## Using the kit without “installing”

Clone this repository and work in it. Commands work here because `.cursor/skills/crav1/` and `.claude/skills/` are already present. That is not an install into another product. Copy the host drop-in, or on Cursor install plugin `crav1`, when a product repo should get the same commands.

## Clone

```bash
git clone https://github.com/Crav1on/crav1-spec-kit.git
```

The kit is at [https://github.com/Crav1on/crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). Cloning this repository does not install the kit into another product. To use the commands there, copy the drop-in for that host (Cursor `.cursor/` or Claude Code `.claude/`) or, on Cursor, install plugin `crav1` from this repo (team marketplace import or a local plugin). See the sections above.

## What to read next

| Situation | Doc |
| --- | --- |
| Just installed; want install through one task | [first-run.md](first-run.md) |
| Cursor plugin just installed, want the command order | [plugins/crav1/README.md](../plugins/crav1/README.md) |
| One-sentence spark | [docs/from-nothing.md](from-nothing.md) |
| Pile of ideas + tech hunches | [docs/from-ideas.md](from-ideas.md) |
| Mixed files / several features or repos | [docs/from-intake.md](from-intake.md) |
| Existing repos plus a dump to match | [docs/from-match.md](from-match.md) |
| A later dump onto specs that already exist | [docs/from-match-dump.md](from-match-dump.md) |
| A code change that already landed, specs already exist | [docs/from-code.md](from-code.md) |
| New information for one existing spec | [docs/from-add.md](from-add.md) |
| Security review after architecture exists | [docs/from-security.md](from-security.md) |
| Review a named open pull request | [docs/from-review-pr.md](from-review-pr.md) |
| A bug that already exists | [docs/from-fix-bug.md](from-fix-bug.md) |
| The method (specs, plan files, tasks, verify) | [README.md](../README.md) |
| Which lane owns a `/crav1-…` skill or `*-agent` | [guild-routing.md](guild-routing.md) |
| How a skill on main behaves | Behavior map in [`.cursor/rules/kit-maintainer.mdc`](../.cursor/rules/kit-maintainer.mdc) (this kit repo only) |
