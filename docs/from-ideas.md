# From a pile of ideas to a spec

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when you have **more than a spark**: several ideas, maybe UX notes, maybe “I think we should use X”, but it is not a spec you would hand to an agent to build.

You still do **not** start by coding. You add an architecture interview and you write diagrams + ADRs. The canonical file remains `spec.md`. Formats are exports.

Spark-only? Use [from-nothing](from-nothing.md) and `/crav1-spark-to-spec` instead.

## First prompt

New Agent chat. Strong reasoning model. Not Plan Mode yet.

```text
/crav1-ideas-to-spec

Format: EARS
# or: BDD | OpenSpec | YAML | JSON | BMAD
# multiple allowed, e.g. Format: EARS, BMAD

Bundle:
- <idea 1>
- <idea 2>
- Technical thoughts: <stack, shape, constraints, “I would like to…”>

Treat hunches as proposed, not decided.
Do not write code. Capture first, then architecture questions.
```

That slash command *is* the prompt. Pin `/crav1-ideas-to-spec` as a Custom Mode if you want it on for the session.

## The extra steps (vs spark)


| Phase          | You                                    | Agent                                                                                     |
| -------------- | -------------------------------------- | ----------------------------------------------------------------------------------------- |
| A Capture      | Paste the pile                         | Clusters intent vs hunches vs undecided, v0 vs later, ≤5 product questions, format choice |
| B Architecture | Answer / “use assumptions”             | ≤7 technical questions + 2–3 options at one abstraction level                             |
| C Write        | Pick options, correct A-numbers        | `spec.md`, `diagrams.md`, ADRs, `export/<format>`                                         |
| D Critique     | Optional                               | `/crav1-architecture-reviewer` then `/crav1-tighten-spec` (one issue at a time)                        |
| D2 Questions   | Leftover Open questions                | `/crav1-resolve-questions` — keep open or answer, one `Q#` at a time                             |
| E Export again | “also want JSON”                       | `/crav1-export-spec` — does not change behavior                                                 |
| Stop           | v0 is demoable and ADRs match diagrams | New chat, Plan Mode, `@spec.md` `@diagrams.md` `@adr/`                                    |


Good replies in B:

- “Source of truth is local files. Sync is later.”
- “Option 2, because I am solo and must ship a demo.”
- “Auth is a non-goal. That hunch is dropped.”

Bad replies:

- “All options, we’ll see in the code.”
- “Add a platform layer in case we need it.”



## What gets written

```text
docs/specs/<slug>/
  spec.md                 # source of truth
  diagrams.md             # mermaid preferred; ascii when better
  adr/0001-<decision>.md  # only real choices (MADR-style)
  export/ears.md          # or bdd.md, spec.yaml, spec.json, bmad.md
  export/openspec/        # if you chose OpenSpec
```

ADRs use the MADR-shaped template in skill `crav1-ideas-to-spec` `assets/adr.md` (drop-in: `.cursor/skills/crav1/crav1-ideas-to-spec/assets/adr.md`; same as `docs/specs/_template/adr.md`). Status starts as `proposed`. Hunches with no alternative belong under Constraints, not as ADRs.

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

Then `/crav1-tighten-spec` to walk the numbered issues. Then `/crav1-resolve-questions` for leftover Open questions.

## After accept

```text
/crav1-plan-from-spec
@docs/specs/<slug>/spec.md
@docs/specs/<slug>/diagrams.md
@docs/specs/<slug>/adr

Stay inside v0. Do not reopen rejected options unless an ADR is still proposed.
Do not code.
```

Or Cursor Plan Mode with the same `@` files. The skill writes `plan.md` and `tasks.md` in the spec folder so the plan lives in git, not only in the Plan Mode UI.

Then, in a **new** chat (or pin `/crav1-implement-task` as a Custom Mode):

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

When you are ready to commit (after a `T#` or a live fix):

```text
/crav1-draft-commit-message
```

Paste the **Summary** and **Description** blocks into GitKraken. The skill does not run `git commit` unless you also ask it to.

To change the wording first, then copy **or** create the git commit:

```text
/crav1-review-commit
```

That command drafts the same way, then asks `copy` / `edit` / `rewrite` / `commit`. It does not push.

First time (no persist rule yet) it asks:

- **`style.md`, this commit only**
- **`style.md`, this commit and onward** — writes `.cursor/rules/draft-commit-style.mdc`
- **Git log, this commit only** — match this repo’s recent messages
- **Git log, this commit and onward** — writes `.cursor/rules/draft-commit-gitlog.mdc`

Onward choices are mutually exclusive (writing one removes the other). To get the prompt again: delete that rule file.

Inner-loop example (same skill; `/crav1-fix-live` also works):

```text
/crav1-fix-from-verify
Gap: T# claimed done, unverified — POST /register never reached SQL
Live command: POST <url>/register
Do not change spec.md.
```

