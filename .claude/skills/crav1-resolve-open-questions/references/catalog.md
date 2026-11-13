# Resolution catalog (per question)

Read only when `SKILL.md` says so.

| Id | Name | What it does | Typical impact |
| --- | --- | --- | --- |
| `keep-open` | Keep open | Leave this question unanswered. No product decision. | Still blocks a fully closed spec. Disk: none, unless they asked to rephrase. **Always offer this.** |
| `answer-A` … | Answer: \<concrete choice\> | Commit one of the real alternatives you listed. | `spec.md` gains a SHALL, constraint, or non-goal; this `Q#` leaves the open list. |
| `answer-custom` | Answer in my words | Use their prose as the decision. Put it in the correct section; do not dump the paragraph into Open questions. | Same as a concrete answer. Offer when choices might not fit. |
| `cut-from-v0` | Cut from v0 | Not deciding how — deciding **not in v0**. | Smaller demo; question removed; lives under non-goals/later. |
| `to-constraint` | Record as constraint | The answer is an accepted tech/limit, not a user journey. | `## Constraints`; not a REQ SHALL about libraries/tables. |
| `to-adr` | Decide via ADR | Real alternatives remain worth recording. Write/update `adr/NNNN`, status `proposed` or `accepted` as they said. | Requirements stay behavioral; question removed once the ADR captures the choice (or stays open if they only drafted the ADR as proposed **and** asked to keep the question — rare; default is remove). |
| `ask` | Narrow first | Ask at most 3 multiple-choice questions **about this Q#**. No file edits. | Retry this `Q#` next turn. Use when your answer options would be a guess. |
| `sync-here` | Sync this artifact | Update the diagram/ADR this answer invalidates. | Only with an answer, not with keep-open. |

Do **not** offer a turn-level “answer all with assumptions.” Guessing is `ask` or `keep-open`.
