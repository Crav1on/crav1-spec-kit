# Parked and retired specs (1.60.0)

Read only when `SKILL.md` says a spec is under `docs/specs/retired/`, is only a `Moved:` pointer, or has a `Parked:` line. Do not open this file for a ready slug. The rules are unchanged.

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: do not build it, and leave it off the board's to-build list. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.
