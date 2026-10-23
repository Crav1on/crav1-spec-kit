# crav1-map-pipeline-environments: section questions

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.5; the rules are unchanged.

## Section questions

Use the questions tool when it is available. Options only. Put that section’s items in the question prompt.

**One environment or shared, when it lists proposed lines.** Options:

1. **Append every proposed line in this section.**
2. **Append none of this section.**
3. **I will edit this section.**

**One environment, when nothing is in it.** Options:

1. **Nothing is in this section.**
2. **I will edit this section.**

**Shared, when nothing is shared.** Options:

1. **Nothing is shared.**
2. **I will edit this section.**

**Unclear, when it lists resources.** Options:

1. **Leave every resource in this section unmarked.**
2. **I will edit this section.**

**Unclear, when nothing is unclear.** Options:

1. **Nothing is unclear.**
2. **I will edit this section.**

**Branches, when it lists proposed lines.** Options:

1. **Append every proposed line in this section** (to `docs/environments/promotion.md`).
2. **Append none of this section.**
3. **I will edit this section.**

**Branches, when nothing is in it.** Options:

1. **No pipeline names a branch.**
2. **I will edit this section.**

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not ask that section again. Sections already answered stay answered. A line they struck is not appended. A resource they add that no pipeline step names stays out. Say the pipeline does not name it. Omitting a listed item does not drop it.

An unclear confirm writes no line. Do not write `marked by the user` from this command.
