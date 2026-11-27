#!/usr/bin/env python3
"""Settle pristine installed-kit copies during a merge (1.208.0).

Two kit updates on the same branch leave conflicts under the vendor trees
(``.cursor/``, ``.claude/``, ``.agents/``). When both sides are pristine
copies of published releases, this writes the newer release, including a
file that release adds or deletes, checks the tree matches that release,
runs ``nothing_lost.py``, and stages those paths.

A kit file that does not match its side's release is left as it is. The
report names only those files.

The merge commit is ``commit``. It uses ``git commit --no-edit --cleanup=strip``
(or an explicit stripped message when a sentence is appended) so git's
``# Conflicts:`` list never lands in the message.

Usage (JSON on stdout):
  kit_merge.py settle --root <repo> [--release <version>=<dir> ...] [--no-fetch]
  kit_merge.py commit --root <repo> [--append <sentence>]

``--release`` is the release tree ``update_kit.py fetch`` would clone.
With none, settle fetches the two published tags. ``--no-fetch`` refuses
a missing tree instead. Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()
sys.dont_write_bytecode = True


def emit(payload: dict, status: int) -> int:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return status


def git(root: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        input=input_text,
        check=False,
    )


def git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=False,
    )


def load_update_kit():
    """The update-kit module beside this skill. Its vendor table and newline compare."""
    skill = Path(__file__).resolve().parent.parent
    candidate = skill.parent / "crav1-update-kit" / "scripts" / "update_kit.py"
    if not candidate.is_file():
        raise RuntimeError(f"update_kit.py is not next to this skill ({candidate})")
    spec = importlib.util.spec_from_file_location("crav1_update_kit_merge", candidate)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def merge_in_progress(root: Path) -> bool:
    proc = git(root, "rev-parse", "--git-path", "MERGE_HEAD")
    if proc.returncode != 0:
        return False
    path = Path(proc.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def tree_bytes(root: Path, rev: str) -> dict[str, bytes]:
    listed = git_bytes(root, "ls-tree", "-r", "-z", rev)
    if listed.returncode != 0:
        return {}
    out: dict[str, bytes] = {}
    for entry in listed.stdout.split(b"\0"):
        if not entry or b"\t" not in entry:
            continue
        meta, path_b = entry.split(b"\t", 1)
        parts = meta.split(b" ")
        if len(parts) < 3 or parts[1] != b"blob":
            continue
        blob = git_bytes(root, "cat-file", "blob", parts[2].decode("ascii"))
        if blob.returncode != 0:
            continue
        out[path_b.decode("utf-8", "surrogateescape")] = blob.stdout
    return out


def unmerged(root: Path) -> list[str]:
    proc = git(root, "diff", "--name-only", "--diff-filter=U")
    if proc.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]


def text_of(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeError:
        return ""


def version_in_map(files: dict[str, bytes], uk) -> str | None:
    """One release number from the Kit version line, else the changelog heading."""
    found: list[str] = []
    for path, data in files.items():
        if "crav1-docs/" not in path.replace("\\", "/"):
            continue
        text = text_of(data)
        if not text:
            continue
        if path.endswith("workflow.md"):
            match = uk.KIT_VERSION_LINE.search(text)
        elif path.endswith("CHANGELOG.md"):
            match = uk.CHANGELOG_HEAD.search(text)
        else:
            continue
        if match:
            found.append(match.group(1))
    unique = set(found)
    if len(unique) == 1:
        return unique.pop()
    return None


def hosts_for_map(files: dict[str, bytes], uk) -> set[str]:
    rows = uk._vendor_rows()
    raw = files.get(".crav1/kit.json")
    if raw is not None:
        try:
            names = uk.parse_kit_json(raw)
        except uk.Refuse:
            names = []
        hosts = {name for name in names if isinstance(rows.get(name), dict) and rows[name].get("install")}
        if hosts:
            return hosts
    found = set()
    for name, row in rows.items():
        if isinstance(row, dict) and row.get("install") and row.get("marker") in files:
            found.add(name)
    return found


def kit_paths(files: dict[str, bytes], hosts: set[str], uk) -> dict[str, bytes]:
    if not hosts:
        return {}
    return {path: data for path, data in files.items() if uk.is_kit_path(path, hosts)}


def differing(side: dict[str, bytes], release: dict[str, bytes], hosts: set[str], uk) -> list[str]:
    """Kit paths whose bytes are not that release, newline-normalized."""
    bad = []
    paths = set(side) | set(release)
    for path in sorted(paths):
        if not uk.is_kit_path(path, hosts):
            continue
        if uk._normalize_newlines(side.get(path)) != uk._normalize_newlines(release.get(path)):
            bad.append(path)
    return bad


def parse_releases(items: list[str]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Refused: --release {item} must be version=dir")
        version, raw = item.split("=", 1)
        key = version.strip().lstrip("v")
        if not key:
            raise ValueError(f"Refused: --release {item} has no version")
        found[key] = Path(raw).resolve()
    return found


def release_tree(version: str, releases: dict[str, Path], fetch: bool, uk) -> Path:
    key = version.lstrip("v")
    if key in releases:
        path = releases[key]
        if not path.is_dir():
            raise FileNotFoundError(f"Refused: release tree {path} is not a directory")
        return path
    if not fetch:
        raise FileNotFoundError(f"Refused: no --release tree for v{key}")
    try:
        return uk.fetch_release("v" + key, None, uk.KIT_REPO)
    except uk.Refuse as exc:
        raise FileNotFoundError(exc.message) from exc


def payload_for(path: str, release_bytes: bytes, newer: dict[str, bytes], uk) -> bytes:
    side = newer.get(path)
    if side is not None and uk._normalize_newlines(side) == uk._normalize_newlines(release_bytes):
        return side
    style = uk._newline_style(side) or uk._newline_style(release_bytes) or "lf"
    if style not in {"lf", "crlf"}:
        style = "lf"
    return uk._restyle(release_bytes, style) or release_bytes


def run_nothing_lost(root: Path) -> dict:
    script = Path(__file__).resolve().parent / "nothing_lost.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"nothing_lost": False, "message": (proc.stdout or proc.stderr or "").strip()}
    if not isinstance(payload, dict):
        payload = {"nothing_lost": False}
    payload["exit"] = proc.returncode
    return payload


def settle(root: Path, releases: dict[str, Path], fetch: bool) -> dict:
    root = root.resolve()
    if not merge_in_progress(root):
        return {
            "ok": False,
            "settled": False,
            "code": "not-a-merge",
            "line": "No merge is in progress.",
            "files": [],
        }
    uk = load_update_kit()
    ours_all = tree_bytes(root, "HEAD")
    theirs_all = tree_bytes(root, "MERGE_HEAD")
    ours_hosts = hosts_for_map(ours_all, uk)
    theirs_hosts = hosts_for_map(theirs_all, uk)
    union = ours_hosts | theirs_hosts
    ours = kit_paths(ours_all, union, uk)
    theirs = kit_paths(theirs_all, union, uk)
    conflicts = unmerged(root)
    kit_conflicts = [path for path in conflicts if union and uk.is_kit_path(path, union)]
    other = [path for path in conflicts if path not in kit_conflicts]
    ours_ver = version_in_map(ours, uk)
    theirs_ver = version_in_map(theirs, uk)
    if not ours_ver or not theirs_ver:
        named = kit_conflicts or sorted(set(ours) | set(theirs))
        return {
            "ok": False,
            "settled": False,
            "code": "no-version",
            "line": "Kit copies have no single release version. Left for you.",
            "files": named,
            "other_conflicts": other,
        }
    if uk.version_key(ours_ver) >= uk.version_key(theirs_ver):
        newer_ver, newer, newer_hosts = ours_ver, ours, ours_hosts
    else:
        newer_ver, newer, newer_hosts = theirs_ver, theirs, theirs_hosts
    if ours_ver == theirs_ver and not kit_conflicts:
        return {
            "ok": True,
            "settled": False,
            "code": "same-version",
            "version": newer_ver,
            "line": f"Kit copies already match v{newer_ver}.",
            "files": [],
            "other_conflicts": other,
        }
    try:
        ours_release = release_tree(ours_ver, releases, fetch, uk)
        theirs_release = release_tree(theirs_ver, releases, fetch, uk)
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "settled": False,
            "code": "no-release",
            "line": str(exc),
            "files": kit_conflicts,
            "other_conflicts": other,
        }
    ours_expected = uk.collect_kit(ours_release, ours_hosts, release=True) if ours_hosts else {}
    theirs_expected = uk.collect_kit(theirs_release, theirs_hosts, release=True) if theirs_hosts else {}
    edited = sorted(
        set(differing(kit_paths(ours_all, ours_hosts, uk), ours_expected, ours_hosts, uk))
        | set(differing(kit_paths(theirs_all, theirs_hosts, uk), theirs_expected, theirs_hosts, uk))
    )
    if edited:
        return {
            "ok": False,
            "settled": False,
            "code": "hand-edited",
            "version": newer_ver,
            "line": "Kit file edited by hand: " + ", ".join(edited) + ". Left for you.",
            "files": edited,
            "other_conflicts": other,
        }
    desired_src = uk.collect_kit(release_tree(newer_ver, releases, fetch, uk), newer_hosts, release=True)
    desired = {path: payload_for(path, data, newer, uk) for path, data in desired_src.items()}
    remove = sorted((set(ours) | set(theirs)) - set(desired))
    added = sorted(path for path in desired if path not in ours_all)
    deleted = [path for path in remove if path in ours_all or path in theirs_all]
    for path, data in desired.items():
        dest = root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    for path in remove:
        dest = root / path
        if dest.is_file() or dest.is_symlink():
            dest.unlink()
    mismatch = []
    for path, data in sorted(desired.items()):
        actual = (root / path).read_bytes() if (root / path).is_file() else None
        if uk._normalize_newlines(actual) != uk._normalize_newlines(data):
            mismatch.append(path)
    for path in remove:
        if (root / path).exists():
            mismatch.append(path)
    if mismatch:
        return {
            "ok": False,
            "settled": False,
            "code": "mismatch",
            "version": newer_ver,
            "line": "Settled kit copies do not match v" + newer_ver + ".",
            "files": mismatch,
            "other_conflicts": other,
        }
    stage = sorted(desired)
    if stage:
        added_proc = git(root, "add", "--", *stage)
        if added_proc.returncode != 0:
            return {
                "ok": False,
                "settled": False,
                "code": "stage",
                "line": (added_proc.stderr or added_proc.stdout or "git add failed").strip(),
                "files": stage,
                "other_conflicts": other,
            }
    if deleted:
        removed_proc = git(root, "rm", "-f", "--ignore-unmatch", "--", *deleted)
        if removed_proc.returncode != 0:
            return {
                "ok": False,
                "settled": False,
                "code": "stage",
                "line": (removed_proc.stderr or removed_proc.stdout or "git rm failed").strip(),
                "files": deleted,
                "other_conflicts": other,
            }
    lost = run_nothing_lost(root)
    nothing = bool(lost.get("nothing_lost"))
    counts = []
    written_n = len(desired) - len(added)
    if written_n:
        counts.append(f"{written_n} written")
    if added:
        counts.append(f"{len(added)} added")
    if deleted:
        counts.append(f"{len(deleted)} deleted")
    detail = f" ({', '.join(counts)})" if counts else ""
    tail = "Nothing lost." if nothing else "Lines lost."
    return {
        "ok": nothing,
        "settled": True,
        "code": "settled" if nothing else "lines-lost",
        "version": newer_ver,
        "written": written_n,
        "added": added,
        "deleted": deleted,
        "nothing_lost": nothing,
        "line": f"Settled kit copies to v{newer_ver}{detail}. {tail}",
        "files": [],
        "other_conflicts": [path for path in unmerged(root) if not (union and uk.is_kit_path(path, union))],
    }


def cleaned_message(root: Path, append: str | None) -> str:
    proc = git(root, "rev-parse", "--git-path", "MERGE_MSG")
    path = Path(proc.stdout.strip())
    if not path.is_absolute():
        path = root / path
    raw = path.read_text(encoding="utf-8")
    stripped = git(root, "stripspace", "--strip-comments", input_text=raw)
    body = (stripped.stdout if stripped.returncode == 0 else raw).rstrip() + "\n"
    sentence = (append or "").strip()
    if sentence and sentence not in body:
        body = body.rstrip() + "\n\n" + sentence + "\n"
    return body


def commit_merge(root: Path, append: str | None) -> dict:
    """Commit the merge. ``# Conflicts:`` comments are stripped.

    With no append sentence this is ``git commit --no-edit --cleanup=strip``.
    With a sentence, the message is that stripped text plus the sentence.
    """
    root = root.resolve()
    if not merge_in_progress(root):
        return {"ok": False, "code": "not-a-merge", "line": "No merge is in progress."}
    sentence = (append or "").strip()
    if sentence:
        body = cleaned_message(root, sentence)
        located = git(root, "rev-parse", "--git-path", "KIT_MERGE_MSG")
        message_file = Path(located.stdout.strip()) if located.returncode == 0 else root / ".git" / "KIT_MERGE_MSG"
        if not message_file.is_absolute():
            message_file = root / message_file
        message_file.write_text(body, encoding="utf-8")
        proc = git(root, "commit", "--cleanup=strip", "-F", str(message_file))
    else:
        proc = git(root, "commit", "--no-edit", "--cleanup=strip")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "git commit failed").strip()
        return {"ok": False, "code": "commit", "line": detail}
    message = git(root, "log", "-1", "--format=%B").stdout
    if "# Conflicts:" in message:
        return {
            "ok": False,
            "code": "conflicts-comment",
            "line": "The merge message still contains # Conflicts:.",
            "message": message,
        }
    return {"ok": True, "code": "committed", "line": "Committed the merge.", "message": message}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Settle pristine kit copies during a merge.")
    parser.add_argument("command", choices=["settle", "commit"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--release", action="append", default=[], help="version=dir, repeatable")
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--append", default=None)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "commit":
            payload = commit_merge(root, args.append)
            status = 0 if payload.get("ok") else (2 if payload.get("code") == "not-a-merge" else 1)
            return emit(payload, status)
        releases = parse_releases(args.release)
        payload = settle(root, releases, fetch=not args.no_fetch)
    except ValueError as exc:
        return emit({"ok": False, "settled": False, "code": "usage", "line": str(exc), "files": []}, 2)
    status = 0 if payload.get("ok") else (2 if payload.get("code") == "not-a-merge" else 1)
    return emit(payload, status)


if __name__ == "__main__":
    sys.exit(main())
