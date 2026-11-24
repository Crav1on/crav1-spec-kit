# crav1-add-to-spec: opening

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Opening question (1.56.0)

This skill now also replaces `/crav1-match-dump-to-specs`, `/crav1-code-into-specs`, and `/crav1-meeting-to-specs`. Their rules are kept, unchanged, as branches. Ask one question, with the questions tool when it is available:

1. **A fact.** One new piece of information for one spec. Follow the rest of this file.
2. **A dump.** A later pile of notes, tickets, old docs, diagrams, or screenshots for one or many specs, or a mail or a chat thread (`mail`, `chat`). Follow [branches/dump/BRANCH.md](../branches/dump/BRANCH.md).
3. **A code change.** A commit, a range, the branch diff, or a pull request (1.65.0) that already landed or is open. Follow [branches/code-change/BRANCH.md](../branches/code-change/BRANCH.md).
4. **A meeting.** Minutes or a transcript. Follow [branches/meeting/BRANCH.md](../branches/meeting/BRANCH.md).

Skip the question when the message shows which: a short new fact with an @-mentioned spec is 1; several files, a pasted pile, a `.eml`, or a chat export is 2; a commit, a SHA, a range, or "the branch diff" is 3; minutes or a transcript is 4. Where a branch hands a kept quote to `/crav1-add-to-spec`, that is choice 1 of this skill, with the handoff that branch describes.


You add new information to **one existing** spec. Then you check whether `docs/system/` or another spec has to change, and you report that impact. You do not silently rewrite those other files. You do not write application code. You do not plan, implement, or commit.

This is not `/crav1-tighten-spec`. Tighten is for mushy wording. This skill is for new information. If the message is only “make this tighter” and brings no new fact, tell them `/crav1-tighten-spec` and do not edit.

This is not `/crav1-existing-to-specs`, `/crav1-bundle-to-specs`, `/crav1-spark-to-spec`, or `/crav1-ideas-to-spec`. Those create the folders. This skill updates one spec that already exists. Do not send this job to those commands, and do not absorb theirs. Do not create a new slug here.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

When the message or the files make one option the better fit, list it first and end its label with ` (Recommended)`. Otherwise keep the order above with no label.
