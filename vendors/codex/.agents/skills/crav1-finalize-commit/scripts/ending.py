#!/usr/bin/env python3
"""Endings for /crav1-finalize-commit, from the shared run-ending helper (1.200.0).

Run next comes first. A failed commit has no Run next. A design branch that
owns the change is a stay card and is never switched to the default branch.

`--walk` reads the spec walk and the build-progress files (1.207.0). A
reopened or unfinished spec walk resumes `/crav1-tighten-and-plan-ready-to-build`.
Otherwise the build walk uses the working branch, never main or master unless
that branch is the one checked out.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

BASE_BRANCHES = frozenset({"main", "master", "develop"})
BRANCH_LINE = re.compile(r"^Branch:\s*(\S+)", re.M)


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


def _walk():
    path = Path(__file__).resolve().parents[2] / "crav1-tighten-and-plan-ready-to-build" / "scripts" / "walk_progress.py"
    spec = importlib.util.spec_from_file_location("walk_progress_commit_ending", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def spec_folder(root: str, slug: str) -> Path | None:
    base = Path(root) if root else None
    candidates = []
    if base and slug:
        candidates.extend([base / "docs" / "specs" / slug, base / slug, base / "docs" / "specs" / slug / "spec.md"])
    if base:
        candidates.append(base)
    for item in candidates:
        folder = item.parent if item.suffix == ".md" else item
        if (folder / "walk-progress.md").is_file() or (folder / "spec.md").is_file():
            return folder
    return None


def _git_branch(root: Path | None) -> str:
    if root is None:
        return ""
    try:
        done = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if done.returncode != 0:
        return ""
    name = done.stdout.strip()
    return "" if name in ("", "HEAD") else name


def progress_branches(folder: Path | None) -> list[str]:
    if folder is None:
        return []
    found = []
    directory = folder / "build-progress"
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        match = BRANCH_LINE.search(text)
        if match and match.group(1) not in found:
            found.append(match.group(1))
    return found


def spec_walk_unfinished(folder: Path | None) -> bool:
    """True when walk-progress has a reopened step or a locked step that is not recorded yet."""
    if folder is None or not (folder / "walk-progress.md").is_file():
        return False
    mod = _walk()
    data = mod.load(folder)
    steps = data.get("steps") or {}
    locked = [step for step in mod.ORDER if step != "playbook"]
    recorded = [step for step in locked if step in steps]
    if not recorded:
        return False
    start = locked.index(recorded[0])
    for step in locked[start:]:
        body = steps.get(step)
        if body is None:
            return True
        try:
            if mod.affected_drift(folder, step, body, steps):
                return True
        except (OSError, ValueError, KeyError):
            return True
    return False


def working_branch(folder: Path | None, root: str, hinted: str) -> str:
    """The build-walk branch. A base branch is used only when it is checked out."""
    hinted = (hinted or "").strip()
    head = _git_branch(Path(root) if root else folder)
    if not head and folder is not None:
        head = _git_branch(folder)
    names = progress_branches(folder)
    feature = [name for name in names if name not in BASE_BRANCHES]
    if hinted and hinted not in BASE_BRANCHES:
        return hinted
    if head and head not in BASE_BRANCHES:
        return head
    if feature:
        return feature[-1]
    if head in BASE_BRANCHES:
        return head
    if hinted in BASE_BRANCHES and head == hinted:
        return hinted
    return ""


def build(state: dict) -> dict:
    helper = _helper()
    card = helper.design_branch_card(state["root"]) if state.get("root") else None
    if state.get("failed"):
        return {"ending": "", "card": card, "switch_to_default": False}
    slug = str(state.get("slug") or "").strip()
    branch = str(state.get("branch") or "").strip()
    count = state.get("uncommitted") or None
    pr = state.get("pr")
    if state.get("walk") and slug:
        folder = spec_folder(str(state.get("root") or ""), slug)
        if spec_walk_unfinished(folder):
            ending = helper.compose(
                "The spec walk is not finished.",
                [("Resume the spec walk:", f"/crav1-tighten-and-plan-ready-to-build {slug}")],
                uncommitted=count)
            return {"ending": ending, "card": card, "switch_to_default": False}
        branch = working_branch(folder, str(state.get("root") or ""), branch)
        if branch:
            ending = helper.compose(
                "The build walk on this branch is not finished.",
                [(f"Continue the build walk on {branch}:", f"/crav1-build-walk {slug} {branch}")],
                uncommitted=count)
        else:
            ending = helper.compose(
                "The build walk is not finished.",
                [("Continue the build walk:", f"/crav1-build-walk {slug}")],
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
