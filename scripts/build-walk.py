#!/usr/bin/env python3
"""Kit entry point for the build walk (1.142.0).

The script ships with the skill, at
.cursor/skills/crav1/crav1-build-walk/scripts/build_walk.py
This wrapper runs it from the kit repo.
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-build-walk/scripts/build_walk.py"


def load():
    spec = importlib.util.spec_from_file_location("build_walk", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
