# crav1-ideas-to-spec: landscape

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Thin landscape

When `docs/system/` does not exist (greenfield or brownfield, including an existing app), create it before the spec from this skill’s `assets/system/` (same files as `docs/system/_template/` and as intake `assets/` `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr.md`):

| File | Fill |
| --- | --- |
| `landscape.md` | One short paragraph of what is in front of you (the app when it exists; otherwise the bundle). **v0** is this slice. **Later** stays short. Bulk `A#`s are the assumptions already listed. Constraints are only ones the repo or the bundle already shows. Under `## How the parts connect`, one line per connection the repo or the bundle already states. Do not invent a connection. Leave the feature index empty until the spec exists. |
| `repos.md` | The repo in front of you. Status `exists` when this checkout is a real repo; `proposed` until a URL exists. One boundaries line only when the repo already shows one. Include the `## Synced at` section. Write a line there only when this run read that whole repo, as under **Synced at** below. |
| `diagrams.md` | One system-context diagram of what is actually there. One heading, one sentence, one fence. Do not invent services. Slice sequences stay in `docs/specs/<slug>/diagrams.md`. |
| `glossary.md` | From `assets/system/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | From `assets/system/adr.md` only when a cross-cutting choice already had real alternatives. Otherwise write no ADR. Slice ADRs stay under `docs/specs/<slug>/adr/`. |

Fill those files from the repo in front of you and from answers already given. Do not ask a landscape interview. Do not run `/crav1-bundle-to-specs`. Do not respec the whole product. If this slice needs a repo that is not the checkout in front of you, add that `repos.md` row and a landscape ADR in this seed, before the spec.

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the repo in front of you, the bundle, and answers already given. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that source already uses. When that same source already says the expansion or meaning, put that text in Meaning. When the source never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the source already treats that word as a term. Write the file even when it has no rows. When `glossary.md` already exists, append only words or abbreviations that are not already rows. Do not rewrite, reorder, or edit existing rows. A new row goes in sorted place by term, not at the end (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). Do not change a Meaning cell that already has text. Do not run an extra interview.

When `docs/system/` already exists, do not rewrite `repos.md` or existing ADRs except the new-repo case below and the `Synced at` line in `repos.md` of a repo this run read as a whole, and do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. If `glossary.md` is missing, write only that file from the same sources and the same glossary rules. If it exists, append only new rows under those rules. If they need a new repo, write a landscape ADR from `assets/system/adr.md` and a `repos.md` row before the spec. Those are the only edits before the spec. The index row and the picture update come after the spec exists.

**Synced at.** Where this run reads a repo, record the commit it actually read. `Synced at` is one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, in the `## Synced at` section of `repos.md`, for example `- orders-api main@abc1234, 2026-10-07` (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`.

When this run reads a whole repo, set that repo's `Synced at` line in `repos.md` to the branch and commit actually read. When that repo and branch already have a line, replace only that line; a new one goes in sorted place (repo, then branch). Leave every other line. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the `## Synced at` section is missing, add it after the table. Do not write a slice `Synced at` line for a repo this run read as a whole.

When this run reads only one slice, do not touch the `## Synced at` section of `repos.md`. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. One line per repo and branch read, for example `Synced at: orders-api develop@00344be, 2026-10-15` and, on the next line, `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19` (1.84.0). When that repo and branch already have a line, replace only that line; a new one goes in sorted place (repo, then branch). Leave the other lines and a `(dropped)` on them.

Do not stamp a repo or a slice this run did not read. A repo or branch with no line keeps no line. A consumer measuring drift uses, for each repo and branch, the older of the repo line and the slice line, and no line means unknown, so fall back to spec file commit dates.
