# CRAV1 Spec Kit (crav1)

**CRAV1 Spec Kit** (`crav1`) runs on **Cursor** and **Claude Code**. The slash commands are the same (`/crav1`, then `/crav1-…`). The install is not. Where the files go is [docs/install.md](docs/install.md).

It is a kit for spec-driven development: skills and agents that take a spark, a pile of ideas, intake files, a match of existing repos to a dump, a later dump onto specs that already exist, a code change that already landed onto those specs, or named repos into one architecture spec, through spec, plan, implement, verify, and a draft commit message. Specs, not chat history, are the source of truth. A short project instruction ships with the install.

On Cursor, install plugin `crav1` from this GitHub repo (team marketplace import or a local plugin). There is no public Cursor Marketplace listing. On Claude Code, there is no plugin and no marketplace: copy `.claude/` into a repository you own, or into `~/.claude` for a client project. Cloning this kit does not install it into another product.

Repo: [crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit). After install on either host, type `/crav1`.

This is a process guide, not an application. Use it as a checklist when you start a repo, then install the kit into that project.

**First 15 minutes:** [docs/first-run.md](docs/first-run.md). **Install:** [docs/install.md](docs/install.md). **After a Cursor plugin install:** [plugins/crav1/README.md](plugins/crav1/README.md). License: [MIT](LICENSE).

## First 15 minutes

Pick an install path, open the product repo, then `/crav1` and one starter option. A spark continues tighten → plan → one task. The short path is [docs/first-run.md](docs/first-run.md). The sections below are the full playbook.

When you ask for startup options, these seven are the only ways in. That ask names the list. It does not run a skill. It does not move work into a lane. Each starter still follows the rules it already has. Every other skill is a later skill.

| Starter | When |
| --- | --- |
| `/crav1-spark-to-spec` | One or two sentences |
| `/crav1-ideas-to-spec` | A pile of ideas and technical hunches |
| `/crav1-intake-to-specs` | Mixed files, or more than one v0 feature |
| `/crav1-match-to-specs` | Existing repos plus a dump to match |
| `/crav1-repos-to-spec` | You name the repos. It runs only then |
| `/crav1-environment-read` | You name the host and a dev or test environment. It runs only then |
| `/crav1-fix-bug` | You name a real bug that already exists. It runs only then |

Primary sources for the method: [GitHub Spec Kit](https://github.com/github/spec-kit/) and [OpenSpec](https://github.com/Fission-AI/OpenSpec). Host file locations and plan-UI notes are in [docs/install.md](docs/install.md).

---

## 1. How the pieces fit together

An agent is three things working at once: **instructions**, **tools**, and a **model**. Spec-driven development (SDD) is how you keep those three pointed at the same outcome when the work is larger than one prompt.

### The agent stack

| Layer | What it is | Role in SDD |
| --- | --- | --- |
| **Model** | The LLM you pick for the turn | Stronger reasoning models for specify/plan; faster models for isolated tasks |
| **Tools** | Search, read, edit, terminal, browser, web, questions | The agent can research, implement, and **verify** instead of only generating text |
| **Instructions** | Project instructions, skills, and the spec in context | Persistent “how we work here”; specs are the current “what to build” |
| **Plan files** | `plan.md` and `tasks.md` in the spec folder | Reviewable how, in git, one task at a time |
| **Git** | Permanent history | Keep specs and code versioned together |

Frontier models do better on long-horizon work when they have a reviewable spec with file paths, constraints, and tasks. That plan lives in git as `plan.md` and `tasks.md`. Each host also has a plan UI. That UI is not those files. See [docs/install.md](docs/install.md).

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

- **Project instructions**: always-on constraints (stack, style, “never touch generated files”). Short, stable, rarely change. Where that file lives is in [docs/install.md](docs/install.md).
- **Skills**: on-demand playbooks (“how we specify a feature”, “how we review a PR”). Load when relevant.
- **Specs / plans**: per-change artifacts. They expire or get archived when the change ships.

If you dump a whole product spec into always-on instructions, you waste context and the agent treats yesterday’s feature as today’s law.

### What you should *not* spec-drive

Quick, well-understood edits (rename, copy tweak, one-file bug with a clear stack trace) belong in a normal agent turn. A bug that is already shipping, or that comes in from outside, is `/crav1-fix-bug`. That command names the lane and does not start it. The spec loop pays off when:

- There are multiple valid designs
- Many files or systems are involved
- Requirements are still fuzzy
- You need an architectural checkpoint before code exists

---

## 2. From one sentence to a spec

If you have only a spark (one or two sentences), do **not** start in the host plan UI and do not paste a “senior architect” persona. Interview first, write `spec.md`, tighten it, *then* plan — **greenfield or a feature on an existing app**. The layout always includes `docs/system/`. This command seeds a thin landscape when that folder is missing, including `glossary.md`, then the spec, then one index row. An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Full walkthrough: [From one sentence to a spec](docs/from-nothing.md).

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

Runnable pieces in this repo:

| Piece | When | How |
| --- | --- | --- |
| Skill `/crav1-spark-to-spec` | You have 1–2 sentences (empty repo or a feature on an existing app) | Starter option. Slash command; greenfield vs brownfield from context. Seeds a thin `docs/system/` when missing, then the spec, then one index row. On Azure Repos, one optional work-item id after a new spec folder |
| Skill `/crav1-feature-branch` | Brownfield: get off the default branch | Prompt: `feat/<slug>` (spec+build) or `spec/<slug>` then `feat/<slug>` for build; no push, no PR |
| Skill `/crav1-architecture-reviewer` | Spec + diagrams/ADRs exist | Slash command; runs the reviewer subagent |
| Skill `/crav1-repos-to-spec` | The user names one or more repos and wants the architecture the code shows | Starter option. Runs only when the repos are named. Asking for startup options names it and does not run it. Slash command; `docs/architecture/spec.md` when that file is missing. Guesses that stay left out go to `docs/architecture/left-out.md`. Existing `docs/system/` notes stay. A later re-read adds only what is new and removes a left-out line when the code shows it. Confirmation is one question per section. A guess stays out until that section accepts it. A link is written only when the code shows it. Does not design the next feature or start Specify, Plan, or Build |
| Skill `/crav1-environment-read` | The user names a host and an environment (Azure dev, Google Cloud test, AWS dev) | Starter option. Runs only when the host and a dev or test environment are named. Asking for startup options names it and does not run it. Slash command; reads that environment only. Azure, AWS, and Google Cloud readers. Any other host stops with no reader. Never production. Does not write the system, architecture, feature, or left-out files. After each confirmed section, the owner adds only what is new. Does not start Specify, Plan, or Build |
| Skill `/crav1-explain` | System notes already exist under `docs/system/` | Slash command; short TLDR, then one level deeper when asked. Yes, no, or not written down. Does not write a file |
| Skill `/crav1-keep-current` | Something was added and the picture should catch up | Slash command; adds what is new to the short description, the diagram, and how the parts connect. Does not rewrite what is already there. Does not plan or commit |
| Skill `/crav1-security-review` | Architecture already exists (`docs/system/` or a spec that describes the design) | Slash command; same command for the whole system, one spec, or the change in front of you. Writes kept findings. Does not plan or commit |
| Skill `/crav1-tighten-spec` | Spec exists, still mushy | Slash command; one issue at a time (option to get a suggestion); then edit |
| Skill `/crav1-resolve-questions` | Open questions remain after tightening | Slash command; keep-open or answer, one `Q#` at a time |
| Skill `/crav1-plan-from-spec` | Spec is accepted; want plan + tasks, no code | Slash command; writes `plan.md` and `tasks.md`; each verify note names the checks. Names a linter when the repo has one, and stops before Build when it does not |
| Skill `/crav1-review-plan` | Plan exists; want a critique | Slash command; numbered `P#`s for tighten-plan |
| Skill `/crav1-tighten-plan` | After review-plan, or mushy tasks | Slash command; one `P#` at a time; patches plan/tasks only |
| Skill `/crav1-implement-task` | `tasks.md` exists; build one slice | Slash command; one `T#`, then its verify |
| Skill `/crav1-complete-task` | One `T#` implement → done in an isolated worker | Persist commit style as a rule; auto-commit; parent relays fix/ready |
| Skill `/crav1-complete-tasks` | Several `T#`s to done | Orchestrates one complete-task worker per id; `T1-T3` or all unchecked |
| Skill `/crav1-complete-features` | Several **specs** to done, serial | One `feat/<slug>` from default at a time, then that slug’s T# loop; not parallel |
| Skill `/crav1-verify-spec` | Want proof against acceptance | Slash command; TL;DR then `verify.md` details |
| Skill `/crav1-fix-from-verify` | After verify-spec, inner-loop gaps | Slash command; omit Gap to walk failed → unverified → G# |
| Skill `/crav1-fix-live` | Live/inner-loop gap | Alias of `/crav1-fix-from-verify` |
| Skill `/crav1-draft-commit-message` | About to commit (GitKraken paste fields) | Slash command; CRAV1 style or git log, once or onward; no commit unless they ask. Optional `work-item.md` mention is the last description line |
| Skill `/crav1-finalize-commit` | Finish a message: git commit, GitKraken copy, or edit | Style first if needed, then draft, then **commit first**, then copy / edit / rewrite / stop; no push. Keeps a trailing work-item mention |
| Skill `/crav1-open-pr` | Commits exist on `feat/<slug>` or `spec/<slug>` and you want a pull request | Push only after an explicit yes; one PR against the default branch; no merge, no commit. Adds a Work item section when `work-item.md` exists. On Windows, Azure DevOps description is `--description "@<file>"` (UTF-8, no BOM). May name `/crav1-review-pr` and does not run it. Later merge is `/crav1-merge-pr` |
| Skill `/crav1-review-pr` | This turn names an open pull request and you want to know if it can ship | Slash command; reads the diff. Spec, plan, `verify.md`, the body, and a required green linter. Does not edit, test, vote, comment, or merge |
| Skill `/crav1-fix-bug` | This turn names a real bug (verify failure on work already shipping, or a defect from outside) | Starter option. Runs only when a real bug is named. Asking for startup options names it and does not run it. Slash command; says where it was seen, names the bug, what it breaks, and the lane. Does not start that lane, edit, or open a pull request. Not a new-repo start |
| Skill `/crav1-exploratory-test` | A build of a slice already exists | Later skill. Slash command; uses the slice once, then again with randomness, and writes bugs. Stops when that second pass has matched the first, or sooner when the user says stop. Does not start Specify, Plan, or Build. Not a starter option |
| Skill `/crav1-suggest-tests-for-code` | The user points at code that already exists, one repo or one area | Later skill. Slash command; suggests tests for what that code can break. Keep, leave, or dismiss, one at a time. A kept suggestion goes on the existing spec. Does not write the tests or start Specify, Plan, or Build. Not a starter option |
| Skill `/crav1-merge-pr` | This turn explicitly asks to merge a named pull request | Merge commit only (`gh pr merge --merge` or Azure `noFastForward`). Parents counted with `git rev-list` after the completed re-read. No squash, rebase, or policy bypass. Does not run `/crav1-review-pr`. Stops when a required host check is red |
| Skill `/crav1-ideas-to-spec` | Pile of ideas + technical hunches | Starter option. Slash command; pick an export format. Seeds a thin `docs/system/` when missing, then the spec, then one index row. On Azure Repos, one optional work-item id after a new spec folder |
| Skill `/crav1-intake-to-specs` | 1–N files; maybe several features/repos | Starter option. Slash command; landscape + one spec per v0 slug. On Azure Repos, one optional work-item question listing the new slugs |
| Skill `/crav1-match-to-specs` | Existing repos plus a dump to match | Starter option. Slash command; where the specs go, then one spec per slice (done, partial, or not in the code). Does not plan or commit |
| Skill `/crav1-match-dump-to-specs` | A later dump, specs already exist | Slash command; sorts the dump onto those specs (belongs, already there, or does not fit), then quotes the new bits. Does not create a slug. Does not plan or commit |
| Skill `/crav1-code-into-specs` | A code change already landed, specs already exist | Slash command; sorts that change onto those specs (belongs, already described there, or fits none), then quotes what the change does. No dump. Does not create a slug. Does not plan or commit |
| Skill `/crav1-add-to-spec` | New information for one existing spec | Slash command; adds it to that spec, then reports impact on the landscape or other specs before editing them. Does not plan or commit |
| Skill `/crav1-export-spec` | Spec exists, want another format | Slash command |
| Subagent `crav1-spec-reviewer-agent` | Independent product/spec critique | Agent delegates, or ask “review this spec” |
| Subagent `crav1-architecture-reviewer-agent` | Diagrams, ADRs, hunches vs decisions | Agent delegates |
| Subagent `crav1-plan-reviewer-agent` | Plan/tasks vs spec | Agent delegates; `/crav1-review-plan` |

## 3. From a pile of ideas (not a spark, not a spec)

When you already have several ideas and maybe stack opinions, use **`/crav1-ideas-to-spec`**, not `/crav1-spark-to-spec`. The layout always includes `docs/system/`. This command seeds a thin landscape when that folder is missing, including `glossary.md`, then the spec artifacts, then one index row. An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Full walkthrough: [From a pile of ideas to a spec](docs/from-ideas.md).

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

Default if you only `@` a codebase: new system, that code is **context** (not extract-as-is). The parent confirms a map (slugs, repos, bulk assumptions, mushy vs ready), writes `docs/system/`, then one isolated worker per v0 slug. Then it **prompts** `/crav1-finalize-commit` (does not commit itself). Later features use spark or ideas. When `docs/system/` already exists, `@` it, use a new slug, and add an index row. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. When the folder is missing, those commands seed a thin landscape, including `glossary.md`. Do not re-run intake.

## 5. From existing repos and a dump

When one or more repos already make up a system, and a dump (notes, tickets, old docs, diagrams, screenshots) is what to match against that code, use **`/crav1-match-to-specs`**. The repos are evidence of what exists. The dump is not a brief for a new product. Full walkthrough: [From existing repos and a dump to specs](docs/from-match.md).

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

## 6. From a later dump onto existing specs

When specs already exist under `docs/specs/` and a new dump (notes, tickets, old docs, diagrams, screenshots) has to be sorted onto them, use **`/crav1-match-dump-to-specs`**. Full walkthrough: [From a later dump onto existing specs](docs/from-match-dump.md).

Match creates the folders from repos plus a dump. Add takes information already aimed at one named spec. This command does not ask for a slug first. It reads the existing spec folders. One dump may be a lot about one slug, or it may cover many. Size is not a limit. It does not plan.

**First prompt:**

```text
/crav1-match-dump-to-specs
@notes/later-dump.md
@tickets/

The specs already exist. Sort this dump onto them. Do not write code. Do not plan.
```

The command shows three piles (belongs to this spec, already in that spec, does not fit) and waits. After that sort is confirmed, it quotes the new bits into the matching specs. Anything that fits none of them stays listed. It does not create a slug. It points at `/crav1-finalize-commit` when those edits should be in git, and at `/crav1-plan-from-spec` only for a slice you choose.

## 7. From a code change that already landed

When specs already exist under `docs/specs/` and a code change already landed without a spec, plan, or build, use **`/crav1-code-into-specs`**. Full walkthrough: [From a code change onto existing specs](docs/from-code.md).

Match creates the folders from repos plus a dump. Match-dump sorts a later dump onto those specs. Add takes information already aimed at one named spec. This command starts from the change. No dump is required. It does not ask for a slug first. It reads the existing spec folders. It does not watch the repo. It runs only when someone points it at a change. It does not plan.

**First prompt:**

```text
/crav1-code-into-specs

The specs already exist. Sort this change onto them. Do not write code. Do not plan.
```

If the message does not name a commit, a commit range, or the branch diff, the command looks at git and asks with options only: recent commits, or the diff of the current branch against the default branch. It does not ask for a typed hash.

The command shows three piles (belongs to this spec, already described there, fits none) and waits. After that sort is confirmed, it quotes what the change does into the matching specs, the same way add writes new information. Anything that fits none of them stays listed. It does not create a slug. It points at `/crav1-finalize-commit` only when those spec edits should be committed.

## 8. The working loop (once a spec exists)

Use this on any non-trivial change.

New information aimed at one spec that already exists is **`/crav1-add-to-spec`**. Full walkthrough: [From new information to an existing spec](docs/from-add.md). `/crav1-tighten-spec` stays for mushy wording. Match, intake, spark, and ideas create the folders. This command does not plan.

When the user names one or more repos and wants the architecture the code shows, **`/crav1-repos-to-spec`** reads those repos and writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) when that file is missing. It writes the system notes under `docs/system/` when those notes are missing. When a real system note is already there, it leaves those notes and writes the missing architecture spec and `docs/architecture/left-out.md`. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there, and removes a left-out line when the code shows it. Full walkthrough: [From named repos to an architecture spec](docs/from-repos.md). A fact the code shows is confirmed. Before any file is written, the confirmation is one question per section. A guess stays out of the spec until that section accepts it. A guess that stays left out is written to `docs/architecture/left-out.md`. A link between repos is written only when the code shows it. If none is found, the command says so. It does not invent links. It is cross-cutting. It is not a lane and not a mode of Specify. It does not design the next feature, write application code, or start Specify, Plan, or Build. It is not `/crav1-code-into-specs`.

When the user names a host and an environment, **`/crav1-environment-read`** reads that environment. Full walkthrough: [From a named environment](docs/from-environment.md). Examples: Azure dev, Google Cloud test, AWS dev. It does not guess the host. It never reads production. This build has readers for Azure, AWS, and Google Cloud. Any other host stops with no reader. It does not read Azure DevOps, GitHub, or CI. The user names the environment, not the subscription, the account, or the project. A resource whose name, group, or tag says that environment is listed. Production is skipped and listed as skipped. A resource with no environment mark stops and is not read. The skill only reads. After a section is confirmed, the skill that already owns the file adds only what is new. A fact is seen in that environment. A link is added only when the environment shows the connection. It is cross-cutting. It is not a lane. It does not start Specify, Plan, or Build.

When system notes already exist, **`/crav1-explain`** reads `docs/system/` and answers with a short TLDR. Full walkthrough: [From the system notes](docs/from-explain.md). Longer goes one level deeper from the same notes. It is cross-cutting. It is not its own lane. It does not guess, write a second document, teach, or start Specify, Plan, or Build.

When something was added, **`/crav1-keep-current`** updates the short description, the diagram, and how the parts connect. Full walkthrough: [Keep the picture current](docs/from-keep-current.md). It adds what is new and does not rewrite what is already there. It does not design the change and does not build it. It can run on its own. Spark, ideas, intake, match, and the siblings that already append a glossary row also run this update. They do not rewrite existing glossary rows.

When architecture already exists, **`/crav1-security-review`** asks whether the thing in front of it is secure. Full walkthrough: [From a security review](docs/from-security.md). The same command covers the whole system, one existing spec, or the change in front of you. It is not a mode of `/crav1-architecture-reviewer`. Architecture review critiques design hunches. This command writes kept findings and stops. Spark, plan, and verify do not run it.

When an open pull request is named, **`/crav1-review-pr`** reads the diff and says whether it can ship. Full walkthrough: [From a pull request review](docs/from-review-pr.md). It is cross-cutting. It is not a lane and not a bot. It does not edit, run the tests, vote, comment, or merge. `/crav1-open-pr` may name it and does not run it. `/crav1-merge-pr` does not run it. Spark, specify, and verify do not run it.

When the user points at code that already exists, one repo or one area, **`/crav1-suggest-tests-for-code`** reads that code and suggests tests for what that code can actually break. Full walkthrough: [From code that already exists, suggest tests](docs/from-suggest-tests.md). A function gets a few checks. A page gets a browser check. A boundary gets an integration check. It does not dump every test type. Every suggestion stays listed. Nothing is dropped to keep the list short. The user takes them one at a time: keep, leave, or dismiss. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. It does not write the tests, change the code, or start Specify, Plan, or Build. It is cross-cutting. It may run from any lane. It does not move work into a lane. It is a later skill. It is not a starter option. Asking for startup options names only the seven and does not run this command. The seven starter options stay unchanged.

When a build of a slice already exists, **`/crav1-exploratory-test`** uses that slice in two passes and writes down bugs. Full walkthrough: [From a built slice, exploratory test](docs/from-exploratory-test.md). Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness and follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. The user does not set a clock. It writes `docs/specs/<slug>/explore.md`. It does not write the checks the plan already named. It is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn. It is a later skill. It is not a starter option. Asking for startup options names only the seven and does not run this command.

When a real bug is named, **`/crav1-fix-bug`** says where it was seen, names the bug, points at the spec or the shipped behavior it breaks, and names the lane. Full walkthrough: [From a bug that already exists](docs/from-fix-bug.md). A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside. It is cross-cutting. It is not a lane and not a stretch of verify. It does not start that lane, edit code, open a pull request, or create an Azure Boards work item. If no bug is named, it stops. It does not go hunting. When you ask for startup options, it is one of the seven starter options. That ask names the list and does not run it. It is an intake for a bug that already exists. It still runs only when you name a real bug. It is not a skill that runs because a repo is new, and it is not started automatically. Spark, specify, plan, and verify do not run it.

### A. Specify (read-heavy)

Describe the user problem, not the stack. Force:

- Who it is for
- Happy path and failure path
- Explicit **non-goals**
- Acceptance checks a stranger could mark yes or no. Name unit, system, or browser only when that kind is already obvious. Otherwise the plan names the kind. Do not write the test list in the spec.

Have the agent research the repo (search, read, existing tests). Answer clarifying questions. Do not skip them; answer quality here dominates output quality later.

Write or update `docs/specs/<change>/spec.md` (or Spec Kit / OpenSpec’s layout). **You** accept this artifact before planning.

### B. Plan (`plan.md` and `tasks.md`)

Run `/crav1-plan-from-spec`. The skill writes `docs/specs/<change>/plan.md` and `tasks.md` with file paths, constraints, and tasks. Each task verify note names the kind of check and the checks that must pass, before any code. The plan also says whether this repo has a linter or checker for the code those tasks will touch. When it has one, the plan names it and Build is expected to leave that check green. When it does not, the plan says so and stops before Build. You decide to add the linter or to go on without one. The plan skill does not install one. Specify stays a yes/no acceptance line and does not name the linter. Edit those files. They are the plan that teammates and later chats see. `/crav1-verify-spec` is the gate that says those named checks passed.

The host plan UI is not a substitute. See [docs/install.md](docs/install.md).

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

---

## 9. How to set it up

The loop above is the method. Optional template families are in step 5. Where the kit files go on each host is [docs/install.md](docs/install.md).

### Step 1 — Standing instructions

Keep project instructions short: language, test command, architecture boundaries, “do not” list. Where that file lives on Cursor or Claude Code is [docs/install.md](docs/install.md).

Keep each instruction under a few hundred lines, split by concern, **point at example files** instead of pasting style guides, and add one only after the agent repeats a mistake.

### Step 2 — Spec layout in git

The layout always includes `docs/system/`. Spark and ideas seed a thin landscape when that folder is missing (greenfield or an existing app), including `glossary.md`, and leave an existing landscape in place, adding one index row, a missing `glossary.md`, and the picture update. Intake writes `docs/system/` and does not skip it, including `glossary.md` in that same pass. Match writes `docs/system/` from the repos and the confirmed match when that folder is missing, and only fills gaps the match needs when it already exists, including a missing `glossary.md`. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there.

A layout that works without extra CLIs:

```text
docs/system/
  _template/
  landscape.md       # short description, how the parts connect, v0 vs later, bulk A#s, feature index
  repos.md           # named repos (proposed until a URL exists)
  diagrams.md        # context diagram; /crav1-keep-current adds what is new
  glossary.md        # words the source already uses; not a feature spec
  security.md        # kept risks after /crav1-security-review (system pass); not seeded by spark
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
```

`/crav1-plan-from-spec` writes `plan.md` and `tasks.md` into that folder so teammates see them.

### Step 3 — Skills

Kit skills are the playbooks. Type `/crav1`. Where the files go, and how a slash command shows up on each host, is [docs/install.md](docs/install.md). Keep `SKILL.md` short; put templates in that skill’s `assets/` (and `references/` for recipes).

Also copy `docs/specs/_template/` and `docs/system/_template/` if you want visible starter folders.

When you change a template in this kit repo, update `docs/specs/_template/` **and** every `assets/` / `agent-assets/` copy, then run `scripts/sync-crav1-plugin.sh` so the Cursor plugin mirror and the generated `.claude/` tree match. The maintainer rule stays in this kit repo (do not dump it with `crav1-*`). See [CONTRIBUTING.md](CONTRIBUTING.md).

This repo already ships:

- `/crav1-spark-to-spec` — one-liner → questions → thin `docs/system/` when missing, including `glossary.md`, then `spec.md`, then one index row (greenfield, brownfield feature, or later feature on an existing landscape; new slug unless they extend). An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. On Azure Repos, offers once to write `work-item.md`
- `/crav1-feature-branch` — prompt for `feat/<slug>` or specify-only `spec/<slug>`; no silent checkout, no push, no PR
- `/crav1-ideas-to-spec` — idea pile + technical hunches → thin `docs/system/` when missing, including `glossary.md`, then spec, diagrams, ADRs, chosen export, then one index row. An existing landscape is left in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. On Azure Repos, offers once to write `work-item.md`
- `/crav1-intake-to-specs` — mixed intake → `docs/system/` (including `glossary.md`) + one spec per v0 feature (isolated slice workers). A missing `glossary.md` is filled when the folder already exists. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. On Azure Repos, one optional work-item question for the new slugs
- `/crav1-match-to-specs` — existing repos plus a dump → where the spec files go, then `docs/system/` (including `glossary.md`) and one spec per confirmed slice (done, partial, or not in the code). Fills a missing `glossary.md` when the folder already exists. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Not intake, spark, or ideas. Does not plan, implement, or commit
- `/crav1-match-dump-to-specs` — a later dump, specs already exist → sort onto those specs (belongs, already there, or does not fit), then quote the new bits. Does not ask for a slug first. Does not create a slug. Does not seed `docs/system/`. Fills a missing `glossary.md` only when that folder already exists. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Does not plan, implement, or commit
- `/crav1-code-into-specs` — a code change that already landed, specs already exist → sort onto those specs (belongs, already described there, or fits none), then quote what the change does. No dump. Does not ask for a slug first. Does not create a slug. Does not watch the repo. Does not seed `docs/system/`. Fills a missing `glossary.md` only when that folder already exists. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. Does not plan, implement, or commit
- `/crav1-add-to-spec` — new information for one existing spec → quote it into that `spec.md`, then report whether the landscape or another spec has to change. Does not rewrite those other files unless asked. Does not create a glossary. A new glossary row can be one listed edit and is not written unless apply is chosen. A meaning the new information does not state is `to be researched`. Existing rows are not rewritten. Does not plan, implement, or commit
- `/crav1-architecture-reviewer` — run the crav1-architecture-reviewer-agent subagent; numbered issues at the end. Optional next, not run from this command: `/crav1-security-review`
- `/crav1-repos-to-spec` — cross-cutting. The user names one or more repos. Reads those repos and writes `docs/architecture/spec.md` when that file is missing, and the `docs/system/` notes `/crav1-explain` reads when those notes are missing. When a real system note is already there, leaves those notes and writes the missing architecture spec and `docs/architecture/left-out.md`. A later re-read adds only what is new and does not rewrite those lines, and removes a left-out line when the code shows it. Before any file is written, one question per section. A fact the code shows is confirmed. A guess stays out until that section accepts it. A guess that stays left out is written to `docs/architecture/left-out.md`. A link is written only when the code shows it. If none is found, says so and does not invent a link. Does not design the next feature, write application code, or start Specify, Plan, or Build. Not `/crav1-code-into-specs`
- `/crav1-environment-read` — cross-cutting. The user names the host and the environment. Reads only what that environment has. Azure, AWS, and Google Cloud readers. Any other host stops with no reader. Never production. Does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. After a confirmed section, the owner adds only what is new. A fact is seen in that environment. A link only when the environment shows the connection. Does not start Specify, Plan, or Build
- `/crav1-explain` — cross-cutting. Reads `docs/system/`. First answer is a short TLDR. Longer goes one level deeper from the same notes. The user can point it at one part, or ask whether the system can do something (yes and where, no, or not written down). Does not guess, write a second document, teach, or start Specify, Plan, or Build. When the picture is older than the specs, says so and names `/crav1-keep-current`
- `/crav1-keep-current` — cross-cutting. Adds what is new to the short description, the diagram, and how the parts connect. Does not rewrite what is already there. Does not design the change or build it. Can run on its own. Spark, ideas, intake, match, match-dump, and code-into-specs run this same update and still do not rewrite existing glossary rows
- `/crav1-security-review` — cross-cutting. After architecture exists, ask whether the thing in front of you is secure. Same command for the whole system (`docs/system/security.md`), one spec, or the change in front of you (a Security section on that spec). One confirm, then kept findings only. Does not invent an architecture. Does not plan, implement, or commit. Spark, plan, and verify do not run it
- `/crav1-tighten-spec` — one issue at a time, with explained resolutions (plus get a suggestion) and impact; patch only that issue after you choose
- `/crav1-resolve-questions` — one Open question at a time; keep it open or answer with impact; patch only that `Q#`
- `/crav1-export-spec` — re-project `spec.md` into EARS, BDD, OpenSpec, YAML, JSON, or BMAD
- `/crav1-plan-from-spec` — file-level `plan.md` and `tasks.md`; each verify note names the checks before code; names a linter or checker when the repo has one, and stops before Build when it does not; refuses to code and does not install a linter
- `/crav1-review-plan` — critique `plan.md` / `tasks.md` against the spec; numbered `P#`s
- `/crav1-tighten-plan` — one plan issue at a time; patches plan/tasks only (spec findings go to tighten-spec)
- `/crav1-implement-task` — one `tasks.md` row, then run its verify step
- `/crav1-complete-task` — isolated worker for one `T#`: implement → commit → verify → optional fix; persist commit style as a rule
- `/crav1-complete-tasks` — orchestrates one worker per `T#` (`T1-T3` or all unchecked); stops the batch when a worker needs you
- `/crav1-complete-features` — serial board of ready slugs: `feat/<slug>` from default, then that spec’s complete-tasks loop; no parallel, no push, no PR
- `/crav1-verify-spec` — TL;DR of implemented vs not, then acceptance details in `verify.md`
- `/crav1-fix-from-verify` — after verify-spec, walk inner-loop gaps (failed → unverified → `G#`); omit Gap for the next; writes `fix-log.md`
- `/crav1-fix-live` — alias when that gap is a live/inner-loop path
- `/crav1-draft-commit-message` — paste-ready GitKraken Summary/Description; CRAV1 style or live git log, once or onward (deletable rule); does not commit unless they ask. Optional Azure Boards mention from `docs/specs/<slug>/work-item.md` is the last description line
- `/crav1-finalize-commit` — same draft, then **commit first**, then copy for GitKraken, edit/rewrite, or stop (no push). Keeps that mention through the HEAD check and the attribution strip
- `/crav1-open-pr` — push the change branch only after an explicit yes, then open one pull request (no merge, no commit). Body is What / why, Spec links, Verify, and a Work item section when `work-item.md` exists. On Windows, a multi-line Azure DevOps description is passed as `--description "@<file>"` (UTF-8 without BOM). May name `/crav1-review-pr` and does not run it. Next explicit ask to merge is `/crav1-merge-pr`
- `/crav1-review-pr` — cross-cutting. Reads one named open pull request. Spec, plan, `verify.md`, the body, and a required green linter must hold before it says ship. Names the lane for a finding and does not start it. Does not edit, test, vote, comment, install a linter, or merge. Spark, specify, and verify do not run it
- `/crav1-fix-bug` — cross-cutting. Names one real bug the user already named (a verify failure on work that is already shipping, or a defect from outside). Says where it was seen, what it breaks, and the lane. Does not start that lane, edit code, open a pull request, or create an Azure Boards work item. Stops when no bug is named. Not a lane and not a stretch of verify. Starter option. Asking for startup options names it and does not run it. It still runs only when the user names a real bug. Not a new-repo start. Not started automatically. Spark, specify, plan, and verify do not run it
- `/crav1-exploratory-test` — cross-cutting later skill. After a build of a slice already exists, uses the slice once, then again with randomness, and writes bugs to `docs/specs/<slug>/explore.md`. The second pass lasts about as long as the first, then stops (`matched the first pass`), or sooner when the user says stop (`the user said stop`). The user does not set a clock. Does not write the checks the plan already named. Does not start Specify, Plan, or Build. A bug is not sent to `/crav1-fix-bug` unless the user says so in that turn. Not a starter option. Asking for startup options names only the seven and does not run this command
- `/crav1-suggest-tests-for-code` — cross-cutting later skill. The user points at code that already exists, one repo or one area, not the whole system. Suggests tests for what that code can break. A function gets a few checks. A page gets a browser check. A boundary gets an integration check. Does not dump every test type. Every suggestion stays listed. Keep, leave, or dismiss, one at a time. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. Does not write the tests, change the code, or start Specify, Plan, or Build. Not a starter option. Asking for startup options names only the seven and does not run this command. The seven starter options stay unchanged
- `/crav1-merge-pr` — merge one named pull request only when that turn asks; always a merge commit; no squash, rebase, or policy bypass. After the completed re-read, two parents are confirmed with `git rev-list` (commits API if git cannot see the commit). Does not run `/crav1-review-pr`. Stops when a required host check is red
- subagent `crav1-spec-reviewer-agent` — independent product/spec critique
- subagent `crav1-architecture-reviewer-agent` — hunches vs decisions, diagrams, ADRs
- subagent `crav1-plan-reviewer-agent` — worker for `/crav1-review-plan` (`plan.md` / `tasks.md` vs spec)
- subagent `crav1-complete-task-agent` — worker for `/crav1-complete-task` / `/crav1-complete-tasks` / `/crav1-complete-features` (one `T#`)
- subagent `crav1-intake-slice-agent` — worker for `/crav1-intake-to-specs` (one feature slug)

Invoke with `/skill-name` (for example `/crav1-implement-task` while you burn down `T#`s).

### Step 4 — Verification as part of the environment

An agent that cannot run tests will guess. Document the exact test, lint, and dev commands in the project instructions. A real environment (deps, secrets, startup) is what lets the agent build, test, and check the UI.

### Step 5 — Optional template families

**GitHub Spec Kit** is a heavier, gated specify → plan → tasks → implement loop. **OpenSpec** is lighter and iterative: propose → apply → verify → archive. You do not need either one to use this kit. This kit’s plan is `plan.md` and `tasks.md` from `/crav1-plan-from-spec`.

### Step 6 — Day-to-day

1. Open a chat in the product repo. On Cursor that is Agent chat. On Claude Code, open a session in that repo.
2. Pick one starter option from the table in First 15 minutes. Asking for startup options names only those seven and does not run one. `/crav1-repos-to-spec` still runs only when the user names the repos. It does not start Specify, Plan, or Build. `/crav1-environment-read` still runs only when the user names the host and a dev or test environment, such as Azure dev. It only reads. It does not start Specify, Plan, or Build. `/crav1-fix-bug` still runs only when the user names a real bug. It is not a skill that runs because a repo is new. Later skills, once specs already exist, include a later dump (`/crav1-match-dump-to-specs`), a landed code change (`/crav1-code-into-specs`), new information on one spec (`/crav1-add-to-spec`), and tests for code that already exists (`/crav1-suggest-tests-for-code`, one repo or one area). Those are not starter options. Do not start in the host plan UI.
3. Accept `spec.md`. Then `/crav1-plan-from-spec` and accept `plan.md` / `tasks.md`.
4. `/crav1-implement-task` or `/crav1-complete-task` for one `T#`. Watch diffs. Run the task’s verify step.
5. If wrong: fix the spec or the plan, then rebuild.
6. `/crav1-verify-spec` when you want the acceptance matrix. Inner-loop gaps go to `/crav1-fix-from-verify`.

---

## 10. Best practices

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

**A project install travels with the repo.** Project skills, project instructions, and `plan.md` are in git. A user-scope install does not land in the repo. See [docs/install.md](docs/install.md).

**Do not confuse Cursor checkpoints with Git.** Cursor checkpoints undo agent file changes in a session. Specs, plans, and finished work belong in version control.

---

## 11. Minimal templates

Copy these into `docs/specs/<change>/`. They match [`docs/specs/_template/`](docs/specs/_template/) (`## Trace` on the plan; each task row has `(verify: <kind> — <named check>) (spec: …)`).

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

- [ ] T1: … (verify: <kind> — <named check>) (spec: …)
- [ ] T2: … (verify: <kind> — <named check>) (spec: …)
```

---

## Support

Broken skill or install: open a [GitHub Issue](https://github.com/Crav1on/crav1-spec-kit/issues). Include the host and version, the install path, the command you ran, and what you expected versus what happened. Details: [SUPPORT.md](SUPPORT.md).

---

## Further reading

- [Kit repository](https://github.com/Crav1on/crav1-spec-kit) · [First 15 minutes](docs/first-run.md) · [Installing and using the kit](docs/install.md) · [Guild routing](docs/guild-routing.md) · [Cursor plugin quick start](plugins/crav1/README.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [MIT License](LICENSE)
- [GitHub Spec Kit](https://github.com/github/spec-kit/) · [GitHub Blog on SDD](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [OpenSpec](https://github.com/Fission-AI/OpenSpec)
- [MADR (Markdown Architectural Decision Records)](https://adr.github.io/madr/)
- [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/)
