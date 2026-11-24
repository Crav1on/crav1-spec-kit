#!/usr/bin/env python3
"""Copy a filled playbook into docs/playbooks on apply (kit 1.120.0).

The first report stays outside the project. This script runs only when
/crav1-resolve-open-questions apply is writing a filled playbook. It does
not edit Answer or Change lines. It does not create a git commit.

Same playbook, in order:
  1. A `Docs path: docs/playbooks/<topic>.md` line in the file. The name
     stays that path.
  2. Otherwise the one file under docs/playbooks/ whose title subject
     matches. The subject is the H1 with a trailing ": playbook" removed.

A file with no filled Answer or Change line outside a code fence is a
draft and is not copied. A later apply overwrites the same file. When
the committed file's `Applied as:` hash does not match its other lines,
the file was edited in the repo: write refuses until --overwrite.

Usage (JSON on stdout):
  playbook_store.py name --subject "CC Process 1.0"
  playbook_store.py prepare --repo <root> --playbook <file>
  playbook_store.py write --repo <root> --playbook <file> --yes
      [--name <kebab>.md] [--overwrite] [--spec <file> ...]

write without --yes writes nothing and exits 2.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
DOCS_LINE_RE = re.compile(r"^Docs path: (docs/playbooks/[a-z0-9]+(?:-[a-z0-9]+)*\.md)$", re.M)
APPLIED_LINE_RE = re.compile(r"^Applied as: ([0-9a-f]{12})$", re.M)
FENCE_RE = re.compile(r"(?ms)^```.*?^```")
ANSWER_RE = re.compile(r"(?m)^[ \t]*(?:[-*][ \t]+)?(?:[NC]\d+[ \t]+)?Answer:[ \t]*(.*)$")
CHANGE_RE = re.compile(r"(?m)^[ \t]*(?:[-*][ \t]+)?(?:K\d+[ \t]+)?Change:[ \t]*(.*)$")
PLAYBOOK_LINK_RE = re.compile(r"^Playbook: .*$", re.M)


def fail(code: str, message: str, status: int = 1, **extra) -> None:
    payload = {"ok": False, "code": code, "message": message}
    payload.update(extra)
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def file_name_for(subject: str) -> str:
    """Lowercase kebab-case file name. 'CC Process 1.0' -> cc-process-1-0.md."""
    text = subject.strip()
    text = re.sub(r"\s*:\s*playbook\s*$", "", text, flags=re.I)
    slug = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    if not slug:
        slug = "playbook"
    return f"{slug}.md"


def safe_name(name: str) -> str | None:
    cleaned = name.strip()
    if "/" in cleaned or "\\" in cleaned or cleaned.startswith("."):
        return None
    if not NAME_RE.fullmatch(cleaned):
        return None
    return cleaned


def subject_of(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"\s*:\s*playbook\s*$", "", title, flags=re.I).strip()
    return ""


def norm_subject(subject: str) -> str:
    return re.sub(r"\s+", " ", subject.strip()).casefold()


def visible(text: str) -> str:
    return FENCE_RE.sub("", text)


def is_draft(text: str) -> bool:
    """No filled Answer or Change line outside a code fence."""
    shown = visible(text)
    if any(item.strip() for item in ANSWER_RE.findall(shown)):
        return False
    if any(item.strip() for item in CHANGE_RE.findall(shown)):
        return False
    return True


def docs_path_of(text: str) -> str | None:
    found = DOCS_LINE_RE.findall(text)
    return found[-1] if found else None


def applied_of(text: str) -> str | None:
    found = APPLIED_LINE_RE.findall(text)
    return found[-1] if found else None


def strip_stamps(text: str) -> str:
    text = re.sub(r"^Docs path: docs/playbooks/[a-z0-9]+(?:-[a-z0-9]+)*\.md\n", "", text, flags=re.M)
    text = re.sub(r"^Applied as: [0-9a-f]{12}\n", "", text, flags=re.M)
    return text


def content_hash(text: str) -> str:
    """Hash of the file with the Applied as line removed."""
    body = re.sub(r"^Applied as: [0-9a-f]{12}\n", "", text, flags=re.M)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def stamp(text: str, rel: str) -> str:
    """Add Docs path, then Applied as for the file with that line and no Applied as line."""
    body = strip_stamps(text)
    if not body.endswith("\n"):
        body += "\n"
    with_docs = _with_docs(body, rel)
    return _with_applied(with_docs, content_hash(with_docs))


def _with_docs(body: str, rel: str) -> str:
    line = f"Docs path: {rel}\n"
    lines = body.splitlines(keepends=True)
    if not lines:
        return line
    for index, raw in enumerate(lines):
        if raw.startswith("Report:"):
            lines.insert(index + 1, line)
            return "".join(lines)
    for index, raw in enumerate(lines):
        if raw.startswith("# "):
            lines.insert(index + 1, line)
            return "".join(lines)
    return line + body


def _with_applied(text: str, hashed: str) -> str:
    line = f"Applied as: {hashed}\n"
    lines = text.splitlines(keepends=True)
    for index, raw in enumerate(lines):
        if raw.startswith("Docs path:"):
            lines.insert(index + 1, line)
            return "".join(lines)
    return line + text


def edited_since_apply(text: str) -> bool:
    recorded = applied_of(text)
    if recorded is None:
        return True
    return recorded != content_hash(text)


def unified_diff(current: str, proposed: str, rel: str) -> str:
    import difflib

    diff = difflib.unified_diff(
        current.splitlines(),
        proposed.splitlines(),
        fromfile=f"{rel} (in the repo)",
        tofile=f"{rel} (this apply)",
        lineterm="",
    )
    lines = list(diff)
    if len(lines) > 200:
        lines = lines[:200] + ["... diff truncated ..."]
    return "\n".join(lines)


def playbook_dir(repo: Path) -> Path:
    return repo / "docs" / "playbooks"


def list_playbooks(repo: Path) -> list[Path]:
    folder = playbook_dir(repo)
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.glob("*.md") if path.is_file())


def subject_matches(repo: Path, subject: str) -> list[Path]:
    wanted = norm_subject(subject)
    if not wanted:
        return []
    found = []
    for path in list_playbooks(repo):
        try:
            title = subject_of(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        if norm_subject(title) == wanted:
            found.append(path)
    return found


def repo_of(spec_root: Path) -> Path | None:
    """Product root that holds docs/, starting from a spec folder."""
    for base in [spec_root, *spec_root.parents]:
        docs = base / "docs"
        if (docs / "specs").is_dir() or (docs / "playbooks").is_dir():
            return base
        if base.name == "docs":
            return base.parent
        if str(base) == "/":
            break
    return None


def identify(repo: Path, text: str) -> dict:
    """Decide the committed path. Does not write."""
    subject = subject_of(text)
    name = file_name_for(subject)
    rel_from_line = docs_path_of(text)
    if rel_from_line:
        return {
            "action": "fixed",
            "rel": rel_from_line,
            "name": Path(rel_from_line).name,
            "recognized": "docs-path",
            "subject": subject,
            "matches": [],
        }
    matches = subject_matches(repo, subject)
    if len(matches) > 1:
        rels = [path.relative_to(repo).as_posix() for path in matches]
        return {
            "action": "several",
            "rel": None,
            "name": name,
            "recognized": "subject",
            "subject": subject,
            "matches": rels,
        }
    if len(matches) == 1:
        rel = matches[0].relative_to(repo).as_posix()
        return {
            "action": "fixed",
            "rel": rel,
            "name": matches[0].name,
            "recognized": "subject",
            "subject": subject,
            "matches": [rel],
        }
    rel = f"docs/playbooks/{name}"
    taken = repo / rel
    if taken.is_file():
        return {
            "action": "name-taken",
            "rel": rel,
            "name": name,
            "recognized": None,
            "subject": subject,
            "matches": [rel],
        }
    return {
        "action": "propose-name",
        "rel": rel,
        "name": name,
        "recognized": None,
        "subject": subject,
        "matches": [],
    }


def read_playbook(path: Path) -> str:
    if not path.is_file():
        fail("playbook", f"not a file: {path}")
    return path.read_text(encoding="utf-8")


def propose_payload(ident: dict, edited: bool = False, diff: str = "") -> dict:
    action = ident["action"]
    if action == "fixed":
        action = "ask-overwrite" if edited else "write"
    payload = {
        "ok": True,
        "action": action,
        "path": ident["rel"],
        "name": ident["name"],
        "recognized": ident["recognized"],
        "subject": ident["subject"],
        "edited": edited,
        "matches": ident["matches"],
    }
    if diff:
        payload["diff"] = diff
    return payload


def prepare(args: argparse.Namespace) -> None:
    repo = Path(args.repo)
    text = read_playbook(Path(args.playbook))
    if is_draft(text):
        emit({
            "ok": True,
            "action": "draft",
            "path": None,
            "name": file_name_for(subject_of(text)),
            "recognized": None,
            "subject": subject_of(text),
            "edited": False,
            "message": "No filled Answer or Change line. A draft is not copied.",
        })
        return
    if not repo.is_dir():
        fail("repo", f"not a folder: {repo}")
    ident = identify(repo, text)
    edited = False
    diff = ""
    if ident["action"] == "fixed" and ident["rel"]:
        current_path = repo / ident["rel"]
        if current_path.is_file():
            current = current_path.read_text(encoding="utf-8")
            if edited_since_apply(current):
                edited = True
                proposed = stamp(text, ident["rel"])
                diff = unified_diff(current, proposed, ident["rel"])
    emit(propose_payload(ident, edited, diff))


def link_spec(text: str, rel: str) -> str:
    line = f"Playbook: {rel}"
    kept = [raw for raw in text.splitlines() if not raw.startswith("Playbook: ")]
    out: list[str] = []
    inserted = False
    for raw in kept:
        out.append(raw)
        if not inserted and raw.startswith("# "):
            out.append(line)
            inserted = True
    if not inserted:
        out.insert(0, line)
    return "\n".join(out).rstrip() + "\n"


def write(args: argparse.Namespace) -> None:
    if not args.yes:
        fail("needs-yes", "write copies the playbook only with --yes", status=2)
    repo = Path(args.repo)
    if not repo.is_dir():
        fail("repo", f"not a folder: {repo}")
    source = Path(args.playbook)
    text = read_playbook(source)
    if is_draft(text):
        fail("draft", "No filled Answer or Change line. A draft is not copied.", status=2)
    ident = identify(repo, text)
    if ident["action"] == "several":
        fail(
            "several",
            "More than one committed playbook has this subject. Do not guess.",
            status=2,
            matches=ident["matches"],
        )
    name_fixed = False
    if ident["action"] == "fixed":
        rel = ident["rel"]
        if args.name and safe_name(args.name) and safe_name(args.name) != ident["name"]:
            name_fixed = True
    elif ident["action"] in ("propose-name", "name-taken"):
        if not args.name:
            fail(
                "needs-name",
                f"Show the name once and pass it as --name. Proposed: {ident['name']}",
                status=2,
                name=ident["name"],
                path=ident["rel"],
            )
        chosen = safe_name(args.name)
        if chosen is None:
            fail("bad-name", "The name is lowercase kebab-case and ends in .md.", status=2, name=args.name)
        rel = f"docs/playbooks/{chosen}"
        existing = repo / rel
        if existing.is_file():
            existing_subject = norm_subject(subject_of(existing.read_text(encoding="utf-8")))
            if existing_subject and existing_subject != norm_subject(subject_of(text)):
                fail(
                    "name-taken",
                    f"{rel} is a different playbook. Pick another name.",
                    status=2,
                    path=rel,
                )
    else:
        fail("playbook", f"cannot place this playbook ({ident['action']})")
        return

    target = repo / rel
    if target.is_file() and edited_since_apply(target.read_text(encoding="utf-8")) and not args.overwrite:
        current = target.read_text(encoding="utf-8")
        proposed = stamp(text, rel)
        fail(
            "edited",
            "The committed playbook was edited in the repo since the last apply. Show the diff and pass --overwrite after a yes.",
            status=2,
            path=rel,
            diff=unified_diff(current, proposed, rel),
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    written = stamp(text, rel)
    target.write_text(written, encoding="utf-8")
    linked = []
    for spec in args.spec or []:
        spec_path = Path(spec)
        if not spec_path.is_file():
            fail("spec", f"not a file: {spec_path}")
        spec_path.write_text(link_spec(spec_path.read_text(encoding="utf-8"), rel), encoding="utf-8")
        linked.append(str(spec_path))
    emit({
        "ok": True,
        "action": "wrote",
        "path": rel,
        "name": Path(rel).name,
        "recognized": ident["recognized"],
        "name_fixed": name_fixed,
        "applied_as": applied_of(written),
        "specs": linked,
    })


def recorded_playbook(spec_root: Path, playbook: Path) -> tuple[str, Path]:
    """Path to store in walk-progress, and the file whose bytes are the version.

    A committed playbook is stored as docs/playbooks/<topic>.md. A file that
    is not one stays as the path that was passed, so older progress files
    keep working.
    """
    given = playbook
    repo = repo_of(spec_root)
    if not given.is_file() and repo is not None:
        candidate = repo / playbook
        if candidate.is_file():
            given = candidate
    if not given.is_file():
        return str(playbook), playbook
    if repo is None:
        return str(playbook), given
    text = given.read_text(encoding="utf-8")
    ident = identify(repo, text)
    if ident["action"] == "fixed" and ident["rel"]:
        committed = repo / ident["rel"]
        if committed.is_file():
            return ident["rel"], committed
    try:
        rel = given.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        rel = ""
    if rel.startswith("docs/playbooks/") and rel.endswith(".md"):
        return rel, given
    return str(playbook), given


def cmd_name(args: argparse.Namespace) -> None:
    name = file_name_for(args.subject)
    emit({"ok": True, "name": name, "path": f"docs/playbooks/{name}", "subject": args.subject})


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Copy a filled playbook into docs/playbooks")
    sub = parser.add_subparsers(dest="cmd", required=True)

    name = sub.add_parser("name")
    name.add_argument("--subject", required=True)
    name.set_defaults(func=cmd_name)

    prep = sub.add_parser("prepare")
    prep.add_argument("--repo", required=True)
    prep.add_argument("--playbook", required=True)
    prep.set_defaults(func=prepare)

    stored = sub.add_parser("write")
    stored.add_argument("--repo", required=True)
    stored.add_argument("--playbook", required=True)
    stored.add_argument("--name")
    stored.add_argument("--overwrite", action="store_true")
    stored.add_argument("--spec", action="append")
    stored.add_argument("--yes", action="store_true")
    stored.set_defaults(func=write)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
