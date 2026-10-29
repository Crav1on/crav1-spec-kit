#!/usr/bin/env python3
"""Kit entry point for the dependency-order sort (1.103.0).

The sort itself ships with the skills, at
.cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py, so it reaches every install.
This wrapper runs it from the kit repo: task-order.py <tasks.md> [--failed T7] [--json]
"""
import importlib.util
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"


def load():
    spec = importlib.util.spec_from_file_location("task_order", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(load().main(sys.argv[1:]))
