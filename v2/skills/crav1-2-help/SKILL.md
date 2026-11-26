---
name: crav1-2-help
description: >-
  Alpha stub for kit 2.0. Use when someone asks what this crav1-2 install
  can do. It says add-to-sot, show-sot, and link-to-spec are not in this
  build. Writes nothing.
---

# crav1-2 help (alpha)

This is an alpha stub. It exists so the kit 2.0 install can be checked. It is not the 1.x help command.

This build ships the engine only: an append-only event log, a fold, generated `sot/` pages, and the installer. It writes nothing from this skill.

These commands are not in this build:

- `/crav1-2-add-to-sot`
- `/crav1-2-show-sot`
- `/crav1-2-link-to-spec`

The engine on this machine is `python -m crav1_2` with `~/.crav1-2/engine` on `PYTHONPATH`. A project records the engine version in `.crav1-2/engine.json` after `init`.
