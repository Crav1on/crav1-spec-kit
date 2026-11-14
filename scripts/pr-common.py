#!/usr/bin/env python3
"""Kit entry point for the shared PR steps (1.158.0).

The script ships with the skill, at
.cursor/skills/crav1/crav1-open-pr/scripts/pr_common.py
This wrapper runs it from the kit repo.
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-open-pr/scripts/pr_common.py"


def load():
    spec = importlib.util.spec_from_file_location("pr_common", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
