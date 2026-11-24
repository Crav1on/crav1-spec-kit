#!/usr/bin/env python3
"""Thin wrapper: this skill documents scripts/claims.py, which lives in crav1-build-walk."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()


def _target() -> Path:
    here = Path(__file__).resolve().parent
    name = Path(__file__).name
    # .cursor/skills/crav1/<this-skill>/scripts -> sibling crav1-build-walk/scripts
    candidate = here.parent.parent / "crav1-build-walk" / "scripts" / name
    if candidate.is_file():
        return candidate
    sys.stderr.write(name + " was not found in crav1-build-walk/scripts\n")
    sys.exit(2)


if __name__ == "__main__":
    target = _target()
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
