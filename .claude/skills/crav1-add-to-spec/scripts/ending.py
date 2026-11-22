#!/usr/bin/env python3
"""Endings for /crav1-add-to-spec, from the shared run-ending helper (1.200.0).

Run next comes first. A design branch that is checked out or owns the change
is a stay card, and the ending never tells you to switch to the default branch.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


_utf8_stdout()


def _helper():
    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "run_ending.py"
    spec = importlib.util.spec_from_file_location("run_ending_add", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(state: dict) -> dict:
    """state: root, slug, changed, reopened, uncommitted. Prints nothing."""
    helper = _helper()
    card = helper.design_branch_card(state["root"]) if state.get("root") else None
    slug = str(state.get("slug") or "").strip()
    count = state.get("uncommitted") or None
    if state.get("reopened") and slug:
        ending = helper.compose(
            "The new information reopened the walk.",
            [("Resume the spec walk:", f"/crav1-tighten-and-plan-ready-to-build {slug}")],
            uncommitted=count)
    elif state.get("changed") and slug:
        ending = helper.compose(
            "The new information is not tightened yet.",
            [("Tighten the spec:", f"/crav1-tighten-spec {slug}")],
            uncommitted=count)
    else:
        ending = helper.compose("nothing needed now.", [], uncommitted=count)
    return {"ending": ending, "card": card, "switch_to_default": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print the add-to-spec ending.")
    parser.add_argument("--root", default="")
    parser.add_argument("--slug", default="")
    parser.add_argument("--changed", action="store_true")
    parser.add_argument("--reopened", action="store_true")
    parser.add_argument("--uncommitted", type=int, default=0)
    args = parser.parse_args(argv)
    result = build({"root": args.root, "slug": args.slug, "changed": args.changed,
                    "reopened": args.reopened, "uncommitted": args.uncommitted or None})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
