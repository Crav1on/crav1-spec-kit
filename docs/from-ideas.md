# From a pile of ideas to a spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when you have **more than a spark**: several ideas, maybe UX notes, maybe “I think we should use X”, but it is not a spec you would hand to an agent to build. This command is a starter option. The seven are in [first-run.md](first-run.md). Asking for startup options names that list and does not run this command.

You still do **not** start by coding. You add an architecture interview and you write diagrams + ADRs. The canonical file remains `spec.md`. Formats are exports. The layout always includes `docs/system/`. This command seeds a thin landscape when that folder is missing (greenfield or an existing app), then writes the spec artifacts, then adds one index row. It fills that landscape from the repo already in front of the agent. When the landscape already exists, this command adds one index row (a repo or ADR row only when the feature needs a new repo) and adds what is new to the picture. Lines already there stay as they are. A missing `glossary.md` is written. An existing glossary gets only new rows for words that are not already listed. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. That same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there.

Spark-only (greenfield or one feature on an existing app)? Use [from-nothing](from-nothing.md) and `/crav1-spark-to-spec` instead. Mixed files or several features/repos? Use [from-intake](from-intake.md) and `/crav1-intake-to-specs`. If this pile is clearly more than one v0 slice or more than one repo, `/crav1-ideas-to-spec` will stop and send you there.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

Paste **one blob**. No required headings, bullets, or `Format:` / `Bundle:` labels. Include the same kinds of information you used to put in sections: who it is for, the ideas, any UX notes, stack or shape hunches, constraints. The skill clusters intent vs hunches for you.

```text
/crav1-ideas-to-spec

<paste the pile in your own words. Mix product ideas and technical thoughts.
You can mention an export format in the same text (EARS, BDD, OpenSpec, YAML,
JSON, BMAD) or skip it and the skill will ask.>

Treat hunches as proposed, not decided.
Do not write code. Capture first, then architecture questions.
```

That slash command *is* the prompt.

On a git repo with commits, the skill **prompts** for `feat/<slug>` (spec+build) or `spec/<slug>` (specify-only) before it writes files. `/crav1-feature-branch` is the same prompt on its own. No push, no PR.

Structured labels still work if you like them; they are not required.

## The extra steps (vs spark)


| Phase              | You                                    | Agent                                                                                     |
| ------------------ | -------------------------------------- | ----------------------------------------------------------------------------------------- |
| Capture            | Paste one unstructured blob            | Clusters intent vs hunches vs undecided, v0 vs later, ≤5 product questions, format choice |
| Architecture       | Answer / “use assumptions”             | ≤7 technical questions + 2–3 options at one abstraction level                             |
| Write              | Pick options, correct A-numbers        | Thin `docs/system/` when missing, including `glossary.md`, then `spec.md`, `diagrams.md`, ADRs, `export/<format>`, then one landscape index row. A missing `glossary.md` is written when the folder already exists. New rows are appended. Existing rows are not rewritten. The picture update adds what is new to the short description, the diagram, and how the parts connect |
| Critique           | Optional                               | `/crav1-architecture-reviewer` then `/crav1-tighten-spec` (one issue at a time)            |
| Questions          | Leftover Open questions                | `/crav1-resolve-questions` — keep open or answer, one `Q#` at a time                      |
| Export again       | “also want JSON”                       | `/crav1-export-spec` — does not change behavior                                           |
| Stop               | v0 is demoable and ADRs match diagrams | New chat, `/crav1-plan-from-spec`, with `spec.md`, `diagrams.md`, and `adr/` attached |


Good replies during Architecture:

- “Source of truth is local files. Sync is later.”
- “Option 2, because I am solo and must ship a demo.”
- “Auth is a non-goal. That hunch is dropped.”

Bad replies:

- “All options, we’ll see in the code.”
- “Add a platform layer in case we need it.”



## What gets written

```text
docs/system/              # always; seeded when the folder is missing
  landscape.md            # one index row points at the new spec
  repos.md
  diagrams.md
  glossary.md             # append words the source already uses; do not edit existing rows
  adr/                    # only a cross-cutting choice that already had alternatives
docs/specs/<slug>/
  spec.md                 # source of truth
  diagrams.md             # mermaid preferred; ascii when better
  adr/0001-<decision>.md  # only real choices (MADR-style)
  export/ears.md          # or bdd.md, spec.yaml, spec.json, bmad.md
  export/openspec/        # if you chose OpenSpec
```

`docs/system/` uses the same landscape, repos, diagram, glossary, and ADR templates intake writes. `repos.md` includes a `Synced at` column. When this run reads a whole repo, it sets that repo's cell and touches only those repos. When this run reads only one slice, it does not touch the column. It writes or updates `Synced at: <repo> <branch>@<short sha>, <date>` in that slice's `spec.md`. When that folder already exists, this command does not rewrite lines that are already there, except that cell on a whole-repo read. A missing `glossary.md` is written. New rows are appended. A meaning the source does not state is `to be researched`. The picture update adds what is new to the short description, the diagram, and how the parts connect.

ADRs use the MADR-shaped template in skill `crav1-ideas-to-spec` `assets/adr.md` (Cursor drop-in: `.cursor/skills/crav1/crav1-ideas-to-spec/assets/adr.md`; Claude Code drop-in: `.claude/skills/crav1-ideas-to-spec/assets/adr.md`; same as `docs/specs/_template/adr.md`). Status starts as `proposed`. Hunches with no alternative belong under Constraints, not as ADRs.

Diagrams: context + v0 sequence are required. State/ER only if the idea needs them. Mermaid for graphs and sequences; ascii for trees, CLIs, and simple pipelines.

## Formats (what you are choosing)


| Id           | You get                              | Use when                                               |
| ------------ | ------------------------------------ | ------------------------------------------------------ |
| **EARS**     | WHEN/IF/WHERE/WHILE … SHALL          | Testable requirements without a full Gherkin suite     |
| **BDD**      | Feature / Given-When-Then            | You want scenarios as the acceptance list              |
| **OpenSpec** | proposal, delta specs, design, tasks | Change-shaped work, especially brownfield later        |
| **YAML**     | `export/spec.yaml`                   | Tools or agents that prefer structured files           |
| **JSON**     | `export/spec.json`                   | Same as YAML, machine-first                            |
| **BMAD**     | Behavior, Model, API, Data           | You want domain + interface + data in one readable doc |


`spec.md` is always written. Choosing EARS does not delete the narrative spec.

## Critique command

```text
/crav1-architecture-reviewer
@docs/specs/<slug>/
Do not edit files.
```

Then `/crav1-tighten-spec` to walk the numbered issues (each issue has resolutions plus **get a suggestion**). When the slice is partial or `## In the code` names paths, it reads the committed code on the repo and branch the spec names before wording issues. A spec with no code behind it skips that read. Then `/crav1-resolve-questions` for leftover Open questions.

## After accept

```text
/crav1-plan-from-spec
@docs/specs/<slug>/spec.md
@docs/specs/<slug>/diagrams.md
@docs/specs/<slug>/adr

Stay inside v0. Do not reopen rejected options unless an ADR is still proposed.
Do not code.
```

`/crav1-plan-from-spec` writes `plan.md` and `tasks.md` in the spec folder. When the spec is partial or `## In the code` names paths, it reads that repo and branch and lists each built piece before any task. Finish the gap, add a verify test, or leave it are the choices. A piece that already matches v0 is marked already there. The host plan UI is not those files ([install.md](install.md)). The plan names a linter or checker when the repo has one, and stops before Build when it does not. You decide to add the linter or to go on without one. The plan skill does not install one. Specify does not name the linter.

Optional critique of the plan (does not change `spec.md`):

```text
/crav1-review-plan
@docs/specs/<slug>/
```

Then `/crav1-tighten-plan` walks **plan** `P#`s one by one. Findings tagged **spec** go to `/crav1-tighten-spec` or `/crav1-resolve-questions`.

If this work is on **`spec/<slug>`**, stop after plan: `/crav1-finalize-commit`, open a PR when you want the spec on the default branch. After it is merged, `/crav1-feature-branch` → `feat/<slug>`, then implement. Do not implement on `spec/<slug>`.

Then, in a **new** chat:

```text
/crav1-implement-task
@docs/specs/<slug>/tasks.md
```

When you want the full acceptance matrix:

```text
/crav1-verify-spec
@docs/specs/<slug>/spec.md
```

If the TL;DR still lists failed, unverified, or wiring `G#` rows (not “not implemented”):

```text
/crav1-fix-from-verify
@docs/specs/<slug>/verify.md
@docs/specs/<slug>/spec.md

Do not change spec.md.
```

Omit `Gap` to take the next inner-loop item (order: verify failed → claimed done/unverified → `G#`). Repeat until that queue is empty. Unimplemented `T#`s stay on `/crav1-implement-task`.

To take **one** `T#` implement-to-done in an **isolated worker chat** (style persisted as a rule):

```text
/crav1-complete-task T2
```

Several (orchestrator stays here; one worker per `T#`):

```text
/crav1-complete-tasks T1-T3
```

Several **specs** (serial; each `feat/<slug>` from the default branch, then that spec’s T#s). One spec still uses complete-tasks:

```text
/crav1-complete-features auth-login billing
```

When you are ready to commit by itself (after a `T#` or a live fix):

```text
/crav1-draft-commit-message
```

Paste the **Summary** and **Description** blocks into GitKraken. The skill does not run `git commit` unless you also ask it to.

To change the wording first, then copy **or** create the git commit:

```text
/crav1-finalize-commit
```

That command drafts the same way: style first if needed, then Summary/Description, **then** `copy` / `edit` / `rewrite` / `commit`. It does not push.

First time (no persist rule yet) it asks:

- **CRAV1 style, this commit only**
- **CRAV1 style, this commit and onward** — writes a host persist rule
- **Git log, this commit only** — match this repo’s recent messages
- **Git log, this commit and onward** — writes the other host persist rule

Onward choices are mutually exclusive (writing one removes the other). To get the prompt again: delete that rule file. Which file that is depends on the host ([install.md](install.md)).

Inner-loop example (same skill; `/crav1-fix-live` also works):

```text
/crav1-fix-from-verify
Gap: T# claimed done, unverified — POST /register never reached SQL
Live command: POST <url>/register
Do not change spec.md.
```

## Optional Azure Boards mention

To link commits and the pull request to an Azure Boards work item, `docs/specs/<slug>/work-item.md` holds one id per line. A line may name the milestone or slice: `Work item: 52` or `Work item: 81 — October billing`. A file with one unlabeled line is the old format and is still read. The commented starter is [docs/specs/_template/work-item.md](specs/_template/work-item.md). Leave the ids out of `tasks.md`.

On an Azure Repos remote (`dev.azure.com` or `*.visualstudio.com`), `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-intake-to-specs` ask once after they create a new spec folder. The question is optional: reply with the id, or skip. Intake lists every new slug in that one question so the user can give an id per slug. A reply writes one line per id. Skip writes nothing and does not ask again in that run. GitHub and other hosts are not asked. Those skills do not create the Feature. Creating a Feature is [`/crav1-specs-to-ado`](from-specs-to-ado.md).

The commit mention picks the line whose label matches the slice being worked. If that match is unclear, the commit skills ask. They do not guess.

The file can still be added by hand.

`/crav1-draft-commit-message` keeps the subject and description as drafted, then adds a blank line and the mention as the last line of the Description, so a GitKraken paste includes it. `/crav1-finalize-commit` commits that same text and keeps the line when it checks HEAD and when it strips a Cursor attribution trailer. `/crav1-open-pr` adds a `## Work item` section when the file has an id. The pull request title stays `<slug>: short summary`. The body stays What / why, Spec (links to that slug’s `spec.md`, `plan.md`, and `tasks.md`), Verify, then the work-item section.

The mention is `#52` on Azure Repos (`dev.azure.com` or `*.visualstudio.com`) and `AB#52` on GitHub. Any other host adds no mention. `Work item: AB#52` or `Work item: #52` is used as written. With no file, the skills continue. On Azure Repos only, they print one hint. They do not block, and `/crav1-open-pr` still does not pass `--work-items`. Creating a Feature stays `/crav1-specs-to-ado`.

