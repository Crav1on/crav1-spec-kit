# Parked and retired

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: do not build it, and leave it off the board's to-build list. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.
