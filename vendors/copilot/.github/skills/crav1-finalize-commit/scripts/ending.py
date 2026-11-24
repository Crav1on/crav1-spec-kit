#!/usr/bin/env python3
"""Endings for /crav1-finalize-commit, from the shared run-ending helper (1.200.0).

Run next comes first. A failed commit has no Run next. A design branch that
owns the change is a stay card and is never switched to the default branch.
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
    spec = importlib.util.spec_from_file_location("run_ending_commit_skill", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(state: dict) -> dict:
    helper = _helper()
    card = helper.design_branch_card(state["root"]) if state.get("root") else None
    if state.get("failed"):
        return {"ending": "", "card": card, "switch_to_default": False}
    slug = str(state.get("slug") or "").strip()
    branch = str(state.get("branch") or "").strip()
    count = state.get("uncommitted") or None
    pr = state.get("pr")
    if state.get("walk") and slug and branch:
        ending = helper.compose(
            "The build walk on this branch is not finished.",
            [(f"Continue the build walk on {branch}:", f"/crav1-build-walk {slug} {branch}")],
            uncommitted=count)
    elif pr:
        ending = helper.compose(
            f"PR {pr} does not have this commit yet.",
            [(f"Push to PR {pr} and comment:", f"/crav1-open-pr pr{pr}")],
            uncommitted=count)
    elif state.get("feature"):
        ending = helper.compose(
            "The commit is only local and no pull request is open.",
            [("Push and open the pull request:", "/crav1-open-pr")],
            uncommitted=count)
    else:
        ending = helper.compose(
            "The commit is only local.",
            [("Push the specs repo:", "git push")],
            uncommitted=count)
    return {"ending": ending, "card": card, "switch_to_default": False}


def _bind_vendor(argv):
    """1.201.0: --vendor codex prints $crav1- commands. The default stays /."""
    source = sys.argv[1:] if argv is None else argv
    if "--vendor" not in source and not any(str(item).startswith("--vendor=") for item in source):
        return argv
    path = Path(__file__).resolve().parents[2] / "crav1-update-kit" / "scripts" / "vendor_prefix.py"
    if not path.is_file():
        print("Refused: --vendor needs the vendor table.", file=sys.stderr)
        raise SystemExit(2)
    import importlib.util
    spec = importlib.util.spec_from_file_location("crav1_vendor_prefix", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.install_from_argv(argv)


def main(argv=None) -> int:
    argv = _bind_vendor(argv)
    parser = argparse.ArgumentParser(description="Print the finalize-commit ending.")
    parser.add_argument("--root", default="")
    parser.add_argument("--slug", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--pr", default="")
    parser.add_argument("--walk", action="store_true")
    parser.add_argument("--feature", action="store_true")
    parser.add_argument("--failed", action="store_true")
    parser.add_argument("--uncommitted", type=int, default=0)
    args = parser.parse_args(argv)
    result = build({"root": args.root, "slug": args.slug, "branch": args.branch, "pr": args.pr,
                    "walk": args.walk, "feature": args.feature, "failed": args.failed,
                    "uncommitted": args.uncommitted or None})
    print(result["ending"], end="")
    if result["card"]:
        print(json.dumps({"card": result["card"], "switch_to_default": False}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
