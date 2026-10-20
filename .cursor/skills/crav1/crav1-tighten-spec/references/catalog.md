# crav1-tighten-spec: catalog

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Resolution catalog (per issue, not per turn)

Pick the ones that fit; rewrite names to the actual REQ/ADR.

| Id | Name | What it does | Typical impact |
| --- | --- | --- | --- |
| `make-testable` | Make this falsifiable | Rewrite this SHALL/acceptance into a yes/no check. No extra features. Do not add a test list. Name unit, system, or browser only when that kind is already obvious from the source. | `spec.md` that requirement/journey. One yes/no outcome. |
| `cut-from-v0` | Cut from v0 | Move this capability to non-goals / later. | Smaller demo; journeys/acceptance that depended on it go away or shrink. |
| `to-constraint` | Treat as constraint | Remove mechanism from requirements; record accepted tech under `## Constraints`. | Product spec stays behavioral; stack is binding without pretending it is a user journey. |
| `to-adr` | Make / reframe an ADR | This is a real choice with alternatives. Write or fix `adr/NNNN`. Status `proposed` unless they already decided. | Requirements lose “how”; decision is reviewable. May need a later `sync` of diagrams. |
| `to-open-question` | Leave as open question | Do not guess. Add or keep a numbered open question. | v0 stays blocked on this until they answer; no silent product decision. |
| `mark-dropped` | Mark the branch dropped (1.64.0) | Only for a listed work branch that is gone and not merged. End its `Synced at` entry with ` (dropped)`. Keep the entry; it stays a record of what was read. | `spec.md` Synced at line. The branch stops counting toward done. |
| `add-missing-path` | Add the missing path | Write the empty, fail, or happy path (and a matching yes/no acceptance line) that is absent. Do not add a test list. Name unit, system, or browser only when that kind is already obvious from the source. | Journeys plus one yes/no line. The kind stays for plan unless the source already made it obvious. |
| `keep` | Keep as written | Explicitly accept the current text. Say the cost (usually untestable or blurred layers). | No disk change. Use rarely; call out the cost. |
| `suggest` | Get a suggestion | Recommend one of the patch letters already offered, with a short why. No edits. Re-offer the same menu. | Stay on this `I#` until they pick a real resolution. Always offer this. |
| `ask` | Ask, don’t patch | Ask at most 3 questions **about this issue**. No file edits. | Next turn retries this `I#` with answers. |
| `sync-here` | Sync this artifact | Update the diagram/ADR/export that this issue names so it matches `spec.md`. Does not change product intent. | Only the named files. |

Do **not** offer a turn-level `apply-notes` that applies the whole architecture review. Each reviewer bullet is its own `I#`.

Do **not** offer finish the gap, add a verify test, or leave it. Those choices belong to `/crav1-plan-from-spec`.

You may add `sync-here` as a **second letter on the same issue** only when the chosen resolution would immediately make a named diagram/ADR wrong (“B, then sync the sequence diagram”). Still one issue.

### When they pick `suggest`

Do **not** patch. Stay on this `I#`.

1. Name the **letter** and catalog id you would pick from the options already shown.
2. **Why** — 2–4 sentences (testability, v0 size, requirement vs decision). Do not invent a new resolution or a product feature.
3. Re-offer the **same** patch letters (and `ask` / `keep` if they were present), with the suggested one first and its label ending in ` (Recommended)`; the letters do not change. Include `suggest` again only if they want a different recommendation; at most **one** alternate, then they must pick a patch letter, `ask`, or `keep`.

Then stop. Do not advance to `I+1`.
