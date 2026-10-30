# Match to specs: **Landscape**

Part of `branches/repos-and-bundle/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Landscape

Write `docs/system/` in the destination from this skill’s `assets/` (same files as `docs/system/_template/`): `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`. An ADR file comes from `assets/adr.md` only when the table below says to write one.

When `docs/system/` is missing, seed it from the repos and the confirmed match, including `glossary.md` in that same pass. Do not run an intake interview. Do not respec a new product.

| File | Fill |
| --- | --- |
| `landscape.md` | What the repos are, in one short paragraph. Constraints only when a repo or the confirmed dump already shows them. Bulk assumptions are confirmed map facts only. Under `## How the parts connect`, one line per connection the repos or the confirmed dump already state. Do not invent a connection. Leave the feature index empty until the specs exist. Add `## Code with no slice` when the map listed uncovered code (repo, path, one line). That note is not a spec. |
| `repos.md` | Every repo in front of you, plus the destination when it is the new clean repo. Status `exists` when the checkout is a real repo; put the URL when you have one. The new clean repo stays without a remote. Boundaries only when the repos already show one. Include the `## Synced at` section. Leave it empty. |
| `diagrams.md` | Follow [references/diagrams.md](../references/diagrams.md). One context diagram of the repos as they are. Replace the sample. Do not invent services. |
| `glossary.md` | From `assets/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | Only where there was a real choice, with real alternatives, already visible in the repos or accepted on the map. Otherwise write no ADR. Hunches are not ADRs. |

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the repos plus the confirmed dump. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that source already uses. When that same source already says the expansion or meaning, put that text in Meaning. When the source never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the source already treats that word as a term. Write the file even when it has no rows. When `glossary.md` already exists, append only words or abbreviations that are not already rows. Do not rewrite, reorder, or edit existing rows. A new row goes in sorted place by term, not at the end (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). Do not change a Meaning cell that already has text. Do not run an extra interview.

When `docs/system/` already exists, do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not rewrite existing ADRs. Only fill gaps the match needs, the same rule as spark and ideas: a `repos.md` row for a repo that is not listed, with no `Synced at` line for it, a landscape ADR only for a real choice that is not already recorded, a context diagram only when `diagrams.md` has none of these repos, `## Code with no slice` when that note is missing and the map has uncovered code, `glossary.md` when that file is missing, and new glossary rows when the file exists. Append to `## Code with no slice` if it is already there. Do not rewrite the paragraphs around it. Write a missing `glossary.md`, or append new rows, from the same sources and the same glossary rules. Do not rewrite existing glossary rows. Do not set or clear an existing `Synced at` line in `repos.md`. When `repos.md` has no `## Synced at` section, add it after the table. This command does not record the commit. The feature index and the picture update are filled in Index, not here.

No `tasks.md`. No application code. No `git init` except the new clean repo they picked. No remotes.
