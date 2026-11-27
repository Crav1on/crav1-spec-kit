#!/usr/bin/env python3
"""Maintainer dry run: try a kit pull request's update and ready check on a real project (1.199.0).

Hidden maintainer tool, not a skill; update_kit.py never copies it. Run it
from the project root:

    python -X utf8 kit_dry_run.py --pr 277 --spec "orders-api"
    python -X utf8 kit_dry_run.py --branch feat/kit-1199 --spec "orders-api"
    python -X utf8 kit_dry_run.py --pr 277 --spec "orders-api" --add codex

It shallow-clones the kit at that pull request or branch into a temp folder,
then dry-runs that head as if it were merged onto origin/main: a temporary
merge in a scratch worktree. A conflict falls back to the branch and names
the files that exist only on main, and those files are never reported as
deletes. A `--spec` placeholder or a name that matches no spec stops before
the update and lists the spec slugs. It adds a detached temporary git
worktree of this project at HEAD, runs the kit's own update_kit.py into the
worktree, then `walk_progress.py start` and `readiness --text` there (plus
any --extra), and prints one block between
`===== COPY FROM HERE =====` and `===== COPY TO HERE =====`. The block is
saved in the temp folder and copied to the clipboard when a clipboard tool
is there. The worktree and both temp folders are removed in a finally block.
It never commits, pushes or fetches into the project, and writes only under
the temp folder (git's own worktree bookkeeping is removed again).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.dont_write_bytecode = True  # before any sibling import; no __pycache__ in the project (1.121.1)


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
# Plain text on stderr. No ANSI: Windows PowerShell 5.1 does not need it.
STEP_DOT_SECONDS = 3.0


class Step:
    """One progress line on stderr. A dot every few seconds while the step runs."""

    def __init__(self, label: str, interval: float = STEP_DOT_SECONDS):
        self.label = label
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "Step":
        sys.stderr.write(self.label)
        sys.stderr.flush()

        def beat() -> None:
            while not self._stop.wait(self.interval):
                sys.stderr.write(".")
                sys.stderr.flush()

        self._thread = threading.Thread(target=beat, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> bool:
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        sys.stderr.write("\n")
        sys.stderr.flush()
        return False


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600, env_extra: dict | None = None) -> tuple[int, str]:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", GIT_TERMINAL_PROMPT="0")
    if env_extra:
        env.update(env_extra)
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
    steps = [GIT + ["init", "--quiet"], GIT + ["remote", "add", "origin", url],
             GIT + ["fetch", "--quiet", "--depth", "1", "origin", f"pull/{pr}/head"],
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
    body = f"$ update_kit.py {cmd} (exit {code})\n{kept}".rstrip()
    if cmd == "apply":
        line = _kit2_line(kept)
        if line:
            body += "\n" + line
    return body


def _kit2_line(text: str) -> str | None:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    line = data.get("kit2_line")
    return line if isinstance(line, str) and line else None


def _flags_api(kit: Path):
    for rel in (
        "plugins/crav1/skills/crav1-update-kit/scripts/flags.py",
        ".cursor/skills/crav1/crav1-update-kit/scripts/flags.py",
    ):
        path = kit / rel
        if path.is_file():
            spec = importlib.util.spec_from_file_location("crav1_dry_flags", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    return None


def flags_banner(repo: Path, kit: Path) -> str | None:
    """None when the project has no flag file, so the copy block stays as it is today."""
    if not (repo / ".crav1" / "flags.local.json").exists():
        return None
    module = _flags_api(kit)
    if module is None:
        return "Flags: none"
    return module.banner(repo)


def _item_path(item: object) -> str | None:
    if isinstance(item, dict):
        path = item.get("path")
        return path if isinstance(path, str) else None
    return item if isinstance(item, str) else None


def _drop_hidden(items: list, hide: set[str]) -> list:
    return [item for item in items if _item_path(item) not in hide]


def _scrub_deletes(text: str, hide: set[str]) -> str:
    """Files that exist only on main are not deletes of the pull request (1.209.0)."""
    if not hide:
        return text
    try:
        data = json.loads(text)
    except ValueError:
        return text
    if not isinstance(data, dict):
        return text
    files = data.get("files")
    if isinstance(files, dict) and isinstance(files.get("delete"), list):
        files["delete"] = _drop_hidden(files["delete"], hide)
    templates = data.get("templates")
    if isinstance(templates, dict) and isinstance(templates.get("delete"), list):
        templates["delete"] = _drop_hidden(templates["delete"], hide)
    if isinstance(data.get("delete"), list):
        data["delete"] = _drop_hidden(data["delete"], hide)
    if isinstance(data.get("touched"), list):
        data["touched"] = _drop_hidden(data["touched"], hide)
    return json.dumps(data)


def _resolve_mod():
    path = Path(__file__).resolve().parent.parent / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/resolve_spec.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("crav1_dry_resolve", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def available_specs(repo: Path) -> str:
    root = repo / "docs/specs"
    if not root.is_dir():
        return "(none)"
    slugs = [
        child.name for child in sorted(root.iterdir())
        if child.is_dir() and child.name not in {"_template", "retired"} and (child / "spec.md").is_file()
    ]
    return ", ".join(slugs) if slugs else "(none)"


def spec_problem(repo: Path, spec: str) -> str | None:
    """A placeholder or an unknown spec stops the dry run. None when one spec matches."""
    text = (spec or "").strip()
    slugs = available_specs(repo)
    if "<" in text and ">" in text:
        return f"--spec '{text}' is a placeholder. Pass a spec slug. Available specs: {slugs}."
    module = _resolve_mod()
    if module is None:
        names = {part.strip() for part in slugs.split(",")}
        return None if text in names else f"No spec named '{text}'. Available specs: {slugs}."
    query = text
    direct = Path(text)
    if not direct.is_absolute() and (repo / text).is_dir():
        query = str(repo / text)
    result = module.resolve(str(repo / "docs/specs"), query)
    if result.get("ok"):
        return None
    if result.get("code") == "several":
        names = ", ".join(item.get("slug") or "" for item in result.get("matches") or [])
        return f"--spec '{text}' matches more than one spec: {names}. Pass one slug."
    return f"No spec named '{text}'. Available specs: {slugs}."


def _fetch_main(kit: Path) -> str | None:
    """origin/main, else origin/master, deep enough that a merge-base exists."""
    fetched = None
    for name in ("main", "master"):
        # A single-branch clone does not create origin/main on its own.
        code, _out = run(GIT + ["-C", str(kit), "fetch", "--quiet", "origin", f"{name}:refs/remotes/origin/{name}"])
        if code == 0:
            fetched = name
            break
    if not fetched:
        return None
    ref = f"origin/{fetched}"
    for _ in range(6):
        code, _base = run(GIT + ["-C", str(kit), "merge-base", "HEAD", ref])
        if code == 0:
            return ref
        code, _out = run(GIT + ["-C", str(kit), "fetch", "--quiet", "--deepen=100", "origin",
                                f"{fetched}:refs/remotes/origin/{fetched}"])
        if code != 0:
            run(GIT + ["-C", str(kit), "fetch", "--quiet", "--unshallow", "origin"])
            break
    code, _base = run(GIT + ["-C", str(kit), "merge-base", "HEAD", ref])
    return ref if code == 0 else None


def _behind_count(kit: Path, ref: str) -> int:
    code, out = run(GIT + ["-C", str(kit), "rev-list", "--count", f"HEAD..{ref}"])
    if code != 0:
        return 0
    try:
        return int((out or "0").strip() or "0")
    except ValueError:
        return 0


def _main_only_files(kit: Path, ref: str) -> list[str]:
    """Paths added on main since this branch point. They are not pull-request deletes."""
    code, base = run(GIT + ["-C", str(kit), "merge-base", "HEAD", ref])
    if code != 0 or not base.strip():
        return []
    code, out = run(GIT + ["-C", str(kit), "diff", "--name-only", "--diff-filter=A", base.strip(), ref])
    if code != 0:
        return []
    return sorted({line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()})


def settle_onto_main(kit: Path, scratch: Path) -> tuple[Path, str | None, set[str]]:
    """Dry-run the pull request as if origin/main were merged in (1.209.0).

    A branch that already contains main is used as-is. Otherwise main is
    merged into a scratch worktree. A conflict keeps the branch, warns, and
    returns the files that exist only on main so they are not reported as deletes.
    """
    ref = _fetch_main(kit)
    if ref is None:
        return kit, None, set()
    behind = _behind_count(kit, ref)
    if behind == 0:
        return kit, None, set()
    only = _main_only_files(kit, ref)
    code, _out = run(GIT + ["-C", str(kit), "worktree", "add", "--detach", "--quiet", str(scratch), "HEAD"])
    if code != 0:
        word = "commit" if behind == 1 else "commits"
        warning = f"branch is behind main by {behind} {word}; these files come only from main: {', '.join(only)}"
        return kit, warning, set(only)
    code, _out = run(GIT + [
        "-C", str(scratch), "-c", "user.name=person A", "-c", "user.email=a@example.com",
        "merge", "--no-edit", ref,
    ])
    if code == 0:
        return scratch, None, set()
    run(GIT + ["-C", str(scratch), "merge", "--abort"])
    run(GIT + ["-C", str(kit), "worktree", "remove", "--force", str(scratch)])
    word = "commit" if behind == 1 else "commits"
    warning = f"branch is behind main by {behind} {word}; these files come only from main: {', '.join(only)}"
    return kit, warning, set(only)


def update_into(worktree: Path, kit: Path, tmp: Path, source: str | None, hide_deletes: set[str] | None = None) -> list[str]:
    """The PR kit's own update, the way /crav1-update-kit installs: detect, old release tree, plan, apply."""
    script = kit / UPDATE
    py = [sys.executable, "-X", "utf8", str(script)]
    dry = {"CRAV1_KIT2_DRY_RUN": "1"}
    lines = []
    with Step("update detect"):
        code, out = run(py + ["detect", "--root", str(worktree)], env_extra=dry)
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
    plan_cmd = ["plan", "--old", str(old), "--new", str(kit), "--to-version", target]
    with Step("update plan"):
        code, out = run(py + plan_cmd + ["--root", str(worktree)], env_extra=dry)
    out = _scrub_deletes(out, hide_deletes or set())
    lines.append(_summarise("plan", code, out))
    if code == 0:
        apply_cmd = ["apply", "--old", str(old), "--new", str(kit), "--yes"]
        with Step("update apply"):
            code, out = run(py + apply_cmd + ["--root", str(worktree)], env_extra=dry)
        out = _scrub_deletes(out, hide_deletes or set())
        lines.append(_summarise("apply", code, out))
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
        with Step(f"add vendor {name}"):
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
    with Step("walk_progress start"):
        code, out = run(py + [str(walk), "start", "--root", spec, "--skip-sync"], cwd=worktree)
    lines.append(f"$ walk_progress.py start --root \"{spec}\" --skip-sync (exit {code})\n{_quiet(out)}")
    folder = None
    try:
        folder = json.loads(out).get("folder")
    except ValueError:
        pass
    if folder:
        with Step("readiness"):
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
    problem = spec_problem(repo, args.spec)
    if problem:
        print(problem)
        return 2
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tmp_kit = Path(tempfile.mkdtemp(prefix="crk"))
    tmp_wt = Path(tempfile.mkdtemp(prefix="crw"))
    worktree = tmp_wt / "w"
    cleanup: list[str] = []
    before = snapshot(repo)
    added = False
    scratch_added = False
    block: list[str] = []
    started = time.monotonic()
    kit = tmp_kit / "k"
    scratch = tmp_kit / "merged"
    try:
        with Step("cloning kit"):
            ok, err = clone_kit(kit, args.kit_source, args.pr, args.branch)
        which_ref = f"PR {args.pr}" if args.pr else f"branch {args.branch}"
        if not ok:
            block = [f"Kit clone of {which_ref} failed:", err]
        else:
            kit_tree, warning, hide = settle_onto_main(kit, scratch)
            scratch_added = scratch.exists()
            _c, sha = run(["git", "-C", str(kit_tree), "rev-parse", "--short", "HEAD"])
            _c, head = run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"])
            block = [f"Kit: {kit_version(kit_tree)} at {sha} ({which_ref})", f"Project HEAD: {head}", f"Spec: {args.spec}"]
            if warning:
                block.append(warning)
            banner = flags_banner(repo, kit_tree)
            if banner:
                block.append(banner)
            block.append("")
            with Step("making temp worktree"):
                code, out = run(GIT + ["-C", str(repo), "worktree", "add", "--detach", "--quiet", str(worktree), "HEAD"])
            if code != 0:
                block.append(f"git worktree add failed:\n{out}")
            else:
                added = True
                module = _flags_api(kit_tree)
                if module is not None:
                    module.seed_worktree(repo, worktree)
                block += ["--- Update ---", *update_into(worktree, kit_tree, tmp_kit, args.kit_source, hide)]
                if args.add:
                    block += ["", "--- Add ---", *add_vendors(worktree, kit_tree, args.add)]
                block += ["", "--- Checks ---", *checks(worktree, kit_tree, args.spec, args.extra)]
    finally:
        with Step("cleanup"):
            if added:
                code, out = run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)])
                if code != 0:
                    cleanup.append(f"git worktree remove failed: {out}")
            if scratch_added and kit.exists():
                code, out = run(GIT + ["-C", str(kit), "worktree", "remove", "--force", str(scratch)])
                if code != 0 and scratch.exists():
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
    elapsed = round(time.monotonic() - started)
    sys.stderr.write(f"done ({elapsed} s)\n")
    sys.stderr.flush()
    return 1 if cleanup or changed else 0


if __name__ == "__main__":
    sys.exit(main())
