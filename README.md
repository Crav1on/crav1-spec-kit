# CRAV1 Spec Kit (crav1)

**CRAV1 Spec Kit** (`crav1`) is a Cursor kit for spec-driven development: skills and agents that take a spark, a pile of ideas, or intake files through spec, plan, implement, verify, and a draft commit message. Specs, not chat history, are the source of truth. The plugin also ships a short usage rule.

Repo: [crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). Plugin id: `crav1`. After install, type `/crav1`.

This is a process guide, not an application. Use it as a checklist when you start a repo, then install the kit into that project.

**First 15 minutes:** [docs/first-run.md](docs/first-run.md). **Before you install:** [docs/install.md](docs/install.md) (drop-in copy, Cursor plugin, or local plugin). **After a plugin install:** [plugins/crav1/README.md](plugins/crav1/README.md). License: [MIT](LICENSE).

## First 15 minutes

Pick an install path, open the product repo, then `/crav1` → `/crav1-spark-to-spec` → tighten → plan → one task. The short path is [docs/first-run.md](docs/first-run.md). The sections below are the full playbook.

Primary sources: [Cursor docs](https://cursor.com/docs/), [Plan Mode](https://cursor.com/docs/agent/plan-mode), [Agent](https://cursor.com/docs/agent/overview), [Rules](https://cursor.com/docs/rules), [Skills](https://cursor.com/docs/skills), [Cloud Agents](https://cursor.com/docs/cloud-agent), [GitHub Spec Kit](https://github.com/github/spec-kit/), and [OpenSpec](https://github.com/Fission-AI/OpenSpec).

---

## 1. How the pieces fit together

Cursor’s agent is three things working at once: **instructions**, **tools**, and a **model**. Spec-driven development (SDD) is how you keep those three pointed at the same outcome when the work is larger than one prompt.

### The agent stack

| Layer | What it is | Role in SDD |
| --- | --- | --- |
| **Model** | The LLM you pick for the turn | Stronger reasoning models for specify/plan; faster models for isolated tasks |
| **Tools** | Search, read, edit, terminal, browser, web, questions | The agent can research, implement, and **verify** instead of only generating text |
| **Instructions** | System prompt + your rules, skills, and the spec in context | Persistent “how we work here”; specs are the current “what to build” |
| **Modes** | Ask, Plan, Agent (and Custom Modes) | Separate thinking from doing |
| **Checkpoints + Git** | Local undo vs permanent history | Roll back bad agent turns; keep specs and code versioned together |
| **Cloud Agents** | Same agent, isolated VM | Parallel, long-running, testable runs once the environment can build and test |

Cursor’s own team now starts most new features by having Agent write a plan first. Plan Mode exists because frontier models do better on long-horizon work when they have a reviewable spec with file paths, constraints, and to-dos.

### Spec-driven development in one sentence

Treat the specification as an **executable contract**: the agent generates, tests, and validates against it. Chat is steering. The spec is the source of truth. When the result is wrong, you fix the spec and rebuild, not endlessly patch code in follow-ups.

GitHub’s Spec Kit frames this as four gated phases:

1. **Specify** — user journeys, success criteria, non-goals (the *what* and *why*)
2. **Plan** — stack, architecture, constraints, interfaces (the *how*)
3. **Tasks** — small, independently testable units of work
4. **Implement** — the agent codes one task at a time; you verify

OpenSpec’s OPSX flow is the same idea without rigid waterfall gates: **explore → propose → apply → verify → sync/archive**, and you may update any artifact as understanding changes. That is a better fit for brownfield work.

### Map that onto Cursor

```
You (intent)
    │
    ├─ AGENTS.md / .cursor/rules     → standing project law
    ├─ Skills / Custom Modes         → playbooks (specify, implement, review)
    └─ Specs in the repo             → this change’s contract
            │
            ▼
     Plan Mode  ──►  reviewable Markdown plan + to-dos
            │
            ▼  you click Build / switch to Agent
     Agent Mode ──►  edits, tests, browser checks
            │
            ├─ Checkpoints  → undo this session
            ├─ Git          → keep spec + code together
            └─ Cloud Agent  → same loop off your laptop
```

**Rules vs skills vs specs** (do not collapse these):

- **Rules / `AGENTS.md`**: always-on or file-scoped constraints (stack, style, “never touch generated files”). Short, stable, rarely change.
- **Skills**: on-demand playbooks (“how we specify a feature”, “how we review a PR”). Load when relevant.
- **Specs / plans**: per-change artifacts. They expire or get archived when the change ships.

If you dump a whole product spec into always-on rules, you waste context and the agent treats yesterday’s feature as today’s law.

### What you should *not* spec-drive

Quick, well-understood edits (rename, copy tweak, one-file bug with a clear stack trace) belong in **Agent mode** immediately. Plan Mode and SDD pay off when:

- There are multiple valid designs
- Many files or systems are involved
- Requirements are still fuzzy
- You need an architectural checkpoint before code exists

---

## 2. From one sentence to a spec

If you have only a spark (one or two sentences), do **not** start in Plan Mode and do not paste a “senior architect” persona. Interview first, write `spec.md`, tighten it, *then* plan — **greenfield or a feature on an existing app**. Full walkthrough: [From one sentence to a spec](docs/from-nothing.md).

**First prompt** (Agent chat, strong reasoning model). Greenfield:

```text
/crav1-spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Do not write code. Ask questions first.
```

Brownfield feature (existing app): `@` the code; the skill writes a **new** spec slug unless you say extend. It **prompts** for `feat/<slug>` (spec+build) or `spec/<slug>` (specify-only; build later on `feat/<slug>` after that spec is on the default branch). No silent checkout, no PR.

```text
/crav1-spark-to-spec
@src

Spark: <one or two sentences for this feature>

Feature on this app. Preserve existing architecture. Do not write code.
```

Then: answer ≤7 questions (and the branch prompt) → agent writes `docs/specs/<slug>/spec.md` → `/crav1-tighten-spec` walks **each** finding → `/crav1-resolve-questions` walks leftover Open questions (keep open or answer) → optional `crav1-spec-reviewer-agent` → **`/crav1-plan-from-spec`** → `/crav1-review-plan` then `/crav1-tighten-plan` for plan `P#`s → `/crav1-implement-task` per `T#` or `/crav1-complete-task` / `/crav1-complete-tasks` (one spec) or `/crav1-complete-features` (several specs, serial) → `/crav1-verify-spec` → `/crav1-fix-from-verify` (omit Gap) for inner-loop remaining: failed → unverified → `G#`.

Runnable pieces in this repo:

| Piece | When | How |
| --- | --- | --- |
| Skill `/crav1-spark-to-spec` | You have 1–2 sentences (empty repo or a feature on an existing app) | Slash command; greenfield vs brownfield from context |
| Skill `/crav1-feature-branch` | Brownfield: get off the default branch | Prompt: `feat/<slug>` (spec+build) or `spec/<slug>` then `feat/<slug>` for build; no push, no PR |
| Skill `/crav1-architecture-reviewer` | Spec + diagrams/ADRs exist | Slash command; runs the reviewer subagent |
| Skill `/crav1-tighten-spec` | Spec exists, still mushy | Slash command; one issue at a time (option to get a suggestion); then edit |
| Skill `/crav1-resolve-questions` | Open questions remain after tightening | Slash command; keep-open or answer, one `Q#` at a time |
| Skill `/crav1-plan-from-spec` | Spec is accepted; want plan + tasks, no code | Slash command; writes `plan.md` and `tasks.md` |
| Skill `/crav1-review-plan` | Plan exists; want a critique | Slash command; numbered `P#`s for tighten-plan |
| Skill `/crav1-tighten-plan` | After review-plan, or mushy tasks | Slash command; one `P#` at a time; patches plan/tasks only |
| Skill `/crav1-implement-task` | `tasks.md` exists; build one slice | Slash command; one `T#`, then its verify |
| Skill `/crav1-complete-task` | One `T#` implement → done in an isolated worker | Persist commit style as a rule; auto-commit; parent relays fix/ready |
| Skill `/crav1-complete-tasks` | Several `T#`s to done | Orchestrates one complete-task worker per id; `T1-T3` or all unchecked |
| Skill `/crav1-complete-features` | Several **specs** to done, serial | One `feat/<slug>` from default at a time, then that slug’s T# loop; not parallel |
| Skill `/crav1-verify-spec` | Want proof against acceptance | Slash command; TL;DR then `verify.md` details |
| Skill `/crav1-fix-from-verify` | After verify-spec, inner-loop gaps | Slash command; omit Gap to walk failed → unverified → G# |
| Skill `/crav1-fix-live` | Live/inner-loop gap | Alias of `/crav1-fix-from-verify` |
| Skill `/crav1-draft-commit-message` | About to commit (GitKraken paste fields) | Slash command; style.md or git log, once or onward; no commit unless they ask |
| Skill `/crav1-finalize-commit` | Finish a message: git commit, GitKraken copy, or edit | Style first if needed, then draft, then **commit first**, then copy / edit / rewrite / stop; no push |
| Skill `/crav1-ideas-to-spec` | Pile of ideas + technical hunches | Slash command; pick an export format |
| Skill `/crav1-intake-to-specs` | 1–N files; maybe several features/repos | Slash command; landscape + one spec per v0 slug |
| Skill `/crav1-export-spec` | Spec exists, want another format | Slash command |
| Subagent `crav1-spec-reviewer-agent` | Independent product/spec critique | Agent delegates, or ask “review this spec” |
| Subagent `crav1-architecture-reviewer-agent` | Diagrams, ADRs, hunches vs decisions | Agent delegates |
| Subagent `crav1-plan-reviewer-agent` | Plan/tasks vs spec | Agent delegates; `/crav1-review-plan` |

## 3. From a pile of ideas (not a spark, not a spec)

When you already have several ideas and maybe stack opinions, use **`/crav1-ideas-to-spec`**, not `/crav1-spark-to-spec`. Full walkthrough: [From a pile of ideas to a spec](docs/from-ideas.md).

**First prompt:**

```text
/crav1-ideas-to-spec

<one blob: ideas, UX notes, stack hunches, constraints. No required structure.
Name an export format in the same text if you already know it, or wait for the ask.>

Treat hunches as proposed, not decided.
Do not write code. Capture first, then architecture questions.
```

Flow: cluster intent vs hunches → product questions if needed → **architecture interview** (≤7 questions, 2–3 options) → write `spec.md` + `diagrams.md` + ADRs + `export/<format>` → optional `/crav1-architecture-reviewer` → Plan Mode.

Canonical spec stays Markdown. EARS / BDD / OpenSpec / YAML / JSON / BMAD are exports. Mermaid for context and sequences; ASCII for trees and CLIs. ADRs only when there were real alternatives (MADR-shaped template). If the pile is several v0 features or several repos, `/crav1-ideas-to-spec` stops and you run `/crav1-intake-to-specs` instead.

## 4. From intake files (several features or repos)

When you have **1–N files** (notes, diagrams, screenshots, optional code as context) that may be a whole system, use **`/crav1-intake-to-specs`**. Full walkthrough: [From intake files to specs](docs/from-intake.md).

**First prompt:**

```text
/crav1-intake-to-specs
@notes/overview.md
@sketches/flow.png
@legacy-api/

Treat hunches as proposed, not decided.
Do not write code. Map first.
```

Default if you only `@` a codebase: new system, that code is **context** (not extract-as-is). The parent confirms a map (slugs, repos, bulk assumptions, mushy vs ready), writes `docs/system/`, then one isolated worker per v0 slug. Then it **prompts** `/crav1-finalize-commit` (does not commit itself). Later features use spark/ideas with `@docs/system/` — new slug, do not re-run intake.

## 5. The working loop (once a spec exists)

Use this on any non-trivial change.

### A. Specify (Ask or Plan Mode, read-heavy)

Describe the user problem, not the stack. Force:

- Who it is for
- Happy path and failure path
- Explicit **non-goals**
- Acceptance checks a stranger could run

Have the agent research the repo (search, read, existing tests). Answer clarifying questions. Do not skip them; Cursor documents that answer quality here dominates output quality later.

Write or update `docs/specs/<change>/spec.md` (or Spec Kit / OpenSpec’s layout). **You** accept this artifact before planning.

### B. Plan (Plan Mode)

`Shift+Tab` rotates into Plan Mode, or pick it from the mode dropdown. Cursor also suggests it when the prompt looks complex.

The agent researches, asks more questions, and writes a Markdown plan with file paths, code references, and to-dos. Edit the plan in the UI or on disk. Save it into the workspace so it is shared, not only in your home directory.

Treat the plan as a design review: wrong files, missing constraints, and oversized tasks are cheaper to fix here than after a 40-file diff.

### C. Task-slice

Every to-do should be implementable **and testable** in isolation. “Add authentication” is not a task. “POST `/register` rejects invalid email and has a test” is.

If a task cannot be verified, it is still part of the spec, not ready for Agent.

### D. Implement (Agent Mode)

Build from the plan. Prefer a **fresh chat** (or a `/goal` for a long-lived objective) so implementation context is not polluted by all the exploration.

Steer with queued follow-ups rather than interrupting mid-tool-call unless you need to redirect now. Use checkpoints if the agent diverges; Cursor’s docs recommend **reverting, tightening the plan, and rebuilding** instead of endless patch prompts.

Verify the same way a human would: tests, linters, and for UI work, the browser tools.

### E. Review and close the loop

Use `/review`, Bugbot, or a dedicated review subagent. Diff against the spec, not against “does it look plausible.” If behavior drifted, update the spec first, then the code. Archive or mark the change done so the next agent does not treat an in-flight proposal as current law.

---

## 6. How to set it up

You can stay native to Cursor, or layer Spec Kit / OpenSpec on top. Native Cursor is enough for most teams; the toolkits add templates and slash-command discipline.

### Step 1 — Standing instructions

At the repo root, add `AGENTS.md` with only what is true for every session: language, test command, architecture boundaries, “do not” list.

Add `.cursor/rules/*.mdc` when guidance is **scoped**:

- `alwaysApply: true` — rare, tiny, global (copyright header, never edit `dist/`)
- `globs` — frontend vs backend conventions
- `description` + intelligent apply — domain workflows
- Manual `@rule` — occasional playbooks you have not turned into skills yet

Cursor’s rule hygiene: keep each rule under ~500 lines, split by concern, **point at example files** instead of pasting style guides, and add a rule only after the agent repeats a mistake. Team Rules (Team/Enterprise) override project and user rules when they conflict.

### Step 2 — Spec layout in git

A layout that works without extra CLIs:

```text
docs/system/
  _template/
  landscape.md       # v0 vs later, bulk A#s, feature index
  repos.md           # named repos (proposed until a URL exists)
  diagrams.md
  adr/
docs/specs/
  _template/
    spec.md          # what / why / acceptance
    plan.md          # how / constraints / files
    tasks.md         # ordered, testable slices
    verify.md        # acceptance matrix after implementation
    fix-log.md       # one gap from verify-spec, fix + re-proof
    live-fix.md      # legacy; new incidents go in fix-log.md
  <change-id>/
    spec.md
    plan.md
    tasks.md
    verify.md
    fix-log.md
AGENTS.md
.cursor/rules/
.cursor/skills/      # or .agents/skills/
```

Save Plan Mode output into `docs/specs/<change>/plan.md` so Cloud Agents and teammates see it.

### Step 3 — Skills and Custom Modes

Create skills with `/create-skill`. New **crav1** skills go under `.cursor/skills/crav1/crav1-<name>/` with `name: crav1-<name>` so `/crav1` lists your library separately from Cursor built-ins. Keep `SKILL.md` short; put templates in that skill’s `assets/` (and `references/` for recipes).

Install into another repo: [docs/install.md](docs/install.md). Drop-in copy is `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc`. Plugin install uses `plugins/crav1/` plus `.cursor-plugin/marketplace.json`. Also copy `docs/specs/_template/` and `docs/system/_template/` if you want visible starter folders.

When you change a template, update `docs/specs/_template/` **and** every `assets/` / `agent-assets/` copy on **both** the drop-in tree and `plugins/crav1/` (`scripts/sync-crav1-plugin.sh`). Rule: `.cursor/rules/kit-maintainer.mdc` (kit repo only; do not dump with `crav1-*`).

This repo already ships:

- `/crav1-spark-to-spec` — one-liner → questions → `spec.md` (greenfield, brownfield feature, or later feature on `docs/system/`; new slug unless they extend)
- `/crav1-feature-branch` — prompt for `feat/<slug>` or specify-only `spec/<slug>`; no silent checkout, no push, no PR
- `/crav1-ideas-to-spec` — idea pile + technical hunches → spec, diagrams, ADRs, chosen export
- `/crav1-intake-to-specs` — mixed intake → `docs/system/` + one spec per v0 feature (isolated slice workers)
- `/crav1-architecture-reviewer` — run the crav1-architecture-reviewer-agent subagent; numbered issues at the end
- `/crav1-tighten-spec` — one issue at a time, with explained resolutions (plus get a suggestion) and impact; patch only that issue after you choose
- `/crav1-resolve-questions` — one Open question at a time; keep it open or answer with impact; patch only that `Q#`
- `/crav1-export-spec` — re-project `spec.md` into EARS, BDD, OpenSpec, YAML, JSON, or BMAD
- `/crav1-plan-from-spec` — file-level `plan.md` and testable `tasks.md`; refuses to code
- `/crav1-review-plan` — critique `plan.md` / `tasks.md` against the spec; numbered `P#`s
- `/crav1-tighten-plan` — one plan issue at a time; patches plan/tasks only (spec findings go to tighten-spec)
- `/crav1-implement-task` — one `tasks.md` row, then run its verify step
- `/crav1-complete-task` — isolated worker for one `T#`: implement → commit → verify → optional fix; persist commit style as a rule
- `/crav1-complete-tasks` — orchestrates one worker per `T#` (`T1-T3` or all unchecked); stops the batch when a worker needs you
- `/crav1-complete-features` — serial board of ready slugs: `feat/<slug>` from default, then that spec’s complete-tasks loop; no parallel, no push, no PR
- `/crav1-verify-spec` — TL;DR of implemented vs not, then acceptance details in `verify.md`
- `/crav1-fix-from-verify` — after verify-spec, walk inner-loop gaps (failed → unverified → `G#`); omit Gap for the next; writes `fix-log.md`
- `/crav1-fix-live` — alias when that gap is a live/inner-loop path
- `/crav1-draft-commit-message` — paste-ready GitKraken Summary/Description; `style.md` or live git log, once or onward (deletable rule); does not commit unless they ask
- `/crav1-finalize-commit` — same draft, then **commit first**, then copy for GitKraken, edit/rewrite, or stop (no push)
- subagent `crav1-spec-reviewer-agent` — independent product/spec critique
- subagent `crav1-architecture-reviewer-agent` — hunches vs decisions, diagrams, ADRs
- subagent `crav1-plan-reviewer-agent` — worker for `/crav1-review-plan` (`plan.md` / `tasks.md` vs spec)
- subagent `crav1-complete-task-agent` — worker for `/crav1-complete-task` / `/crav1-complete-tasks` / `/crav1-complete-features` (one `T#`)
- subagent `crav1-intake-slice-agent` — worker for `/crav1-intake-to-specs` (one feature slug)

Invoke with `/skill-name`, or pin a skill as a **Custom Mode** (`Option+Enter` / `Alt+Enter`) so it stays on for the session (for example `/crav1-implement-task` while you burn down `T#`s).

### Step 4 — Verification as part of the environment

An agent that cannot run tests will guess. Locally: document the exact test/lint/dev commands in `AGENTS.md`. For Cloud Agents, this is the highest-leverage setup: a real environment (deps, secrets, startup, network policy) so the agent can build, test, and use the browser. Cursor’s docs compare skipping this to “not giving engineers a computer.”

Optional: `.cursor/hooks.json` to format, block forbidden paths, or run checks after edits. Cloud Agents pick up **project** hooks, not your `~/.cursor/hooks.json`.

### Step 5 — Optional toolkits

**Spec Kit** (heavier, gated phases, great for greenfield and org-wide process):

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai cursor
```

Then use its constitution → specify → plan → tasks → implement skills/commands. There is a Cursor integration; if a named integration is missing, the generic agent path still works.

**OpenSpec** (lighter, iterative, better for existing codebases): keep delta specs per change; propose → apply → verify → archive without requiring a full waterfall.

You do not need both. Pick one template family and stay consistent.

### Step 6 — Day-to-day in the product

1. Open Agent (`Cmd/Ctrl+I`).
2. For a sizable change: Plan Mode (`Shift+Tab`).
3. Answer questions; edit the plan; **Save to workspace**.
4. Build. Watch diffs. Run tests.
5. If wrong: restore checkpoint, edit the plan, rebuild.
6. For long objectives: `/goal …` (optionally with a Custom Mode and `/loop`).
7. For parallel or unattended work: kick a **Cloud Agent** from desktop, [cursor.com/agents](https://cursor.com/agents), Slack, or `@cursor` on an issue/PR — after source control is connected.

---

## 7. Best practices (Cursor + Spec Kit + OpenSpec)

**Make intent unambiguous.** Models complete patterns; they do not read your mind. “Add photo sharing” hides thousands of decisions. Specs surface them before code exists.

**Separate what from how.** Spec Kit’s specify phase is deliberately non-technical. Mixing stack choices into the product spec locks you in early and makes the agent argue with itself.

**Human gates between phases.** The agent writes the artifacts; you accept them. Do not auto-advance specify → plan → implement in one unattended burst on a risky change.

**Small, testable tasks.** Isolated tasks are how the agent stays honest. They are TDD for the agent’s work queue.

**Context hygiene.** Implementation in a clean chat with `@spec` / `@plan` / `@tasks` attached beats one 200-message thread. OpenSpec explicitly recommends clearing context before implement. Skills should load references on demand, not dump everything into the prompt.

**Put organizational law where the agent can use it.** Security, compliance, design-system, and “we use X not Y” belong in constitution/rules/plan — not a wiki the model never sees.

**Use the right model for the phase.** Planning and specification benefit from stronger reasoning. Mechanical, well-specified tasks can use a faster/cheaper model.

**Verify against the spec, not the story.** Tests, browser flows, and `/review` should trace back to acceptance criteria. “Looks good” is not a gate.

**When implementation diverges, repair the spec.** Cursor: revert, refine the plan, rebuild. Spec Kit: the spec remains the living artifact. OpenSpec: update any artifact; then apply again.

**Start simple, then encode mistakes.** Do not pre-write 40 rules. Add a rule or skill when you see a repeated failure. Check them into git.

**Cloud agents need the same contract.** Project skills, `AGENTS.md`, workspace plans, and hooks travel with the repo. Personal `~/.cursor` skills and hooks do not, unless you sync skills for Cloud Agents.

**Do not confuse checkpoints with Git.** Checkpoints undo agent file changes in a session. Specs, plans, and finished work belong in version control.

---

## 8. Minimal templates

Copy these into `docs/specs/<change>/`. They match [`docs/specs/_template/`](docs/specs/_template/) (`## Trace` on the plan; each task row has `(verify: …) (spec: …)`).

### spec.md

```markdown
# <Change title>

## Problem
Who hurts, and what happens today?

## Goals
- …

## Non-goals
- …

## Users and journeys
1. …

## Acceptance criteria
- [ ] …
- [ ] Failure case: …

## Open questions
- …
```

### plan.md

```markdown
# Plan: <Change title>

## Constraints
Stack, compatibility, performance, security.

## Approach
1. …

## Files likely touched
- `path` — why

## Risks
- …

## Trace
| Acceptance / REQ | Tasks |
| --- | --- |
| | T1 |

## Out of scope
- …
```

### tasks.md

```markdown
# Tasks

- [ ] T1: … (verify: …) (spec: …)
- [ ] T2: … (verify: …) (spec: …)
```

---

## Support

Broken skill or install: open a [GitHub Issue](https://github.com/Crav1on/crav1-spec-kit/issues). Include your Cursor version, install path (drop-in, team marketplace, or local plugin), the command you ran, and what you expected versus what happened. Details: [SUPPORT.md](SUPPORT.md).

---

## Further reading

- [Kit repository](https://github.com/Crav1on/crav1-spec-kit) · [First 15 minutes](docs/first-run.md) · [Installing and using the kit](docs/install.md) · [Guild routing](docs/guild-routing.md) · [Plugin quick start](plugins/crav1/README.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [MIT License](LICENSE)
- [Cursor documentation hub](https://cursor.com/docs/)
- [Plugins](https://cursor.com/docs/plugins) · [Plugins reference](https://cursor.com/docs/reference/plugins)
- [Plan Mode](https://cursor.com/docs/agent/plan-mode) · [Introducing Plan Mode](https://cursor.com/blog/plan-mode)
- [Agent overview](https://cursor.com/docs/agent/overview)
- [Rules and AGENTS.md](https://cursor.com/docs/rules)
- [Agent Skills](https://cursor.com/docs/skills)
- [Cloud Agents](https://cursor.com/docs/cloud-agent)
- [Hooks](https://cursor.com/docs/hooks)
- [Subagents](https://cursor.com/docs/subagents)
- [GitHub Spec Kit](https://github.com/github/spec-kit/) · [GitHub Blog on SDD](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [OpenSpec](https://github.com/Fission-AI/OpenSpec)
- [MADR (Markdown Architectural Decision Records)](https://adr.github.io/madr/)
- [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/)
