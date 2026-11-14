#!/usr/bin/env python3
"""Kit entry point for whole-branch build-walk runs (1.155.0).

The script ships with the skill, at
.cursor/skills/crav1/crav1-build-walk/scripts/branch_run.py
This wrapper runs it from the kit repo.
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-build-walk/scripts/branch_run.py"


def load():
    spec = importlib.util.spec_from_file_location("branch_run", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
