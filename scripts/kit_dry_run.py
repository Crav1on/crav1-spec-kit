#!/usr/bin/env python3
"""Maintainer dry run: try a kit pull request's update and ready check on a real project (1.199.0).

Hidden maintainer tool, not a skill; update_kit.py never copies it. Run it
from the project root:

    python -X utf8 kit_dry_run.py --pr 277 --spec "orders-api"
    python -X utf8 kit_dry_run.py --branch feat/kit-1199 --spec "orders-api"
    python -X utf8 kit_dry_run.py --pr 277 --spec "orders-api" --add codex

It shallow-clones the kit at that pull request or branch into a temp folder,
adds a detached temporary git worktree of this project at HEAD, runs the
kit's own update_kit.py into the worktree, then `walk_progress.py start` and
`readiness --text` there (plus any --extra), and prints one block between
`===== COPY FROM HERE =====` and `===== COPY TO HERE =====`. The block is
saved in the temp folder and copied to the clipboard when a clipboard tool
is there. The worktree and both temp folders are removed in a finally block.
It never commits, pushes or fetches into the project, and writes only under
the temp folder (git's own worktree bookkeeping is removed again).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


_utf8_stdout()

KIT_URL = "https://github.com/Crav1on/crav1-spec-kit.git"
FROM = "===== COPY FROM HERE ====="
TO = "===== COPY TO HERE ====="
UPDATE = "plugins/crav1/skills/crav1-update-kit/scripts/update_kit.py"
WALK = "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
GIT = ["git", "-c", "core.longpaths=true", "-c", "core.autocrlf=false"]


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", GIT_TERMINAL_PROMPT="0")
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, f"{type(exc).__name__}: {exc}"
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr and proc.stderr.strip() else "")
    return proc.returncode, out.strip()


def _source_url(source: str | None) -> str:
    if not source:
        return KIT_URL
    path = Path(source)
    return path.resolve().as_uri() if path.exists() else source


def clone_kit(dest: Path, source: str | None, pr: int | None, branch: str | None, ref: str | None = None) -> tuple[bool, str]:
    """Shallow clone of the kit at a branch, a tag (ref) or a GitHub pull request head."""
    url = _source_url(source)
    if branch or ref:
        code, out = run(GIT + ["clone", "--quiet", "--depth", "1", "--branch", branch or ref, url, str(dest)])
        return code == 0, out
    dest.mkdir(parents=True, exist_ok=True)
    steps = [GIT + ["init", "--quiet"], GIT + ["fetch", "--quiet", "--depth", "1", url, f"pull/{pr}/head"],
             GIT + ["checkout", "--quiet", "--detach", "FETCH_HEAD"]]
    for cmd in steps:
        code, out = run(cmd, cwd=dest)
        if code != 0:
            return False, out
    return True, ""


def kit_version(kit: Path) -> str:
    try:
        return json.loads((kit / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8")).get("version") or "?"
    except (OSError, ValueError):
        return "?"


def find_walk(worktree: Path, kit: Path) -> Path | None:
    for base in (worktree / ".cursor/skills/crav1", worktree / ".claude/skills", kit / ".cursor/skills/crav1"):
        if (base / WALK).is_file():
            return base / WALK
    return None


def find_script(name: str, worktree: Path, kit: Path) -> Path | None:
    for base in (worktree / ".cursor/skills/crav1", worktree / ".claude/skills", kit / ".cursor/skills/crav1"):
        if base.is_dir():
            for hit in sorted(base.rglob(name)):
                if hit.is_file():
                    return hit
    return None


def _quiet(text: str) -> str:
    """Drop the spurious no-upstream line. It is not a dry-run failure (1.200.0)."""
    return "\n".join(ln for ln in str(text or "").splitlines() if "no upstream" not in ln.lower())


_PLAN_KINDS = ("update", "add", "merge", "delete", "clash", "unchanged", "left_extra")
_PLAN_SAMPLES = ("update", "add", "merge", "delete", "clash")


def _plan_summary(code: int, text: str) -> str:
    """Counts by kind, then at most 10 changed paths (1.201.0). Unchanged stays a count."""
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    files = data.get("files") if isinstance(data, dict) else None
    if not isinstance(files, dict):
        head = "\n".join(text.splitlines()[:12])
        return f"$ update_kit.py plan (exit {code})\n{head}".rstrip()
    counts = []
    samples: list[str] = []
    changed = 0
    for kind in _PLAN_KINDS:
        items = files.get(kind) or []
        if not isinstance(items, list):
            items = []
        counts.append(f"{kind} {len(items)}")
        if kind not in _PLAN_SAMPLES:
            continue
        for item in items:
            path = item.get("path") if isinstance(item, dict) else item
            if not isinstance(path, str):
                continue
            changed += 1
            if len(samples) < 10:
                samples.append(path)
    body = ", ".join(counts)
    if samples:
        body += "\n" + "\n".join(samples)
    extra = changed - len(samples)
    if extra > 0:
        body += f"\n… and {extra} more"
    return f"$ update_kit.py plan (exit {code})\n{body}"


def _summarise(cmd: str, code: int, out: str) -> str:
    """Detect is mode and version. Plan is counts by kind. Apply keeps its exit line (1.200.0, 1.201.0)."""
    text = _quiet(out)
    if cmd == "detect":
        try:
            info = json.loads(text)
            return f"$ update_kit.py detect (exit {code})\nmode: {info.get('mode')}; version: {info.get('version')}"
        except ValueError:
            return f"$ update_kit.py detect (exit {code})\n{text}"
    if cmd == "plan":
        return _plan_summary(code, text)
    kept = text
    if "dry-run-marker.md" in out and "dry-run-marker.md" not in kept:
        kept = (kept + "\ndry-run-marker.md").strip()
    return f"$ update_kit.py {cmd} (exit {code})\n{kept}".rstrip()


def update_into(worktree: Path, kit: Path, tmp: Path, source: str | None) -> list[str]:
    """The PR kit's own update, the way /crav1-update-kit installs: detect, old release tree, plan, apply."""
    script = kit / UPDATE
    py = [sys.executable, "-X", "utf8", str(script)]
    lines = []
    code, out = run(py + ["detect", "--root", str(worktree)])
    lines.append(_summarise("detect", code, out))
    try:
        info = json.loads(out)
    except ValueError:
        return lines + ["Update skipped: detect did not return JSON."]
    if info.get("mode") != "drop-in":
        return lines + [f"Update skipped: install mode is {info.get('mode')}, not drop-in; the checks use the PR kit's own scripts."]
    installed = info.get("version")
    old = tmp / "o"
    ok, err = clone_kit(old, source, None, None, ref=f"v{installed}") if installed else (False, "no installed version")
    if not ok:
        return lines + [f"Update skipped: the installed release v{installed} could not be fetched: {err.splitlines()[-1] if err else ''}"]
    target = kit_version(kit)
    for cmd in (["plan", "--old", str(old), "--new", str(kit), "--to-version", target],
                ["apply", "--old", str(old), "--new", str(kit), "--yes"]):
        code, out = run(py + cmd + ["--root", str(worktree)])
        lines.append(_summarise(cmd[0], code, out))
        if code != 0:
            break
    return lines


def _vendor_row(kit: Path, name: str) -> dict:
    for rel in (
        "plugins/crav1/skills/crav1-update-kit/vendors.json",
        ".cursor/skills/crav1/crav1-update-kit/vendors.json",
    ):
        path = kit / rel
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}
            row = (data.get("vendors") or {}).get(name)
            return row if isinstance(row, dict) else {}
    return {}


def _skill_total(kit: Path) -> int:
    for rel in ("docs/reference/skills.yaml", ".cursor/skills/crav1/crav1-docs/reference/skills.yaml"):
        path = kit / rel
        if path.is_file():
            return len(re.findall(r"(?m)^- name: (crav1-[a-z0-9-]+)\s*$", path.read_text(encoding="utf-8")))
    return 0


def _command_only(worktree: Path, row: dict, name: str) -> int:
    folder = worktree / str(row.get("skills") or "")
    if not folder.is_dir():
        return 0
    if name == "codex":
        return sum(1 for path in folder.glob("*/agents/openai.yaml") if path.is_file())
    count = 0
    for skill in folder.glob("*/SKILL.md"):
        try:
            text = skill.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        if "disable-model-invocation: true" in head:
            count += 1
    return count


def add_vendors(worktree: Path, kit: Path, names: list[str]) -> list[str]:
    """plan --add and apply --add in the temp worktree, then vendors. The real repo is not this folder."""
    script = kit / UPDATE
    py = [sys.executable, "-X", "utf8", str(script)]
    lines: list[str] = []
    total = _skill_total(kit)
    for name in names:
        row = _vendor_row(kit, name)
        code, out = run(py + ["plan", "--add", name, "--root", str(worktree)])
        try:
            plan = json.loads(out)
        except ValueError:
            plan = {}
        item = {}
        if isinstance(plan, dict):
            vendors = plan.get("vendors") or []
            if vendors and isinstance(vendors[0], dict):
                item = vendors[0]
        if code == 0:
            code, applied = run(py + ["apply", "--add", name, "--yes", "--root", str(worktree)])
            if code != 0:
                out = applied
        folder = item.get("folder") or row.get("skills") or "(unknown)"
        extras = item.get("extras") if isinstance(item.get("extras"), list) else row.get("extras") or []
        extra_text = ", ".join(str(part) for part in extras) if extras else "none"
        present = 0
        if row.get("skills"):
            base = worktree / str(row["skills"])
            if base.is_dir():
                present = sum(1 for child in base.iterdir() if child.is_dir() and (child / "SKILL.md").is_file())
        untouched = item.get("project_untouched")
        lines += [
            f"--- Vendor {name} ---",
            f"folder: {folder}",
            f"skills: {present}/{total}",
            f"command-only: {_command_only(worktree, row, name)}",
            f"extras: {extra_text}",
            f"added: {len(item.get('added') or [])}, merged: {len(item.get('merged') or [])}, clash: {len(item.get('clash') or [])}",
            f"project_untouched: {str(untouched).lower() if untouched is not None else 'unknown'}",
        ]
        if isinstance(plan, dict) and plan.get("kit_json_op") and plan.get("kit_json_op") != "unchanged":
            after = plan.get("vendors_after") if isinstance(plan.get("vendors_after"), list) else []
            lines.append("kit.json: " + plan["kit_json_op"] + (" -> " + ", ".join(after) if after else ""))
        if item.get("note"):
            lines.append(str(item["note"]))
        if code != 0:
            lines.append(f"$ update_kit.py plan --add {name} (exit {code})\n{_quiet(out)}")
    code, out = run(py + ["vendors", "--root", str(worktree)])
    lines.append(f"$ update_kit.py vendors (exit {code})\n{_quiet(out)}")
    return lines


def checks(worktree: Path, kit: Path, spec: str, extras: list[str]) -> list[str]:
    walk = find_walk(worktree, kit)
    if walk is None:
        return ["walk_progress.py was not found in the worktree or the kit clone."]
    py = [sys.executable, "-X", "utf8"]
    lines = [f"Scripts from: {walk.relative_to(worktree) if worktree in walk.parents else 'the kit clone'}"]
    code, out = run(py + [str(walk), "start", "--root", spec, "--skip-sync"], cwd=worktree)
    lines.append(f"$ walk_progress.py start --root \"{spec}\" --skip-sync (exit {code})\n{_quiet(out)}")
    folder = None
    try:
        folder = json.loads(out).get("folder")
    except ValueError:
        pass
    if folder:
        code, out = run(py + [str(walk), "readiness", "--root", folder, "--text"], cwd=worktree)
        rel = os.path.relpath(folder, worktree)
        lines.append(f"$ walk_progress.py readiness --root {rel} --text (exit {code})\n{_quiet(out)}")
    else:
        lines.append("readiness skipped: start did not name a spec folder.")
    for extra in extras:
        parts = shlex.split(extra.replace("{folder}", folder or spec), posix=os.name != "nt")
        script = find_script(parts[0], worktree, kit) if parts else None
        if not script:
            lines.append(f"$ {extra}\nnot run: {parts[0] if parts else 'nothing'} was not found.")
            continue
        code, out = run(py + [str(script)] + parts[1:], cwd=worktree)
        lines.append(f"$ {extra} (exit {code})\n{_quiet(out)}")
    return lines


def snapshot(repo: Path) -> dict:
    """What the dry run must leave as it was: branch, HEAD, status, stashes, worktrees."""
    out = {}
    for key, cmd in (("branch", ["branch", "--show-current"]), ("HEAD", ["rev-parse", "HEAD"]),
                     ("status", ["status", "--porcelain"]), ("stash", ["stash", "list"]),
                     ("worktrees", ["worktree", "list", "--porcelain"])):
        _code, text = run(["git", "-C", str(repo)] + cmd)
        out[key] = text
    return out


def compare(before: dict, after: dict) -> list[str]:
    lines = []
    for key in before:
        if before[key] != after.get(key):
            lines.append(f"{key} before:\n{before[key] or '(empty)'}\n{key} after:\n{after.get(key) or '(empty)'}")
    return lines


def to_clipboard(text: str) -> str | None:
    if os.environ.get("CRAV1_DRY_RUN_NO_CLIPBOARD"):
        return None
    tools = [["clip.exe"], ["clip"], ["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"]]
    for tool in tools:
        if not shutil.which(tool[0]):
            continue
        try:
            data = text.encode("utf-16-le") if tool[0].startswith("clip") else text.encode("utf-8")
            subprocess.run(tool, input=data, check=True, timeout=20, capture_output=True)
            return tool[0]
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def _rm_readonly(func, path, _exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def remove_tree(path: Path) -> str | None:
    if not path.exists():
        return None
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_rm_readonly)
    else:
        shutil.rmtree(path, onerror=_rm_readonly)
    return f"could not delete {path}" if path.exists() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run a kit pull request's update and ready check in a temp worktree.")
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--pr", type=int, help="kit pull request number")
    which.add_argument("--branch", help="kit branch name")
    parser.add_argument("--spec", required=True, help="spec folder, slug or title, as /crav1-tighten-and-plan-ready-to-build takes it")
    parser.add_argument("--extra", action="append", default=[], help='another kit script and its args, e.g. "build_map.py --root {folder}"; repeatable')
    parser.add_argument("--add", action="append", default=[], help="after the update, plan and apply this vendor in the temp worktree; repeatable")
    parser.add_argument("--repo", default=".", help="the project root (default: current folder)")
    parser.add_argument("--kit-source", help=argparse.SUPPRESS)  # tests: a local kit repo instead of GitHub
    args = parser.parse_args(argv)

    code, top = run(["git", "-C", args.repo, "rev-parse", "--show-toplevel"])
    if code != 0:
        print(f"Not a git repository: {Path(args.repo).resolve()}")
        return 2
    repo = Path(top.splitlines()[-1].strip())
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tmp_kit = Path(tempfile.mkdtemp(prefix="crk"))
    tmp_wt = Path(tempfile.mkdtemp(prefix="crw"))
    worktree = tmp_wt / "w"
    cleanup: list[str] = []
    before = snapshot(repo)
    added = False
    block: list[str] = []
    try:
        ok, err = clone_kit(tmp_kit / "k", args.kit_source, args.pr, args.branch)
        kit = tmp_kit / "k"
        which_ref = f"PR {args.pr}" if args.pr else f"branch {args.branch}"
        if not ok:
            block = [f"Kit clone of {which_ref} failed:", err]
        else:
            _c, sha = run(["git", "-C", str(kit), "rev-parse", "--short", "HEAD"])
            _c, head = run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"])
            block = [f"Kit: {kit_version(kit)} at {sha} ({which_ref})", f"Project HEAD: {head}", f"Spec: {args.spec}", ""]
            code, out = run(GIT + ["-C", str(repo), "worktree", "add", "--detach", "--quiet", str(worktree), "HEAD"])
            if code != 0:
                block.append(f"git worktree add failed:\n{out}")
            else:
                added = True
                block += ["--- Update ---", *update_into(worktree, kit, tmp_kit, args.kit_source)]
                if args.add:
                    block += ["", "--- Add ---", *add_vendors(worktree, kit, args.add)]
                block += ["", "--- Checks ---", *checks(worktree, kit, args.spec, args.extra)]
    finally:
        if added:
            code, out = run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)])
            if code != 0:
                cleanup.append(f"git worktree remove failed: {out}")
        code, out = run(["git", "-C", str(repo), "worktree", "prune"])
        if code != 0:
            cleanup.append(f"git worktree prune failed: {out}")
        for folder in (tmp_wt, tmp_kit):
            problem = remove_tree(folder)
            if problem:
                cleanup.append(problem)
    changed = compare(before, snapshot(repo))
    repo_line = "Your repo: unchanged" if not changed else "!!!!! Your repo CHANGED: !!!!!\n" + "\n".join(changed)
    text = "\n".join([FROM, *block, "", "Cleanup: " + ("; ".join(cleanup) if cleanup else "worktree and temp folders removed"),
                      repo_line, TO])
    print(text)
    saved = Path(tempfile.gettempdir()) / f"crav1-dry-run-{args.pr or 'branch'}-{stamp}.txt"
    saved.write_text(text + "\n", encoding="utf-8")
    clip = to_clipboard(text)
    print(f"Saved to {saved}; " + (f"copied to the clipboard ({clip})." if clip else "not on the clipboard (no clipboard tool found)."))
    if cleanup:
        print("Cleanup failed: " + "; ".join(cleanup))
    if changed:
        print("Your repo CHANGED during the dry run; see the block above.")
    return 1 if cleanup or changed else 0


if __name__ == "__main__":
    sys.exit(main())
