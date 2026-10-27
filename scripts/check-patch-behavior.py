#!/usr/bin/env python3
"""Warn when a patch release adds a behavior sentence to a skill (1.96.0).

A pull request is a patch when the version in
plugins/crav1/.cursor-plugin/plugin.json goes from X.Y.Z to X.Y.Z' with a
higher Z. For such a pull request, every added line in a skill's SKILL.md or
in a file under a skill's references/ (the .cursor/ source; the plugin and
.claude/ copies are generated from it) is split into sentences. A sentence
that holds never, always, stop or ask (and their -s/-ed/-ing forms) and that
appears nowhere in the base tree's SKILL.md, references/ files or crav1.mdc is
new behavior text, so the check prints a GitHub warning for it. A sentence
moved word for word from another skill file is not new and is not flagged.

This is a warning, not a failure: the author either bumps the minor version,
or says in the pull request body why the change is still a patch.

Usage: check-patch-behavior.py <base-ref> [<head-ref>]
"""
import json
import re
import subprocess
import sys

PLUGIN = "plugins/crav1/.cursor-plugin/plugin.json"
SKILL_FILE = re.compile(r"^\.cursor/skills/crav1/(?!crav1-docs/)[^/]+/(SKILL\.md|(.*/)?references/.+\.md)$")
CORPUS_EXTRA = {".cursor/rules/crav1.mdc"}
WORDS = re.compile(r"\b(never|always|stop(s|ped|ping)?|ask(s|ed|ing)?)\b", re.IGNORECASE)
SPLIT = re.compile(r"(?<=[.!?])\s+(?=[`*(\"'A-Z0-9])")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def version(ref):
    try:
        v = json.loads(git("show", f"{ref}:{PLUGIN}"))["version"]
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return None
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v)
    return tuple(int(x) for x in m.groups()) if m else None


def norm(s):
    s = re.sub(r"^\s*(?:[-*+]|\d+\.|#+|>)\s+", "", s)
    s = s.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def sentences(text):
    out = []
    for line in text.splitlines():
        for part in SPLIT.split(line):
            n = norm(part)
            if n:
                out.append((part.strip(), n))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    old, new = version(base), version(head)
    if not old or not new or new[:2] != old[:2] or new[2] <= old[2]:
        print("Not a patch release; nothing to check.")
        return
    mb = git("merge-base", base, head).strip()
    files = git("diff", "--name-only", f"{mb}...{head}").split()
    targets = [p for p in files if SKILL_FILE.match(p)]
    corpus = set()
    for p in git("ls-tree", "-r", "--name-only", mb).split():
        if SKILL_FILE.match(p) or p in CORPUS_EXTRA:
            corpus.update(n for _, n in sentences(git("show", f"{mb}:{p}")))
    flagged = 0
    vtxt = "%d.%d.%d -> %d.%d.%d" % (old + new)
    for p in targets:
        diff = git("diff", "-U0", f"{mb}...{head}", "--", p)
        line_no = 0
        for d in diff.splitlines():
            h = re.match(r"^@@ -\S+ \+(\d+)", d)
            if h:
                line_no = int(h.group(1))
                continue
            if d.startswith("+++"):
                continue
            if d.startswith("+"):
                for raw, n in sentences(d[1:]):
                    if WORDS.search(raw) and n not in corpus:
                        flagged += 1
                        short = raw if len(raw) <= 160 else raw[:157] + "..."
                        print(f"::warning file={p},line={line_no},title=Behavior sentence in a patch::"
                              f"Patch release {vtxt} adds: \"{short}\" Bump the minor version, "
                              "or say in the pull request body why this is still a patch.")
                line_no += 1
    if flagged:
        print(f"{flagged} new never/always/stop/ask sentence(s) in a patch release. "
              "Bump the minor version, or note in the pull request body why it is still a patch.")
    else:
        print(f"Patch release {vtxt}: no new never/always/stop/ask sentence in a SKILL.md or references/ file.")


if __name__ == "__main__":
    main()
