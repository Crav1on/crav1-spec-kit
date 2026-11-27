# After a choice

1. Patch **only** this question.
   - **Keep open:** leave the bullet. You may sharpen the wording if they asked; do not resolve it. When the slice has `tasks.md`, ask once which tasks it blocks, as options: each unticked `T#` (multi-select), **The whole slice**, or **None**. A pick of tasks writes one indented line under the question, `- Blocks: T2, T4`, replacing an earlier `Blocks:` line (see `crav1-add-to-spec` `references/open-questions.md`). **None** writes `- Blocks: none`, not nothing. Reason may follow. **The whole slice** writes `- Blocks: whole slice`, not nothing. `Blocks: none` blocks no current task. A missing `Blocks:` line is not this pick.
   - **Answer:** fold the decision into the right place (requirement/journey/acceptance, `## Constraints`, non-goals/later, or a new/updated ADR). When the question had an `Answered:` line, keep that quote and its source with the decision. **Remove** it from Open questions, with its `Asked:`, `Pending:`, and `Answered:` lines (or mark the assumption resolved). Never remove an `Approved:` line. An acceptance line you add is yes/no. Name unit, system, or browser only when that kind is already obvious from the answer. Otherwise leave the kind for plan. Do not invent a test list.
   - **Cut from v0:** move to non-goals/later; remove from Open questions.
2. After **Answer** or **Cut from v0**, and not after **Keep open**, run the stale-state check before the recap. The script is `../crav1-add-to-spec/scripts/stale_state_lines.py --spec docs/specs/<slug>/spec.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

   `<interpreter> -X utf8 ../crav1-add-to-spec/scripts/stale_state_lines.py --spec docs/specs/<slug>/spec.md --changed <Q# or the constraint id> --old "<old date or old option>" --new "<the decision's words>" --decision "<short decision>"`

   It lists notes under that constraint or question that still say `Possible answer`, `Waiting for`, `stands until`, `not a settlement`, or `**Conflict:**`, and other lines that still carry the old value. A blockquote, an `Answered:` line, and a line whose old value sits only inside quotes are excluded and never changed. When `n_notes` and `n_lines` are both 0, say nothing and go on. Otherwise ask one batch card. The question is the script's `question`, `Mark N notes superseded and update M lines?`, and the reply shows its `diff`. On yes, run the same command with `--yes`. That appends `Superseded <date> by <decision>.` to each note and rewords the derived lines. On leave, write nothing else. Do not search only for the removed question title.
3. Recap **Added / Removed / Still open** for this `Q#`.
4. If the answer makes a named diagram/ADR wrong, either they also chose `sync-here`, or the **next** item is that drift (do not silently skip).
5. Otherwise advance to the next unanswered `Q#`.

If none remain, the list-done line in `SKILL.md` names the next file. Do not open it from here when questions remain.
