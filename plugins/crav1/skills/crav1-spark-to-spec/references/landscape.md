# crav1-spark-to-spec: landscape

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Thin landscape

When `docs/system/` does not exist (greenfield or brownfield, including an existing app), create it before the spec from this skill’s `assets/system/` (same files as `docs/system/_template/` and as intake `assets/` `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr.md`):

| File | Fill |
| --- | --- |
| `landscape.md` | One short paragraph of what is in front of you (the app when it exists; otherwise the spark). **v0** is this slice. **Later** stays short. Bulk `A#`s are the assumptions already listed. Constraints are only ones the repo or the spark already shows. Under `## How the parts connect`, one line per connection the repo or the spark already states. Do not invent a connection. Leave the feature index empty until the spec exists. |
| `repos.md` | The repo in front of you. Status `exists` when this checkout is a real repo; `proposed` until a URL exists. One boundaries line only when the repo already shows one. Include the `Synced at` column. Leave that cell empty. |
| `diagrams.md` | One system-context diagram of what is actually there. One heading, one sentence, one fence. Do not invent services. Slice sequences stay on the spec. |
| `glossary.md` | From `assets/system/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | From `assets/system/adr.md` only when a cross-cutting choice already had real alternatives. Otherwise write no ADR. |

Fill those files from the repo in front of you and from answers already given. Do not ask a landscape interview. Do not run `/crav1-bundle-to-specs`. Do not respec the whole product. If this slice needs a repo that is not the checkout in front of you, add that `repos.md` row and a landscape ADR in this seed, before the spec.

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the repo in front of you, the spark, and answers already given. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that source already uses. When that same source already says the expansion or meaning, put that text in Meaning. When the source never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the source already treats that word as a term. Write the file even when it has no rows. When `glossary.md` already exists, append only words or abbreviations that are not already rows. Do not rewrite, reorder, or edit existing rows. Do not change a Meaning cell that already has text. Do not run an extra interview.

When `docs/system/` already exists, do not rewrite `repos.md` or existing ADRs except the new-repo case below, and do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not set `Synced at` on a repo row. If `glossary.md` is missing, write only that file from the same sources and the same glossary rules. If it exists, append only new rows under those rules. If they need a new repo, write a landscape ADR from `assets/system/adr.md` and a `repos.md` row before the spec. Those are the only edits before the spec. The index row and the picture update come after the spec exists.

**Synced at.** This command reads one slice. It does not touch the `Synced at` column in `repos.md`. When this run read the code for this slice, write or update one line in that `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. The branch is the branch that was read. The short sha is seven characters, the commit that was read. The date is the date of that read, `YYYY-MM-DD`. One line per repo. That line has one entry per branch read, separated by `; `, for example `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`. When the branch read already has an entry, replace only that entry; a new branch adds an entry at the end. Leave the other entries, a `(dropped)` on them, and other repos' `Synced at` lines. When this run did not read that code, do not invent the line. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.
