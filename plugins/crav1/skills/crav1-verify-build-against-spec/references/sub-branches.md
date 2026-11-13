# Sub-branches and reverts (1.68.0)

Read only when `SKILL.md` says an entry has `(into <spec branch>)`, or a merged branch was later undone on the base. Do not open this file otherwise. The rules are unchanged.

**Sub-branches and reverts (1.68.0).** As skill `crav1-add-to-spec`, `references/branches.md` says under **Spec branch and sub-branches** and **Reverted**: sub-branches (entries with `(into <spec branch>)`) are left out of the Branches count and get `Sub-branches: <n> of <m> merged into <spec branch>.`, plus `left behind: <branch> (not in <spec branch>)` for one that never merged after the spec branch reached the base; done counts top-level branches only. A merged branch whose change was later undone on the base shows `<branch>: merged, reverted on <base> (<revert sha>)`. Both are report only and never block done. In verify.md they go with the Branches line in the TL;DR. "Demoable; they can ship / PR" needs every top-level branch merged, not every sub-branch.
