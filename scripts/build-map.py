#!/usr/bin/env python3
"""Kit entry point for the build map (1.128.0).

The script ships with the skill, at
.cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py
This wrapper runs it from the kit repo.
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py"


def load():
    spec = importlib.util.spec_from_file_location("build_map", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
