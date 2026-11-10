#!/usr/bin/env python3
"""Kit entry point for the dependency-order sort (1.103.0).

The sort itself ships with the skills, at
.cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py, so it reaches every install.
This wrapper runs it from the kit repo: task-order.py <tasks.md> [--failed T7] [--json]
"""
import sys


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

sys.dont_write_bytecode = True  # before loading the skill script; no __pycache__ beside it (1.121.1)

import importlib.util
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"


def load():
    spec = importlib.util.spec_from_file_location("task_order", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
