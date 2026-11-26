---
name: crav1-2-help
description: >-
  Alpha help for kit 2.0. Use when someone asks what this crav1-2 install
  can do. Names add-to-sot, show-sot, and link-to-spec. Writes nothing.
---

# crav1-2 help (alpha)

This install is an alpha. It is not a release. It writes nothing from this skill.

- `/crav1-2-add-to-sot` captures one source as one note under `sot/`. `this-session` captures the current chat.
- `/crav1-2-show-sot` reads that folder and writes nothing.
- `/crav1-2-link-to-spec <slug>` reads notes that have not been read against that 1.x spec, shows cards, and writes `crav1-2:item` lines. `dry-run` writes nothing. `park` and `resume` use the session file.

The engine is `python -m crav1_2` with `~/.crav1-2/engine` on `PYTHONPATH`. A project records the engine version in `.crav1-2/engine.json` after `init`. This install does not commit.
