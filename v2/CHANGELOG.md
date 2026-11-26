# Changelog

## 2.0.0-alpha.1 (unreleased)

The first 2.0 skeleton. Not released. No tag.

- Event log schema v1, append-only, with ULID ids and an ISO time with an offset.
- Fold drops a duplicate id and gives a different body that shares an id a run suffix. Two streams merged in any order fold to the same state.
- Generated `sot/index.md`, `sot/facts.md`, `sot/decisions.md`, and `sot/assumptions.md`. Note pages render passage anchors from the log.
- Session files (`open`, `parked`, `ended`) and `.crav1-2/engine.json`.
- Path guard for the paths 2.0 is allowed to write. 1.x marks and 1.x lines stay put.
- User-level install, uninstall, and status. Codex is skipped because 1.x has no user-level Codex path.
- Alpha `/crav1-2-help` stub, so the install can be checked.

`/crav1-2-add-to-sot`, `/crav1-2-show-sot`, `/crav1-2-link-to-spec`, and this-session are not in this version.
