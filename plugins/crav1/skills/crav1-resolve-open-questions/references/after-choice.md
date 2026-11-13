# After a choice

1. Patch **only** this question.
   - **Keep open:** leave the bullet. You may sharpen the wording if they asked; do not resolve it. When the slice has `tasks.md`, ask once which tasks it blocks, as options: each unticked `T#` (multi-select), **The whole slice**, or **None**. A pick of tasks writes one indented line under the question, `- Blocks: T2, T4`, replacing an earlier `Blocks:` line (see `crav1-add-to-spec` `references/open-questions.md`). **None** writes `- Blocks: none`, not nothing. Reason may follow. **The whole slice** writes `- Blocks: whole slice`, not nothing. `Blocks: none` blocks no current task. A missing `Blocks:` line is not this pick.
   - **Answer:** fold the decision into the right place (requirement/journey/acceptance, `## Constraints`, non-goals/later, or a new/updated ADR). When the question had an `Answered:` line, keep that quote and its source with the decision. **Remove** it from Open questions, with its `Asked:`, `Pending:`, and `Answered:` lines (or mark the assumption resolved). Never remove an `Approved:` line. An acceptance line you add is yes/no. Name unit, system, or browser only when that kind is already obvious from the answer. Otherwise leave the kind for plan. Do not invent a test list.
   - **Cut from v0:** move to non-goals/later; remove from Open questions.
2. Recap **Added / Removed / Still open** for this `Q#`.
3. If the answer makes a named diagram/ADR wrong, either they also chose `sync-here`, or the **next** item is that drift (do not silently skip).
4. Otherwise advance to the next unanswered `Q#`.

If none remain, the list-done line in `SKILL.md` names the next file. Do not open it from here when questions remain.
