# Spec-driven agentic development with Cursor

A concise playbook for using Cursor as an agentic coding environment where **specs, not chat history, are the source of truth**.

This is a process guide, not an application. Use it as a checklist when you start a repo, then install the kit into that project.

**Before you install:** [docs/install.md](docs/install.md) (drop-in copy, Cursor plugin, or local plugin). **After a plugin install:** [plugins/crav1/README.md](plugins/crav1/README.md).

Primary sources: [Cursor docs](https://cursor.com/docs/), [Plan Mode](https://cursor.com/docs/agent/plan-mode), [Agent](https://cursor.com/docs/agent/overview), [Rules](https://cursor.com/docs/context/rules), [Skills](https://cursor.com/docs/context/skills), [Cloud Agents](https://cursor.com/docs/cloud-agent), [GitHub Spec Kit](https://github.com/github/spec-kit/), and [OpenSpec](https://github.com/Fission-AI/OpenSpec).

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

If you have no spec, no stack, and only a spark, do **not** start in Plan Mode and do not paste a “senior architect” persona. Interview first, write `spec.md`, tighten it, *then* plan. Full walkthrough: [From one sentence to a spec](docs/from-nothing.md).

**First prompt** (Agent chat, strong reasoning model):

```text
/crav1-spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Do not write code. Ask questions first.
```

Then: answer ≤7 questions → agent writes `docs/specs/<slug>/spec.md` → `/crav1-tighten-spec` walks **each** finding → `/crav1-resolve-questions` walks leftover Open questions (keep open or answer) → optional `crav1-spec-reviewer` → **`/crav1-plan-from-spec`** → `/crav1-implement-task` per `T#` → `/crav1-verify-spec` → `/crav1-fix-from-verify` (omit Gap) for inner-loop remaining: failed → unverified → `G#`.

Runnable pieces in this repo:

| Piece | When | How |
| --- | --- | --- |
| Skill `/crav1-spark-to-spec` | You have 1–2 sentences | Slash command; can pin as Custom Mode |
| Skill `/crav1-architecture-reviewer` | Spec + diagrams/ADRs exist | Slash command; runs the reviewer subagent |
| Skill `/crav1-tighten-spec` | Spec exists, still mushy | Slash command; one issue at a time, then edit |
| Skill `/crav1-resolve-questions` | Open questions remain after tightening | Slash command; keep-open or answer, one `Q#` at a time |
| Skill `/crav1-plan-from-spec` | Spec is accepted; want plan + tasks, no code | Slash command; writes `plan.md` and `tasks.md` |
| Skill `/crav1-implement-task` | `tasks.md` exists; build one slice | Slash command; one `T#`, then its verify |
| Skill `/crav1-verify-spec` | Want proof against acceptance | Slash command; TL;DR then `verify.md` details |
| Skill `/crav1-fix-from-verify` | After verify-spec, inner-loop gaps | Slash command; omit Gap to walk failed → unverified → G# |
| Skill `/crav1-fix-live` | Live/inner-loop gap | Alias of `/crav1-fix-from-verify` |
| Skill `/crav1-draft-commit-message` | About to commit (GitKraken paste fields) | Slash command; style.md or git log, once or onward; no commit unless they ask |
| Skill `/crav1-finalize-commit` | Finish a message: edit, GitKraken copy, or git commit | Same draft; wording first, then next message copy / edit / rewrite / commit; no push |
| Skill `/crav1-ideas-to-spec` | Pile of ideas + technical hunches | Slash command; pick an export format |
| Skill `/crav1-export-spec` | Spec exists, want another format | Slash command |
| Subagent `crav1-spec-reviewer` | Independent product/spec critique | Agent delegates, or ask “review this spec” |
| Subagent `crav1-architecture-reviewer` | Diagrams, ADRs, hunches vs decisions | Agent delegates |

## 3. From a pile of ideas (not a spark, not a spec)

When you already have several ideas and maybe stack opinions, use **`/crav1-ideas-to-spec`**, not `/crav1-spark-to-spec`. Full walkthrough: [From a pile of ideas to a spec](docs/from-ideas.md).

**First prompt:**

```text
/crav1-ideas-to-spec

Format: EARS
# BDD | OpenSpec | YAML | JSON | BMAD  (comma-separate for more than one)

Bundle:
- <ideas>
- Technical thoughts: <hunches, constraints, preferred shape>

Treat hunches as proposed, not decided.
Do not write code. Capture first, then architecture questions.
```

Flow: cluster intent vs hunches → product questions if needed → **architecture interview** (≤7 questions, 2–3 options) → write `spec.md` + `diagrams.md` + ADRs + `export/<format>` → optional `crav1-architecture-reviewer` → Plan Mode.

Canonical spec stays Markdown. EARS / BDD / OpenSpec / YAML / JSON / BMAD are exports. Mermaid for context and sequences; ASCII for trees and CLIs. ADRs only when there were real alternatives (MADR-shaped template).

## 4. The working loop (once a spec exists)

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

## 5. How to set it up

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

Install into another repo: [docs/install.md](docs/install.md). Drop-in copy is `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc`. Plugin install uses `plugins/crav1/` plus `.cursor-plugin/marketplace.json`. Also copy `docs/specs/_template/` if you want the human starter folder.

When you change a template, update `docs/specs/_template/` **and** every `assets/` / `agent-assets/` copy on **both** the drop-in tree and `plugins/crav1/` (`scripts/sync-crav1-plugin.sh`). Rule: `.cursor/rules/crav1-self-contained-skills.mdc`.

This repo already ships:

- `/crav1-spark-to-spec` — one-liner → questions → `spec.md`
- `/crav1-ideas-to-spec` — idea pile + technical hunches → spec, diagrams, ADRs, chosen export
- `/crav1-architecture-reviewer` — run the crav1-architecture-reviewer subagent; numbered issues at the end
- `/crav1-tighten-spec` — one issue at a time, with explained resolutions and impact; patch only that issue after you choose
- `/crav1-resolve-questions` — one Open question at a time; keep it open or answer with impact; patch only that `Q#`
- `/crav1-export-spec` — re-project `spec.md` into EARS, BDD, OpenSpec, YAML, JSON, or BMAD
- `/crav1-plan-from-spec` — file-level `plan.md` and testable `tasks.md`; refuses to code
- `/crav1-implement-task` — one `tasks.md` row, then run its verify step
- `/crav1-verify-spec` — TL;DR of implemented vs not, then acceptance details in `verify.md`
- `/crav1-fix-from-verify` — after verify-spec, walk inner-loop gaps (failed → unverified → `G#`); omit Gap for the next; writes `fix-log.md`
- `/crav1-fix-live` — alias when that gap is a live/inner-loop path
- `/crav1-draft-commit-message` — paste-ready GitKraken Summary/Description; `style.md` or live git log, once or onward (deletable rule); does not commit unless they ask
- `/crav1-finalize-commit` — same draft, then copy for GitKraken, edit/rewrite the text, or `git commit` when they accept it (no push)
- subagent `crav1-spec-reviewer` — independent product/spec critique
- subagent `crav1-architecture-reviewer` — hunches vs decisions, diagrams, ADRs

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

## 6. Best practices (Cursor + Spec Kit + OpenSpec)

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

## 7. Minimal templates

Copy these into `docs/specs/<change>/`.

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

## Out of scope
- …
```

### tasks.md

```markdown
# Tasks

- [ ] T1: … (verify: …)
- [ ] T2: … (verify: …)
```

---

## Further reading

- [Installing and using the kit](docs/install.md) · [Plugin quick start](plugins/crav1/README.md)
- [Cursor documentation hub](https://cursor.com/docs/)
- [Plugins](https://cursor.com/docs/plugins) · [Plugins reference](https://cursor.com/docs/reference/plugins)
- [Plan Mode](https://cursor.com/docs/agent/plan-mode) · [Introducing Plan Mode](https://cursor.com/blog/plan-mode)
- [Agent overview](https://cursor.com/docs/agent/overview)
- [Rules and AGENTS.md](https://cursor.com/docs/context/rules)
- [Agent Skills](https://cursor.com/docs/context/skills)
- [Cloud Agents](https://cursor.com/docs/cloud-agent)
- [Hooks](https://cursor.com/docs/hooks)
- [Subagents](https://cursor.com/docs/subagents)
- [GitHub Spec Kit](https://github.com/github/spec-kit/) · [GitHub Blog on SDD](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [OpenSpec](https://github.com/Fission-AI/OpenSpec)
- [MADR (Markdown Architectural Decision Records)](https://adr.github.io/madr/)
- [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/)
