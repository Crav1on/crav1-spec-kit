# Stacking

Read this when a task needs code that is still only on an unmerged branch. Work may continue on other branches while earlier branches are unmerged. One checkout still follows one branch.

The task is cut from that unmerged branch, not from `develop` (or the other stated base). `scripts/build_walk.py stack` writes `Cut from:`. A dependency whose branch is already merged does not change the cut. The branch offer still refuses a merged or deleted name, using the same helper as `build_map.py --recommend` (1.140.0).

The merge list is ordered. A branch merges back into the branch it was cut from before that parent merges onward.

```text
Merge: feat/orders-later into feat/orders-note
Merge: feat/orders-note into feat/orders-host-setup-scripts
Merge: feat/orders-host-setup-scripts into develop
```

Show that list in the progress file and in the report. Never recommend a merged or deleted branch. When the only name is already merged, the offer is a new branch from the stated base, and the description says why.
