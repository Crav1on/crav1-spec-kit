# Resolution catalog (per plan issue)

Read by `/crav1-tighten-plan` when it builds the options for a plan `P#`.


| Id | Name | What it does | Typical impact |
| --- | --- | --- | --- |
| `split-task` | Split this T# | Replace one oversized task with independently verifiable `T#`s. Renumber if needed; fix the trace table. | `tasks.md` (+ `plan.md` trace / approach if it named the old id). |
| `add-verify` | Add verify | Name the kind and the checks on `verify:` (one or many; not one test per kind). Add `(spec: …)` if missing. | That `T#` line, unless trace also lacked the spec id. |
| `add-cases` | Name the cases | When the spec describes an algorithm, name several checks, including corner cases of the behavior it already states. | That `T#` verify note. |
| `add-regression` | Name the regression | Name checks that would fail if behavior that already works broke. | That `T#` verify note, or one new `T#` and the trace. |
| `add-integration` | Name the boundary | When two parts meet, name an integration test for that edge. | That `T#` or one new `T#`. A system test of the whole path does not replace it. |
| `cover-security` | Cover the security check | Map a kept check from `docs/system/security.md` or the spec Security section to a `T#`, or mark “covered by T#”. | Trace row; a new `T#` only when no task already proves that check. |
| `drop-scope` | Drop extra scope | Remove the step/`T#` that is not in the spec (or move it to plan Out of scope). | Smaller task list; trace still covers remaining acceptance. |
| `fix-trace` | Fix trace | Map acceptance/REQ ↔ `T#`. Add a covering task or mark “covered by T#”. | `plan.md` Trace table; maybe one new `T#`. |
| `retarget-files` | Fix files likely touched | Correct paths; mark `(proposed)` if no repo. Do not invent a new architecture. | `plan.md` Files section. |
| `name-linter` | Name the linter | Search the repo. When it has a linter or checker for the code the tasks will touch, name the tool and the command under `## Linter`, and say Build leaves that check green. When it does not, write that. Do not install one. | `plan.md` Linter section. |
| `park-risk` | Park as risk | Plan was treating a kept-open question as decided. Remove that decision from tasks; list it under Risks. | No silent product answer. |
| `send-to-spec` | Send to spec | This is a spec defect or a new product question. Do not patch the plan. | No disk change here. Next: `/crav1-tighten-spec` or `/crav1-resolve-open-questions`. |
| `keep` | Keep as written | Accept the cost (usually untestable or extra scope). | No disk change. Rare; say the cost. |
| `suggest` | Get a suggestion | Recommend one offered patch letter. No edits. | Stay on this `P#`. Always offer. |
| `ask` | Ask, don’t patch | At most 3 questions about this issue. | Retry this `P#`. |
