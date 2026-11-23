# CRAV1 Spec Kit: supporting several AI coding tools ("vendors")

Research proposal, revised with Thomas's decisions (21 Nov 2026). Read-only: no code, PRs or pushes. Based on kit v1.199.0 (`main` at 22d4346) and official vendor docs read on 21 Nov 2026. Nothing starts before 22 Nov.

---

## 1. Recommendation (as decided)

1. **A vendor is data, not new code paths.** One small vendor table in the update-kit skill (`vendors.json`) lists, per vendor, the folders the kit owns, the frontmatter it needs, its command prefix and its extra files. The hard-coded Cursor and Claude Code allow-lists in `update_kit.py` (`is_cursor_kit`, `is_claude_kit`, `collect_kit`) become rows in that table; Codex and Copilot are two more rows.
2. **One generated, full copy per vendor**, each in that vendor's own native folder:
   - Codex: `.agents/skills/`, plus `agents/openai.yaml` for each command-only skill.
   - GitHub Copilot: `.github/skills/`, plus a kit-owned `.github/instructions/crav1.instructions.md`.
   - Claude Code: `.claude/skills/` (as today).
   - Cursor: keeps `.cursor/skills/crav1/` (as today).
   The kit repo commits the generated Codex and Copilot trees under `vendors/codex/` and `vendors/copilot/`, paths no tool loads, and CI checks them for drift the same way `.claude/` is checked today.
3. **Each copy knows its vendor.** The generator writes the right command prefix into that copy (`$crav1-x` in Codex, `/crav1-x` everywhere else), and the copy's skills pass `--vendor <name>` to the scripts that print Run next, so endings show only the right form.
4. **Always-on kit rules** come from a first line in each generated skill ("Read `../crav1-docs/reference/kit-rules.md` first") plus the kit-owned Copilot instructions file. The project's `AGENTS.md` is never written.
5. **A repo's vendor list lives in `.crav1/kit.json`**, written by the installer and changed by `add` or `remove`.
6. **Adding or removing a vendor reuses the update machinery**: the same three-way plan and apply with an empty "old" side, the same heads-up card, the one yes, `project_untouched`, and one commit. `/crav1-update-kit add codex`, `/crav1-update-kit remove copilot`. A repo with no kit gets a one-line bootstrap shaped like the dry-run tester.
7. **Order after 1.200:** vendor table, generator and checks, Codex, Copilot, installer. Thomas dry-runs each PR on his real spec and live-tests Codex and Copilot himself (setup checklist in the appendix).

---

## 2. Vendor facts

Sources are listed at the end of this section. "Verified" means it was read in official docs today. "Unverified" means it needs a live test.

| Topic | Claude Code | Cursor | OpenAI Codex (CLI, IDE extension, desktop app) | GitHub Copilot (VS Code agent mode, Copilot CLI, cloud agent) |
|---|---|---|---|---|
| Agent Skills `SKILL.md` standard | Yes | Yes | Yes, "build on the open agent skills standard" | Yes, "open standard (agentskills.io)" |
| Project skill folders | `.claude/skills/<name>/SKILL.md` only | `.agents/skills/`, `.cursor/skills/`, and for compatibility `.claude/skills/` and `.codex/skills/` | `.agents/skills/`, from the current folder up to the repo root. The VS Code Codex integration (experimental) also reads `.github/skills/` | `.github/skills/`, `.claude/skills/` and `.agents/skills/` (CLI and cloud agent docs). The VS Code table lists `.github/skills/` as the Copilot harness location, "not every directory it recognizes" |
| User-level folders | `~/.claude/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | `~/.agents/skills/`, `/etc/codex/skills` | `~/.copilot/skills/`, `~/.agents/skills/` |
| Name rules | Folder name, or frontmatter `name` | Standard | `name` and `description` required | `name` must equal the folder name, lowercase with hyphens, max 64 characters. A bad name means it "silently fail[s] to load" |
| Command-only switch (kit: 45 of 47 skills) | `disable-model-invocation: true` | `disable-model-invocation: true` (it appears in Cursor's migrate-to-skills output) | `agents/openai.yaml` → `policy: allow_implicit_invocation: false`. The frontmatter key is not documented | `disable-model-invocation: true` (VS Code). `user-invocable` hides a skill from the `/` menu |
| How the user runs a skill | `/crav1-…` | `/crav1-…` | `$crav1-…` mention, or the `/skills` picker. **Not `/`** | `/crav1-…` in VS Code chat and the CLI. In the CLI, "Use the /name skill …" |
| Always-on project text | `.claude/CLAUDE.md` | `.cursor/rules/*.mdc` (alwaysApply), `AGENTS.md` | `AGENTS.md` / `AGENTS.override.md` per folder, 32 KiB total limit by default | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (`applyTo`), `AGENTS.md` (the nearest one wins), or a root `CLAUDE.md` |
| Subagents / custom agents | `.claude/agents/*.md` | `.cursor/agents/*.md` | On by default. Custom agents live in `.codex/agents/*.toml`. A skill or `AGENTS.md` can ask for delegation | Custom agents in `.github/agents/*.agent.md`. VS Code skills can run `context: fork` (experimental) |
| Question cards (kit: at most 4 options, recommended first) | AskUserQuestion | AskQuestion | `request_user_input`: 1 to 3 questions with **2 to 3 options**, "(Recommended)" first, and "Other" added automatically. **Available only in some modes** (from the source code; unverified in the docs) | VS Code `askQuestions` (in core since March 2026, 2 to 4 options, recommended marked). Copilot CLI: unverified. Cloud agent: none (it is non-interactive) |
| Running the kit's Python scripts | Yes | Yes | Yes. Sandbox and approvals apply, and the network is often off by default, which affects `update_kit.py fetch` (unverified for the current defaults) | Yes. The CLI asks before running shell commands unless `allowed-tools` pre-approves them. The cloud agent sits behind a firewall |
| Extra frontmatter keys (kit uses `icon`, `color`) | Ignored | Used | Unknown, so strip them in the generated copy | Unknown, so strip them in the generated copy |
| Skill list budget | n/a | n/a | About 2% of context or 8,000 characters. **The kit's 47 descriptions total about 11,900 characters**, so Codex will shorten them. That is harmless for command-only skills | n/a |

### What each vendor can't do that the kit relies on, and how the kit degrades

| Kit feature | Gap | Fallback |
|---|---|---|
| Question cards with 4 options | Codex allows at most 3, and only in some modes. The Copilot cloud agent can't ask at all | The kit already accepts **choice words as plain text answers**. The generated Codex and Copilot copies add one line to `question-cards.md`: "If the host has no card tool, or allows fewer options, print the options as a numbered list with their choice words and wait for the reply." Cards stay at most 4 in the source |
| `/crav1-…` in Run next lines | Codex uses `$` | The Codex copy is generated with `$crav1-x`, and its skills call the ending scripts with `--vendor codex`, so Codex users see only `$crav1-x`. Other copies keep `/crav1-x` |
| Subagents (`crav1-spec-reviewer-agent` and four others) | Each vendor has a different agent file format | Phase 1: when the named agent is missing, the skill does the review itself in a separate pass that reads the agent's instructions from `crav1-docs`. Later phases generate `.github/agents/crav1-*.agent.md` and `.codex/agents/crav1-*.toml` |
| Always-on kit rules (`crav1.mdc`) | Codex has only `AGENTS.md`, which the project owns | Each generated `SKILL.md` opens with one line: "Read `../crav1-docs/reference/kit-rules.md` first." Copilot also gets a kit-owned `.github/instructions/crav1.instructions.md` (`applyTo: "**"`). The project's `AGENTS.md` is never written |
| `update_kit.py fetch` (git clone) | The Codex sandbox or Copilot cloud firewall may block the network | The skill says so in one line and offers the plain terminal command |
| Cloud or headless runs | No questions can be asked | Already covered, because the walks stop at the first needed yes |

### Sources

- Codex skills: https://developers.openai.com/codex/skills
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex subagents and custom agents: https://developers.openai.com/codex/subagents
- Codex `request_user_input` (source code): https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input_spec.rs
- Copilot agent skills: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- Copilot CLI skills: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills
- Copilot CLI custom agents: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- Copilot repository instructions (AGENTS.md, CLAUDE.md): https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- VS Code agent skills (locations, `disable-model-invocation`, `user-invocable`, `context: fork`, Local harness deprecation in Feb 2027): https://code.visualstudio.com/docs/copilot/customization/agent-skills
- VS Code prompt files (`.github/prompts/*.prompt.md`, Local harness only, and "create a skill" for the Copilot harness): https://code.visualstudio.com/docs/copilot/customization/prompt-files
- VS Code custom agents: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- VS Code askQuestions: https://code.visualstudio.com/updates/v1_109 and https://github.com/microsoft/vscode-copilot-chat/blob/main/CHANGELOG.md
- Claude Code skills: https://code.claude.com/docs/en/skills
- Cursor skills: https://cursor.com/docs/context/skills
- Agent Skills spec: https://agentskills.io/specification

**Note on prompt files:** in VS Code, `.prompt.md` files now run only in the deprecated Local harness, and the docs tell you to turn workflows into skills. So the kit should **not** generate prompt files. Skills are the one format that covers all four vendors.

---

## 3. What exists in the kit today (grounding) (grounding)

- **Source and copies.** The source is `.cursor/` plus `plugins/crav1/`. `scripts/sync-crav1-claude.py` generates `.claude/` with path rewrites (`PATH_REWRITES`) and agent frontmatter changes, and `--check` fails CI on drift. That is exactly the pattern a third generated tree needs.
- **Skill registry.** `docs/reference/skills.yaml` is the registry. `scripts/gen-skill-docs.py --check` already fails when a skill folder is missing from the registry or listed twice.
- **Names.** All 47 skill names already meet the Agent Skills name rule, and each name equals its folder. The largest description is 360 characters, under the 1024 limit. The only non-standard frontmatter is `icon` and `color`.
- **Command-only skills.** 45 skills are command-only (`disable-model-invocation: true`). Only `crav1-help` and `crav1-update-kit` can start on their own. `crav1-docs` is a bundled docs folder, not a skill, which explains the hand-made "47 vs 48" gap.
- **update_kit.py (stdlib only).**
  - `detect` finds the Cursor and Claude drop-ins by marker file.
  - `collect_kit` and `is_kit_path` hold hard-coded allow-lists per host.
  - `build_actions` runs the three-way merge (update, add, merge, delete, clash, left_extra), and `plan_view` reports `project_untouched: True`.
  - `apply_overlay` writes only allow-listed paths, and `commit_kit` makes one commit.
  - Migrations come from `migrations.json`.
  - `overlay.md` says: "Do not create the other host's tree." Today there is **no way to add a host**.
- **Size.** Each host tree is about 9.3 MB and 674 files, mostly the bundled `crav1-docs`.
- **Dry-run tester.** The maintainer dry-run tester clones the PR kit, makes a temp worktree, runs `detect`, `plan` and `apply` from the installed tag to the PR, runs readiness checks, and snapshots branch, HEAD, status, stash and worktrees before and after.

---

## 4. Layout (decided: one generated copy per vendor)

Options considered: generated pointer files, one shared `.agents/skills` copy for several vendors, and one full copy per vendor. **Thomas chose one full copy per vendor.**

| Vendor | Skills folder written | Vendor extras (kit-owned) | Prefix in that copy | Tree in the kit repo |
|---|---|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/agents/crav1-*.md`, `.claude/agent-assets/crav1-*`, `.claude/CLAUDE.md` (as today) | `/` | `.claude/` (as today) |
| Cursor | `.cursor/skills/crav1/` | `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, `.cursor/rules/crav1.mdc` (as today) | `/` | `.cursor/` (the source, as today) |
| Codex | `.agents/skills/` | `.agents/skills/<name>/agents/openai.yaml` per command-only skill | `$` | `vendors/codex/` |
| GitHub Copilot | `.github/skills/` | `.github/instructions/crav1.instructions.md` (`applyTo: "**"`) | `/` | `vendors/copilot/` |

**Why this works:** each copy is self-contained and its text is tuned for its vendor (prefix, paths, card fallback). Adding or removing a vendor touches only that vendor's folder. The cost is about 9 MB and 674 files per extra vendor, mostly the bundled `crav1-docs`. Slimming `crav1-docs` is a later option, not part of this plan.

**Generator:** `scripts/sync-crav1-vendors.py` reads the `.cursor` source, `skills.yaml` and the vendor table, and writes `vendors/codex/` and `vendors/copilot/`. Per vendor it applies:
- standard frontmatter only: `name`, `description`, `license: MIT`, `disable-model-invocation`, and `metadata.crav1-vendor` and `metadata.crav1-version` (`icon` and `color` are dropped)
- path rewrites to that vendor's folders, as the Claude sync does today
- the vendor's command prefix in Run next lines and command names (`$crav1-x` for Codex, `/crav1-x` for Copilot)
- `--vendor <name>` on every Run next script call in the skills (`update_kit.py ending`, `walk_progress.py` endings and the others), so the scripts print the right prefix
- `openai.yaml` with `policy: allow_implicit_invocation: false` for every command-only skill (Codex only)
- the kit-rules first line, and the card fallback line in `question-cards.md`
- a header comment in each generated `SKILL.md`: generated, do not edit

**Ending scripts:** the scripts that print Run next get `--vendor <cursor|claude|codex|copilot>`, default `cursor`/`/` so current output does not change. With `--vendor codex` they print `$crav1-x`.

---

## 5. Vendor-selection config (decided: `.crav1/kit.json`)

```json
{
  "schema": 1,
  "vendors": ["claude", "codex"]
}
```

- **Allowed values** come from the kit's vendor table: `cursor`, `claude`, `codex`, `copilot`. An unknown value is refused with a one-line reason.
- **The version is not stored here.** It stays where it is read from today (the marker or CHANGELOG), so there's one source.
- **A missing file means inferred vendors**, taken from the vendor trees present (today's behaviour). The next update offers to write the file in the same commit, after the same yes.
- **Why JSON:** `update_kit.py` is stdlib only, so it has no YAML parser.
- **Why `.crav1/`:** a kit-named folder, separate from `docs/system/` (project notes) and from tool folders.

**Kit-side vendor table** (`crav1-update-kit/vendors.json`), one row per vendor:

```json
{"codex":   {"skills": ".agents/skills", "tree": "vendors/codex", "prefix": "$",
             "extras": ["<skill>/agents/openai.yaml"],
             "marker": ".agents/skills/crav1-docs/reference/workflow.md"},
 "copilot": {"skills": ".github/skills", "tree": "vendors/copilot", "prefix": "/",
             "extras": [".github/instructions/crav1.instructions.md"],
             "marker": ".github/skills/crav1-docs/reference/workflow.md"},
 "claude":  {"skills": ".claude/skills", "tree": ".claude", "prefix": "/", "...": "today's allow-list"},
 "cursor":  {"skills": ".cursor/skills/crav1", "tree": ".cursor", "prefix": "/", "...": "today's allow-list"}}
```

`collect_kit` and `is_kit_path` read this table instead of their hard-coded lists. That refactor has no behaviour change and lands first.

---

## 6. Install and update flow

### Existing repo adds a vendor

For example, a repo on the Claude drop-in wants Codex.

1. The user runs `/crav1-update-kit add codex`. The skill reads `heads-up.md` and runs `detect`, which now also prints `vendors` and `vendors_from: kit.json|inferred`.
2. The kit runs `update_kit.py plan --add codex --new <tree of the installed tag>`.
   - The installed tag is used, not latest, so adding a vendor never also upgrades.
   - Adding and updating together is allowed: `add codex to v1.20x.0`.
3. **The old side for the new vendor is empty**, so `build_actions` classifies every file as `add`. A file that already exists locally shows as a `clash` on the card.
4. **Heads-up card:** the same card, listing the files to add, `.crav1/kit.json` as written, and anything left alone. The three choices stay: `yes, write and commit (Recommended)`, `write only`, `stop`.
5. `apply --yes` writes only that vendor's allow-listed paths plus `.crav1/kit.json`, then makes one commit: `Add CRAV1 kit vendor codex v1.20x.0`.
6. The ending is Run next, in the right prefix for the vendor the user is running in, with "reload the window / restart Codex so the new skills load".

### Remove a vendor

1. The user runs `/crav1-update-kit remove copilot`.
2. The plan deletes that vendor's kit-owned files that still match the installed release. A local edit is a clash, and the card offers `keep` or `take`.
3. `kit.json` is updated and the change goes in one commit. Other vendors' folders are not touched.

### Normal update

`/crav1-update-kit` updates **every vendor in `kit.json`** in one plan, card and commit. Nothing else changes from today.

### Repo with no kit yet (bootstrap)

A one-liner, the same shape as the dry-run tester, pinned to a release tag rather than `main`. It downloads `update_kit.py` to a temp file, runs `install --vendors codex --to latest --root .`, prints the plan, and writes only after `--yes`, which the user types after reading the plan. The temp file is deleted afterwards. From then on the user runs `/crav1-update-kit` (or `$crav1-update-kit` in Codex) inside the tool. In `detect` this is `mode: none`.

### `project_untouched` guarantees kept

- Writes go only to each vendor's allow-listed paths and `.crav1/kit.json`.
- The project's `AGENTS.md`, `.github/copilot-instructions.md`, README, specs and notes are never written.
- The plan JSON still reports `project_untouched: true`, and tests assert it.

### The teammate's hand-made Codex branch

Thomas deletes it. No migration is needed for its pointer files. A repo that still had hand-made files in `.agents/skills/` would see them as clashes on the add card, the normal way.

---

## 7. Checks and tests

**In CI (kit repo):**
- `sync-crav1-vendors.py --check` fails when `vendors/codex/` or `vendors/copilot/` differs from the generated result.
- New `kit-lint` rules, run per vendor tree:
  - every `skills.yaml` skill has exactly one folder in each vendor tree, with no extra or missing folders: 47/47 in Codex, Copilot, Claude and Cursor (the "47 vs 48" problem, caught for real; `crav1-docs` is bundled docs, not a skill)
  - `name` equals the folder name and meets the Agent Skills name rule
  - descriptions are at most 1024 characters
  - only standard frontmatter keys appear in the Codex and Copilot copies
  - Codex: exactly 45 `openai.yaml` files, one per command-only skill, each with `allow_implicit_invocation: false`, and none on `crav1-help` or `crav1-update-kit`
  - Copilot and Claude: 45 skills with `disable-model-invocation: true`
  - Copilot: `.github/instructions/crav1.instructions.md` present
  - no other vendor's paths in a copy (no `.cursor/`, `.claude/`, `.github/skills` in the Codex copy, and so on)
  - prefix: no `/crav1-` command in the Codex copy, no `$crav1-` in the others
  - every Run next script call in the Codex and Copilot copies passes `--vendor`
- Optional: run `skills-ref validate` from agentskills.io on the Codex and Copilot trees.

**Unit tests (`scripts/tests/test_kit_12xx.py`):**
- Adding a vendor: `add codex` into an empty repo, `add codex` on top of a Claude drop-in, `add copilot` next to Codex (each writes only its own folder).
- Removing a vendor: `remove codex` leaves Copilot, Claude and Cursor byte-identical.
- Config file: missing `kit.json`, so vendors are inferred and the file is offered; an unknown vendor is refused.
- Update and clashes: an update with two vendors produces one commit; a local edit in a vendor tree gives a clash card; a pre-existing hand-made file in `.agents/skills/` is a clash, not overwritten.
- Endings: `--vendor codex` prints `$crav1-x`; no `--vendor` prints today's output unchanged.
- Untouched files: `AGENTS.md`, `.github/copilot-instructions.md` and README stay byte-identical, and `project_untouched` is asserted for every path written.

**Live smoke checklist (Thomas, once per vendor per phase; setup in the appendix):**
1. The tool lists the 47 `crav1-*` skills.
2. `crav1-help` can start on its own, and a command-only skill does **not** start on its own.
3. `$crav1-help whats-new` in Codex, `/crav1-help whats-new` in Copilot, answers.
4. A walk asks one card question, or prints the numbered fallback.
5. A kit script runs, and its Run next line shows the right prefix.

---

## 8. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Vendor docs move fast (VS Code Local harness removed Feb 2027, the Codex VS Code integration is experimental, `askQuestions` changed recently) | Generated files stop working | The vendor table is data. Re-check the vendor facts every quarter, and repeat the smoke checklist |
| Codex question tool: at most 3 options, and only in some modes | Kit cards with 4 options get cut or fail | The numbered-list fallback with choice words. A lint warning for 4-option cards in skills Codex uses heavily |
| Codex skill-list budget (11.9k characters against an 8k default) | Descriptions shortened | Harmless for command-only skills. Keep the two auto-starting skills' descriptions front-loaded |
| Repo size (about +9 MB per extra vendor) | Slower clones | Only chosen vendors are written. Later, consider slimming `crav1-docs` in the generated copies |
| Sandbox or network limits (Codex sandbox, Copilot cloud agent firewall) | `fetch` fails | A one-line reason and the terminal command to run instead |
| Enterprise settings can turn off the Codex harness in VS Code | Codex inside VS Code is unavailable | Document it. Codex CLI still works |
| A vendor copy drifts back to another vendor's paths or prefix | Wrong paths or commands | The per-vendor lint rules for paths, prefix and `--vendor` |
| Live tests depend on one person | Regressions go unseen between vendor phases | CI covers structure; Thomas's smoke checklist at each vendor phase; the dry run on every PR |
| A generated copy is hand-edited | Edits lost on sync | The header comment in each generated `SKILL.md`, and CONTRIBUTING step 2 extended |

---

## 9. Phased build outline

v1.200.0 is already scoped (fixtures, the shared "waiting" judgement, tester tidy-ups and the PR lookup). Nothing here starts before 22 Nov. Each phase is one kit release with its own review PR, dry run and Thomas's go-ahead.

| Release | Scope | Consumer-visible? | Live test |
|---|---|---|---|
| **v1.201.0** | Vendor table (`vendors.json`); `collect_kit` / `is_kit_path` read it (no behaviour change). `detect` reports `vendors`. A read-only `update_kit.py vendors --root .` lists each vendor's folder and skill count. `--vendor` on the Run next scripts, default unchanged. Dry-run tester gets `--add` | Only the extra `detect` fields and the read-only `vendors` command | None needed |
| **v1.202.0** | `scripts/sync-crav1-vendors.py`, committed `vendors/codex/` and `vendors/copilot/` trees, CI `--check` and the per-vendor lint rules. No install path yet | No | Optional: Thomas copies a tree into a scratch repo |
| **v1.203.0** | `.crav1/kit.json`, `/crav1-update-kit add <vendor>` and `remove <vendor>`, the Codex row live. Docs: install.md Codex section, update-kit page, CHANGELOG | **Yes: Codex** | Thomas: Codex smoke on a scratch repo, then the dry run with `--add codex` |
| **v1.204.0** | The Copilot row live: `.github/skills/` and the instructions file. Docs for Copilot | **Yes: Copilot** | Thomas: VS Code agent mode and Copilot CLI smoke |
| **v1.205.0** | Bootstrap install for repos with no kit (`install --vendors …`), plus an install.md "pick your tool" page | Yes | Thomas: a fresh scratch repo per vendor |
| **later** | Generated custom agents (`.github/agents/crav1-*.agent.md`, `.codex/agents/crav1-*.toml`); more vendors as table rows | Yes | Per vendor |

---

## 10. Dry-run plan (before each merge)

Thomas runs the tester on his real spec for every PR, as today:

```
python -X utf8 <the maintainer dry-run tester> --pr N --spec "orders-api"
```

**Additions (v1.201.0):**
- `--add <vendor>` (repeatable) runs `plan --add` and `apply --add` inside the **temp worktree** after the normal update, then `update_kit.py vendors`. The real repo is still proven untouched by the existing snapshot comparison.
- **Output to copy** adds one block per vendor: the folder written, skill count against `skills.yaml`, command-only count, vendor extras, files added, merged or clashing, and `project_untouched: true`.

**Expected counts per vendor:**

| Vendor | Folder | Skills | Command-only | Extras |
|---|---|---|---|---|
| Codex | `.agents/skills/` | 47/47 | 45 `openai.yaml` | none |
| Copilot | `.github/skills/` | 47/47 | 45 with `disable-model-invocation: true` | 1 instructions file |
| Claude Code | `.claude/skills/` | 47/47 | 45 with `disable-model-invocation: true` | as today |
| Cursor | `.cursor/skills/crav1/` | 47/47 | 45 with `disable-model-invocation: true` | as today |

(Counts are for v1.199.0; they follow `skills.yaml` when skills are added or removed.)

**What to check per phase:**
- **v1.201.0:** the dry run without `--add` matches 1.200 output exactly, which proves the refactor has no effect.
- **v1.202.0:** dry run unchanged (no install path yet); CI shows both generated trees in sync.
- **v1.203.0:** `--add codex` shows the Codex row above, `$crav1-` in its Run next lines, and nothing written outside `.agents/` and `.crav1/`.
- **v1.204.0:** `--add codex --add copilot` writes both folders, each with its own counts; nothing outside `.agents/`, `.github/skills/`, `.github/instructions/crav1.instructions.md` and `.crav1/`.
- **v1.205.0:** a bootstrap run against an empty scratch folder (not the real repo).

---

## 11. Decided (Thomas, 21 Nov 2026)

1. **Layout:** one generated copy per vendor in its own folder: Codex `.agents/skills/`, Copilot `.github/skills/`, Claude Code `.claude/skills/`; Cursor keeps `.cursor/skills/crav1/`.
2. **Vendor list:** `.crav1/kit.json`.
3. **Always-on rules:** a first line in each generated skill plus a kit-owned Copilot instructions file; the project's `AGENTS.md` is never written.
4. **Command wording:** each copy knows its vendor. The generator writes `$crav1-x` in Codex and `/crav1-x` elsewhere, and skills pass `--vendor` to the Run next scripts. No "show both".
5. **Order after 1.200:** vendor table, generator and checks, Codex, Copilot, installer. Nothing starts before 22 Nov.
6. **Live tests:** Thomas tests Codex and Copilot himself (appendix below).
7. **The teammate's hand-made branch:** deleted by Thomas; no pointer-file migration.

---

## Appendix: Setup checklist for live testing Codex and Copilot on Windows

Use a **scratch repo**, not the real spec repo, for each smoke test.

### Codex

1. Install Codex CLI as the official page shows (npm or the Windows installer): https://developers.openai.com/codex/cli
2. Optional: the Codex IDE extension for VS Code: https://developers.openai.com/codex/ide
3. Run `codex` in the scratch repo and choose **Sign in with ChatGPT** (or another listed sign-in).
4. Windows sandbox: Codex runs natively in PowerShell with a Windows sandbox (MXC recommended; WSL is optional). Check it per https://developers.openai.com/codex/windows. Allow network when `update_kit.py fetch` needs it, or run that step in a normal terminal.
5. Skills: confirm `.agents/skills/` is picked up with `/skills` or by typing `$crav1`; restart Codex if new skills don't appear: https://developers.openai.com/codex/skills
6. Question tool and subagents behave per https://developers.openai.com/codex/subagents; note whether cards appear or the numbered fallback is used.

### GitHub Copilot

1. A Copilot plan on your GitHub account (Copilot CLI and agent skills need it).
2. **VS Code agent mode:** set up Copilot in VS Code: https://code.visualstudio.com/docs/copilot/setup. Open the scratch repo, switch chat to Agent, type `/` and check that the `crav1-*` skills from `.github/skills/` are listed: https://code.visualstudio.com/docs/copilot/customization/agent-skills
3. Optional: turn on `chat.askQuestions.enabled` if cards don't appear: https://code.visualstudio.com/updates/v1_109
4. **Copilot CLI:** install with `winget install GitHub.Copilot` or `npm install -g @github/copilot`: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli
5. Sign in: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli
6. In the scratch repo run `copilot`, then `/skills list` and `/skills info crav1-help`; `/skills reload` after adding skills: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills
7. Copilot asks before shell commands; approve the kit scripts per run (don't pre-approve `shell`).
8. Instructions file: confirm `.github/instructions/crav1.instructions.md` is applied: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions

### After each smoke

Paste the smoke checklist results (section 7) together with the dry-run output, the same way as the PR dry runs.
