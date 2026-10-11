# The method

This page is the method behind the kit: how the pieces fit together, the seven ways in, the working loop once a spec exists, how to set it up, and the best practices. The commands themselves, with what each reads and writes, are in the [skills reference](../reference/skills.md). Where the files go on each host is [install](../install.md). Every other page is listed in the [docs index](../README.md).

## How the pieces fit together

An agent is three things working at once: **instructions**, **tools**, and a **model**. Spec-driven development (SDD) is how you keep those three pointed at the same outcome when the work is larger than one prompt.

### The agent stack

| Layer | What it is | Role in SDD |
| --- | --- | --- |
| **Model** | The LLM you pick for the turn | Stronger reasoning models for specify/plan; faster models for isolated tasks |
| **Tools** | Search, read, edit, terminal, browser, web, questions | The agent can research, implement, and **verify** instead of only generating text |
| **Instructions** | Project instructions, skills, and the spec in context | Persistent “how we work here”; specs are the current “what to build” |
| **Plan files** | `plan.md` and `tasks.md` in the spec folder | Reviewable how, in git, one task at a time |
| **Git** | Permanent history | Keep specs and code versioned together |

Frontier models do better on long-horizon work when they have a reviewable spec with file paths, constraints, and tasks. That plan lives in git as `plan.md` and `tasks.md`. Each host also has a plan UI. That UI is not those files. See [docs/install.md](../install.md).

### Spec-driven development in one sentence

Treat the specification as an **executable contract**: the agent generates, tests, and validates against it. Chat is steering. The spec is the source of truth. When the result is wrong, you fix the spec and rebuild, not endlessly patch code in follow-ups.

GitHub’s Spec Kit frames this as four gated phases:

1. **Specify** — user journeys, success criteria, non-goals (the *what* and *why*)
2. **Plan** — stack, architecture, constraints, interfaces (the *how*)
3. **Tasks** — small, independently testable units of work
4. **Implement** — the agent codes one task at a time; you verify

OpenSpec’s OPSX flow is the same idea without rigid waterfall gates: **explore → propose → apply → verify → sync/archive**, and you may update any artifact as understanding changes. That is a better fit for brownfield work.

### How a change moves

```
You (intent)
    │
    ├─ Project instructions     → standing project law (host file: install doc)
    ├─ Skills                   → playbooks (specify, implement, review)
    └─ Specs in the repo        → this change’s contract
            │
            ▼
     /crav1-plan-from-spec  ──►  docs/specs/<slug>/plan.md + tasks.md
            │
            ▼
     One task               ──►  edits, tests, checks
            │
            ├─ Git             → keep spec + code together
            └─ Verify          → prove the slice against the spec
```

**Instructions vs skills vs specs** (do not collapse these):

- **Project instructions**: always-on constraints (stack, style, “never touch generated files”). Short, stable, rarely change. Where that file lives is in [docs/install.md](../install.md).
- **Skills**: on-demand playbooks (“how we specify a feature”, “how we review a PR”). Load when relevant.
- **Specs / plans**: per-change artifacts. They expire or get archived when the change ships.

If you dump a whole product spec into always-on instructions, you waste context and the agent treats yesterday’s feature as today’s law.

### What you should *not* spec-drive

Quick, well-understood edits (rename, copy tweak, one-file bug with a clear stack trace) belong in a normal agent turn. A bug that is already shipping, or that comes in from outside, is `/crav1-fix-bug`. That command names the lane and does not start it. The spec loop pays off when:

- There are multiple valid designs
- Many files or systems are involved
- Requirements are still fuzzy
- You need an architectural checkpoint before code exists

## Starting points

Each starting point below has its own walkthrough with the full steps. The table of all seven starter options is on the [README](../../README.md#the-seven-starter-options).

### From one sentence to a spec

If you have only a spark (one or two sentences), do **not** start in the host plan UI and do not paste a “senior architect” persona. Interview first, write `spec.md`, tighten it, *then* plan — **greenfield or a feature on an existing app**. The layout always includes `docs/system/`. This command seeds a thin landscape when that folder is missing, including `glossary.md`, then the spec, then one index row. An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Full walkthrough: [From one sentence to a spec](../from-nothing.md).

**First prompt** (Cursor: Agent chat. Claude Code: a session in the product repo. Strong reasoning model). Greenfield:

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

Then: answer ≤7 questions (and the branch prompt) → agent seeds a thin `docs/system/` when that folder is missing, writes `docs/specs/<slug>/spec.md`, then adds one landscape index row → `/crav1-tighten-spec` walks **each** finding → `/crav1-resolve-questions` walks leftover Open questions (keep open or answer) → optional `crav1-spec-reviewer-agent` → **`/crav1-plan-from-spec`** → `/crav1-review-plan` then `/crav1-tighten-plan` for plan `P#`s → `/crav1-implement-task` per `T#` or `/crav1-complete-task` / `/crav1-complete-tasks` (one spec) or `/crav1-complete-features` (several specs, serial) → `/crav1-verify-spec` → `/crav1-fix-from-verify` (omit Gap) for inner-loop remaining: failed → unverified → `G#`.

### From a pile of ideas (not a spark, not a spec)

When you already have several ideas and maybe stack opinions, use **`/crav1-ideas-to-spec`**, not `/crav1-spark-to-spec`. The layout always includes `docs/system/`. This command seeds a thin landscape when that folder is missing, including `glossary.md`, then the spec artifacts, then one index row. An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Full walkthrough: [From a pile of ideas to a spec](../from-ideas.md).

**First prompt:**

```text
/crav1-ideas-to-spec

<one blob: ideas, UX notes, stack hunches, constraints. No required structure.
Name an export format in the same text if you already know it, or wait for the ask.>

Treat hunches as proposed, not decided.
Do not write code. Capture first, then architecture questions.
```

Flow: cluster intent vs hunches → product questions if needed → **architecture interview** (≤7 questions, 2–3 options) → thin `docs/system/` when that folder is missing, then `spec.md` + `diagrams.md` + ADRs + `export/<format>`, then one landscape index row → optional `/crav1-architecture-reviewer` → `/crav1-plan-from-spec`.

Canonical spec stays Markdown. EARS / BDD / OpenSpec / YAML / JSON / BMAD are exports. Mermaid for context and sequences; ASCII for trees and CLIs. ADRs only when there were real alternatives (MADR-shaped template). If the pile is several v0 features or several repos, `/crav1-ideas-to-spec` stops and you run `/crav1-intake-to-specs` instead.

### From intake files (several features or repos)

When you have **1–N files** (notes, diagrams, screenshots, optional code as context) that may be a whole system, use **`/crav1-intake-to-specs`**. Full walkthrough: [From intake files to specs](../from-intake.md).

**First prompt:**

```text
/crav1-intake-to-specs
@notes/overview.md
@sketches/flow.png
@legacy-api/

Treat hunches as proposed, not decided.
Do not write code. Map first.
```

Default if you only `@` a codebase: new system, that code is **context** (not extract-as-is). The parent confirms a map (slugs, repos, bulk assumptions, mushy vs ready), writes `docs/system/`, then one isolated worker per v0 slug. Then it **prompts** `/crav1-finalize-commit` (does not commit itself). Later features use spark or ideas. When `docs/system/` already exists, `@` it, use a new slug, and add an index row. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. When the folder is missing, those commands seed a thin landscape, including `glossary.md`. Do not re-run intake.

### From existing repos and a dump

When one or more repos already make up a system, and a dump (notes, tickets, old docs, diagrams, screenshots) is what to match against that code, use **`/crav1-match-to-specs`**. The repos are evidence of what exists. The dump is not a brief for a new product. Full walkthrough: [From existing repos and a dump to specs](../from-match.md).

This does not replace `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, or `/crav1-ideas-to-spec`.

**First prompt:**

```text
/crav1-match-to-specs
@repo-a/
@repo-b/
@notes/old-spec.md

The repos are what exists. The dump is what to match. Do not write code.
```

The command asks where the spec files go (one repo already in front of it, or a new clean repo), then stops on a map: slice, repo, and done / partial / not in the code. After that map is confirmed, one branch carries the dump, then `docs/system/` and one spec per slice. It prompts `/crav1-finalize-commit` and does not plan a slice that is not in the code.

### From a later dump onto existing specs

When specs already exist under `docs/specs/` and a new dump (notes, tickets, old docs, diagrams, screenshots) has to be sorted onto them, use **`/crav1-match-dump-to-specs`**. Full walkthrough: [From a later dump onto existing specs](../from-match-dump.md).

Match creates the folders from repos plus a dump. Add takes information already aimed at one named spec. This command does not ask for a slug first. It reads the existing spec folders. One dump may be a lot about one slug, or it may cover many. Size is not a limit. It does not plan.

**First prompt:**

```text
/crav1-match-dump-to-specs
@notes/later-dump.md
@tickets/

The specs already exist. Sort this dump onto them. Do not write code. Do not plan.
```

The command shows four piles (belongs to this spec, already in that spec, note, does not fit) and waits. After that sort is confirmed, it quotes the new bits into the matching specs. A confirmed note is written under `docs/notes/` and is not tied to a spec yet. Anything that fits none of them stays listed. It does not create a slug. It points at `/crav1-finalize-commit` when those edits should be in git, and at `/crav1-plan-from-spec` only for a slice you choose.

### From a code change that already landed

When specs already exist under `docs/specs/` and a code change already landed without a spec, plan, or build, use **`/crav1-code-into-specs`**. Full walkthrough: [From a code change onto existing specs](../from-code.md).

Match creates the folders from repos plus a dump. Match-dump sorts a later dump onto those specs. Add takes information already aimed at one named spec. This command starts from the change. No dump is required. It does not ask for a slug first. It reads the existing spec folders. It does not watch the repo. It runs only when someone points it at a change. It does not plan.

**First prompt:**

```text
/crav1-code-into-specs

The specs already exist. Sort this change onto them. Do not write code. Do not plan.
```

If the message does not name a commit, a commit range, or the branch diff, the command looks at git and asks with options only: recent commits, or the diff of the current branch against the default branch. It does not ask for a typed hash.

The command shows three piles (belongs to this spec, already described there, fits none) and waits. After that sort is confirmed, it quotes what the change does into the matching specs, the same way add writes new information. Anything that fits none of them stays listed. It does not create a slug. It points at `/crav1-finalize-commit` only when those spec edits should be committed.

## The working loop (once a spec exists)

Use this on any non-trivial change.

The later skills that work on a spec that already exists (add, repos-to-spec, environment-read, pipeline-environments, explain, whats-known-about, keep-current, security-review, review-pr, suggest-tests-for-code, meeting-to-specs, exploratory-test, fix-bug) are described in full on their pages in the [skills reference](../reference/skills.md).

### A. Specify (read-heavy)

Describe the user problem, not the stack. Force:

- Who it is for
- Happy path and failure path
- Explicit **non-goals**
- Acceptance checks a stranger could mark yes or no. Name unit, system, or browser only when that kind is already obvious. Otherwise the plan names the kind. Do not write the test list in the spec.

Have the agent research the repo (search, read, existing tests). Answer clarifying questions. Do not skip them; answer quality here dominates output quality later.

Write or update `docs/specs/<change>/spec.md` (or Spec Kit / OpenSpec’s layout). **You** accept this artifact before planning.

### B. Plan (`plan.md` and `tasks.md`)

Run `/crav1-plan-from-spec`. The skill writes `docs/specs/<change>/plan.md` and `tasks.md` with file paths, constraints, and tasks. When the spec is partial or `## In the code` names paths, it reads that repo and branch and lists each built piece before any task. Finish the gap, add a verify test, or leave it are the choices. A piece that already matches v0 is marked already there. Each task verify note names the kind of check and the checks that must pass, before any code. The plan also says whether this repo has a linter or checker for the code those tasks will touch. When it has one, the plan names it and Build is expected to leave that check green. When it does not, the plan says so and stops before Build. You decide to add the linter or to go on without one. The plan skill does not install one. Specify stays a yes/no acceptance line and does not name the linter. Edit those files. They are the plan that teammates and later chats see. `/crav1-verify-spec` is the gate that says those named checks passed.

The host plan UI is not a substitute. See [docs/install.md](../install.md).

Treat the plan as a design review: wrong files, missing constraints, and oversized tasks are cheaper to fix here than after a 40-file diff.

### C. Task-slice

Every task should be implementable **and testable** in isolation. “Add authentication” is not a task. “POST `/register` rejects invalid email (verify: unit — empty email is rejected; unit — malformed email is rejected)” is.

If a task cannot be verified, it is still part of the spec, not ready to implement.

### D. Implement

Build from `plan.md` and `tasks.md`. Prefer a **fresh chat** so implementation context is not polluted by all the exploration. `/crav1-implement-task` is one `T#`. `/crav1-complete-task` is that `T#` in an isolated worker.

If the agent diverges, revert, tighten the plan, and rebuild instead of endless patch prompts.

Verify the same way a human would: tests, linters, and for UI work, the browser tools.

### E. Review and close the loop

Use a review pass or the kit’s review subagent. Diff against the spec, not against “does it look plausible.” If behavior drifted, update the spec first, then the code. Archive or mark the change done so the next agent does not treat an in-flight proposal as current law.

## How to set it up

The loop above is the method. Optional template families are in step 5. Where the kit files go on each host is [docs/install.md](../install.md).

### Step 1 — Standing instructions

Keep project instructions short: language, test command, architecture boundaries, “do not” list. Where that file lives on Cursor or Claude Code is [docs/install.md](../install.md).

Keep each instruction under a few hundred lines, split by concern, **point at example files** instead of pasting style guides, and add one only after the agent repeats a mistake.

### Step 2 — Spec layout in git

The layout always includes `docs/system/`. Spark and ideas seed a thin landscape when that folder is missing (greenfield or an existing app), including `glossary.md`, and leave an existing landscape in place, adding one index row, a missing `glossary.md`, and the picture update. Intake writes `docs/system/` and does not skip it, including `glossary.md` in that same pass. Match writes `docs/system/` from the repos and the confirmed match when that folder is missing, and only fills gaps the match needs when it already exists, including a missing `glossary.md`. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there.

The full layout, with what each folder holds and which command writes it, is [Data layout](data-layout.md).

`/crav1-plan-from-spec` writes `plan.md` and `tasks.md` into that folder so teammates see them.

### Step 3 — Skills

Kit skills are the playbooks. Type `/crav1`. Where the files go, and how a slash command shows up on each host, is [docs/install.md](../install.md). Keep `SKILL.md` short; put templates in that skill’s `assets/` (and `references/` for recipes).

Also copy `docs/specs/_template/` and `docs/system/_template/` if you want visible starter folders.

When you change a template in this kit repo, update `docs/specs/_template/` **and** every `assets/` / `agent-assets/` copy, then run `scripts/sync-crav1-plugin.sh` so the Cursor plugin mirror and the generated `.claude/` tree match. The maintainer rule stays in this kit repo (do not dump it with `crav1-*`). See [CONTRIBUTING.md](../../CONTRIBUTING.md).

Every skill and subagent this kit ships, with what it reads, what it writes, and what it leaves alone, is in the [skills reference](../reference/skills.md).

Invoke with `/skill-name` (for example `/crav1-implement-task` while you burn down `T#`s).

### Step 4 — Verification as part of the environment

An agent that cannot run tests will guess. Document the exact test, lint, and dev commands in the project instructions. A real environment (deps, secrets, startup) is what lets the agent build, test, and check the UI.

### Step 5 — Optional template families

**GitHub Spec Kit** is a heavier, gated specify → plan → tasks → implement loop. **OpenSpec** is lighter and iterative: propose → apply → verify → archive. You do not need either one to use this kit. This kit’s plan is `plan.md` and `tasks.md` from `/crav1-plan-from-spec`.

### Step 6 — Day-to-day

1. Open a chat in the product repo. On Cursor that is Agent chat. On Claude Code, open a session in that repo.
2. Pick one starter option from the [seven starter options](../../README.md#the-seven-starter-options). Asking for startup options names only those seven and does not run one. `/crav1-repos-to-spec` still runs only when the user names the repos. It does not start Specify, Plan, or Build. `/crav1-environment-read` still runs only when the user names the host, such as Azure. Naming production, prod, or live stops. It reads every non-prod environment in one pass. A prod-only resource is shape and connections only, after one yes. SQL metadata and storage structure are optional after that, and only when the user says yes. Look-inside never opens production. It does not start Specify, Plan, or Build. `/crav1-fix-bug` still runs only when the user names a real bug. It is not a skill that runs because a repo is new. Later skills, once specs already exist, include a later dump (`/crav1-match-dump-to-specs`), a landed code change (`/crav1-code-into-specs`), new information on one spec (`/crav1-add-to-spec`), tests for code that already exists (`/crav1-suggest-tests-for-code`, one repo or one area), and `/crav1-pipeline-environments` when the user names Azure DevOps, the org, and the project. Those are not starter options. Do not start in the host plan UI.
3. Accept `spec.md`. Then `/crav1-plan-from-spec` and accept `plan.md` / `tasks.md`.
4. `/crav1-implement-task` or `/crav1-complete-task` for one `T#`. Watch diffs. Run the task’s verify step.
5. If wrong: fix the spec or the plan, then rebuild.
6. `/crav1-verify-spec` when you want the acceptance matrix. Inner-loop gaps go to `/crav1-fix-from-verify`.

## Best practices

**Make intent unambiguous.** Models complete patterns; they do not read your mind. “Add photo sharing” hides thousands of decisions. Specs surface them before code exists.

**Separate what from how.** Spec Kit’s specify phase is deliberately non-technical. Mixing stack choices into the product spec locks you in early and makes the agent argue with itself.

**Human gates between phases.** The agent writes the artifacts; you accept them. Do not auto-advance specify → plan → implement in one unattended burst on a risky change.

**Small, testable tasks.** Isolated tasks are how the agent stays honest. They are TDD for the agent’s work queue.

**Context hygiene.** Implementation in a clean chat with `@spec` / `@plan` / `@tasks` attached beats one 200-message thread. OpenSpec explicitly recommends clearing context before implement. Skills should load references on demand, not dump everything into the prompt.

**Put organizational law where the agent can use it.** Security, compliance, design-system, and “we use X not Y” belong in constitution/rules/plan — not a wiki the model never sees.

**Use the right model for the phase.** Planning and specification benefit from stronger reasoning. Mechanical, well-specified tasks can use a faster/cheaper model.

**Verify against the spec, not the story.** Tests and browser flows should trace back to acceptance criteria. “Looks good” is not a gate.

**When implementation diverges, repair the spec.** Revert, refine the plan, rebuild. The spec remains the living artifact.

**Start simple, then encode mistakes.** Do not pre-write 40 rules. Add a rule or skill when you see a repeated failure. Check them into git.

**A project install travels with the repo.** Project skills, project instructions, and `plan.md` are in git. A user-scope install does not land in the repo. See [docs/install.md](../install.md).

**Do not confuse Cursor checkpoints with Git.** Cursor checkpoints undo agent file changes in a session. Specs, plans, and finished work belong in version control.

## Minimal templates

Copy these into `docs/specs/<change>/`. They match [`docs/specs/_template/`](../specs/_template/) (`## Linter` and `## Trace` on the plan; each task row has `(verify: <kind> — <named check>) (spec: …)`).

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

## Linter
- …

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

- [ ] T1: … (verify: <kind> — <named check>) (spec: …)
- [ ] T2: … (verify: <kind> — <named check>) (spec: …)
```
