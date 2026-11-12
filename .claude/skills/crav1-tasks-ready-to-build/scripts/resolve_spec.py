#!/usr/bin/env python3
"""Resolve one spec folder from a name (1.136.0).

Exact folder first, then hyphen and space forms (`orders 1.0` matches
`orders-1-0`). If none, one unique match on a playbook basename the spec
names, the spec title, or a work-item name in spec.md. Several matches are
listed and the command stops. It does not search the rest of the tree.

Usage: resolve_spec.py <query> [--root docs/specs] [--json]
Standard library only. Reads spec.md under the root. Writes nothing.
"""
import json
import pathlib
import re
import sys

SKIP = {"_template", "retired"}
PLAYBOOK = re.compile(r"(?im)^(?:[-*]\s*)?Playbook:\s*`?([^`\n]+)")
TITLE = re.compile(r"(?m)^#\s+(.+?)\s*$")
WORK = re.compile(r"(?im)^(?:[-*]\s*)?Work item:\s*(.+?)\s*$")
ID_ONLY = re.compile(r"^(?:AB)?#?\d+$", re.I)


def _utf8_stdout():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()


def folder_names(scope):
    """Folder names a query may mean. Same forms as build_map.scope_folder_names."""
    text = (scope or "").strip().strip("/")
    if not text:
        return []
    low = text.lower()
    names = [text, low]
    spaced = re.sub(r"\s+", "-", low)
    kebab = re.sub(r"[^a-z0-9]+", "-", low).strip("-")
    for name in (spaced, kebab):
        if name and name not in names:
            names.append(name)
    return names


def norm(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def playbook_basenames(spec_text):
    names = []
    for match in PLAYBOOK.finditer(spec_text or ""):
        raw = match.group(1).strip().strip("`").strip()
        if not raw:
            continue
        stem = pathlib.PurePath(raw.replace("\\", "/")).stem
        if stem:
            names.append(stem)
    return names


def spec_title(spec_text):
    match = TITLE.search(spec_text or "")
    return match.group(1).strip() if match else ""


def work_item_names(spec_text):
    names = []
    for match in WORK.finditer(spec_text or ""):
        value = match.group(1).strip()
        name = value
        for sep in (" — ", " – ", " - "):
            if sep in value:
                name = value.split(sep, 1)[1].strip()
                break
        if name and not ID_ONLY.fullmatch(name):
            names.append(name)
    return names


def _specs(root):
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    found = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in SKIP:
            continue
        spec = child / "spec.md"
        if spec.is_file():
            found.append(child)
    return found


def resolve(root, query):
    """Return ok with one folder, or several/none and the matches."""
    query = (query or "").strip()
    folders = _specs(root)
    if not query:
        return {"ok": False, "code": "none", "matches": [], "query": query}
    direct = pathlib.Path(query)
    if direct.is_dir() and (direct / "spec.md").is_file() and direct.name not in SKIP:
        return {
            "ok": True,
            "code": "folder",
            "slug": direct.name,
            "folder": str(direct),
            "how": "folder",
            "matches": [{"slug": direct.name, "how": "folder"}],
        }
    names = set(folder_names(query))
    folder_hits = [child for child in folders if child.name in names or child.name.lower() in names]
    if len(folder_hits) == 1:
        child = folder_hits[0]
        return {
            "ok": True,
            "code": "folder",
            "slug": child.name,
            "folder": str(child),
            "how": "folder",
            "matches": [{"slug": child.name, "how": "folder"}],
        }
    if len(folder_hits) > 1:
        matches = [{"slug": child.name, "how": "folder"} for child in folder_hits]
        return {"ok": False, "code": "several", "matches": matches, "query": query}
    want = norm(query)
    hits = []
    for child in folders:
        text = (child / "spec.md").read_text(encoding="utf-8")
        reasons = []
        if any(norm(name) == want for name in playbook_basenames(text)):
            reasons.append("playbook")
        if norm(spec_title(text)) == want:
            reasons.append("title")
        if any(norm(name) == want for name in work_item_names(text)):
            reasons.append("work-item")
        if reasons:
            hits.append({"slug": child.name, "how": ", ".join(reasons), "folder": str(child)})
    if len(hits) == 1:
        hit = hits[0]
        return {
            "ok": True,
            "code": hit["how"],
            "slug": hit["slug"],
            "folder": hit["folder"],
            "how": hit["how"],
            "matches": [{"slug": hit["slug"], "how": hit["how"]}],
        }
    if len(hits) > 1:
        return {
            "ok": False,
            "code": "several",
            "matches": [{"slug": hit["slug"], "how": hit["how"]} for hit in hits],
            "query": query,
        }
    return {"ok": False, "code": "none", "matches": [], "query": query}


def render(result):
    if result.get("ok"):
        return result["folder"]
    if result.get("code") == "several":
        lines = [f"Several spec folders match {result.get('query', '')!r}. Stop."]
        for match in result.get("matches") or []:
            lines.append(f"- {match['slug']} ({match['how']})")
        return "\n".join(lines)
    return f"No spec folder matches {result.get('query', '')!r}."


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 0
    as_json = "--json" in argv
    args = [arg for arg in argv if arg != "--json"]
    root = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--root" and i + 1 < len(args):
            root = args[i + 1]
            i += 2
            continue
        positional.append(args[i])
        i += 1
    if len(positional) != 1 or root is None:
        sys.stdout.write("Usage: resolve_spec.py <query> --root <docs/specs> [--json]\n")
        return 2
    result = resolve(root, positional[0])
    if as_json:
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    else:
        text = render(result)
        sys.stdout.write(text + ("\n" if not text.endswith("\n") else ""))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
