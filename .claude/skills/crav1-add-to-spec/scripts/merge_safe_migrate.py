#!/usr/bin/env python3
"""One-go migration to the CRAV1 merge-safe formats (kit 1.84.0).

Rewrites every docs/**/spec.md and docs/system/repos.md once:
  - `Synced at: <repo> a@1, d; b@2, d` becomes one `Synced at:` line per repo
    and branch, sorted by repo, then branch.
  - the repos table's `Synced at` column moves into a `## Synced at` section
    right after the table: `- <repo> <branch>@<short sha>, <date>`, one bullet
    per repo and branch, sorted.
  - numbered or `Q<n>`-prefixed open questions become plain `- ` bullets.

Every line and every entry is kept. Before anything is written, a
nothing-lost check compares old and new; a file that would lose anything is
left alone and the run exits 2. A second run changes nothing. Line endings
are kept. Never commits.

Usage (from the product repo root, or pass --root):
    python3 merge_safe_migrate.py --dry-run   list what would change; write nothing
    python3 merge_safe_migrate.py             migrate
    python3 merge_safe_migrate.py --check     exit 1 when a file still needs it
    python3 merge_safe_migrate.py --selftest
Standard library only.
"""
import argparse, re, sys, tempfile
from collections import Counter
from pathlib import Path

SYNC = re.compile(r"^Synced at: (\S+) (.+?)\s*$")
ENTRY = re.compile(r"^(\S+)@([0-9a-f]{7,40}), (\d{4}-\d{2}-\d{2})( \(dropped\))?$")
QNUM = re.compile(r"^(?:\d+[.)]\s+)?(?:\*\*)?Q\d+[.:)]?(?:\*\*)?\s+(.*)$")
NUM = re.compile(r"^\d+[.)]\s+(.*)$")
OLD_NOTE = '`Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.'  # the 1.83 template paragraph, replaced only when unchanged
NEW_NOTE = ("`## Synced at` below holds one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, "
            "sorted by repo, then branch (1.84.0). A new read replaces only that repo and branch's line. "
            "A consumer measuring drift uses, for each repo and branch, the older of this line and the slice line; "
            "no line means unknown, so fall back to spec file commit dates.")


def entries(text):
    return [e.strip() for e in text.split(";") if e.strip()]


def key(repo, entry):
    return (repo.lower(), entry.split("@", 1)[0].lower(), entry)


def cell_repo(c):
    c = c.strip().strip("`")
    m = re.match(r"^\[([^\]]+)\]\([^)]*\)$", c)
    return (m.group(1) if m else c).strip("`").strip()


def split_row(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    return [c.strip() for c in s.strip("|").split("|")]


def migrate_spec(lines):
    out, i = [], 0
    in_q = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            in_q = ln.strip().lower() == "## open questions"
        if SYNC.match(ln):
            block = []
            while i < len(lines) and SYNC.match(lines[i]):
                m = SYNC.match(lines[i])
                block += [(m.group(1), e) for e in entries(m.group(2))]
                i += 1
            seen = []
            for r, e in sorted(block, key=lambda x: key(*x)):
                if (r, e) not in seen:
                    seen.append((r, e))
            out += ["Synced at: %s %s" % (r, e) for r, e in seen]
            continue
        if in_q and not ln.startswith((" ", "\t")):
            m = QNUM.match(ln[2:]) if ln.startswith("- ") else QNUM.match(ln)
            if m and (ln.startswith("- ") or NUM.match(ln) or ln.startswith("Q") or ln.startswith("**Q")):
                ln = "- " + m.group(1)
            else:
                n = NUM.match(ln)
                if n:
                    ln = "- " + n.group(1)
        out.append(ln)
        i += 1
    return out


def migrate_repos(lines):
    out, i, synced = [], 0, []
    table_end = None
    while i < len(lines):
        row = split_row(lines[i])
        if row and "Synced at" in row and i + 1 < len(lines) and split_row(lines[i + 1]) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            col = row.index("Synced at")
            rcol = row.index("Repo") if "Repo" in row else 0
            while i < len(lines) and split_row(lines[i]):
                cells = split_row(lines[i])
                if len(cells) > col:
                    if lines[i] is not None and i > 1 and not set(lines[i].replace("|", "").strip()) <= set("-: ") and cells[col] != "Synced at":
                        repo = cell_repo(cells[rcol]) if len(cells) > rcol else ""
                        for e in entries(cells[col]):
                            if repo:
                                synced.append((repo, e))
                    raw = lines[i].strip()[1:-1].split("|")
                    del raw[col]
                    out.append("|" + "|".join(raw) + "|")
                else:
                    out.append(lines[i])
                i += 1
            table_end = len(out)
            continue
        out.append(lines[i])
        i += 1
    # existing section
    start = None
    for j, ln in enumerate(out):
        if ln.strip() == "## Synced at":
            start = j
            break
    if start is not None:
        j = start + 1
        while j < len(out) and not out[j].startswith("## "):
            m = re.match(r"^- (\S+) (\S+@[0-9a-f]{7,40}, \d{4}-\d{2}-\d{2}.*?)\s*$", out[j])
            if m:
                synced.append((m.group(1), m.group(2)))
            j += 1
        del out[start:j]
        if table_end is not None and table_end > start:
            table_end -= (j - start)
    out = [NEW_NOTE if ln == OLD_NOTE else ln for ln in out]
    if not synced and start is None:
        return out
    seen = []
    for r, e in sorted(synced, key=lambda x: key(*x)):
        if (r, e) not in seen:
            seen.append((r, e))
    section = ["## Synced at", ""] + ["- %s %s" % (r, e) for r, e in seen] + ([""] if seen else [])
    if start is not None:
        pos = start
    elif table_end is not None:
        pos = table_end
        if pos < len(out) and out[pos].strip() == "":
            pos += 1
        # after the paragraphs that describe the table, before the next heading
        while pos < len(out) and not out[pos].startswith("## "):
            pos += 1
    else:
        pos = len(out)
    if pos > 0 and out[pos - 1].strip() != "":
        section = [""] + section
    return out[:pos] + section + out[pos:]


def items(lines, repos):
    """What must survive: every entry and every non-blank line, normalised."""
    c = Counter()
    in_q = False
    hdr = None
    for ln in lines:
        if ln.startswith("## "):
            in_q = ln.strip().lower() == "## open questions"
        m = SYNC.match(ln)
        if m:
            for e in entries(m.group(2)):
                c[("S", m.group(1), e)] += 1
            continue
        if repos:
            row = split_row(ln)
            if row is not None:
                if set(ln.replace("|", "").strip()) <= set("-: "):
                    continue
                if "Synced at" in row and "Repo" in row:
                    hdr = row
                if hdr and len(row) == len(hdr) and "Synced at" in hdr:
                    col, rcol = hdr.index("Synced at"), hdr.index("Repo")
                    if row is not hdr and row != hdr:
                        for e in entries(row[col]):
                            c[("S", cell_repo(row[rcol]), e)] += 1
                    row = row[:col] + row[col + 1:]
                c[("R", tuple(x for x in row if x))] += 1
                continue
            mm = re.match(r"^- (\S+) (\S+@[0-9a-f]{7,40}, \d{4}-\d{2}-\d{2}.*?)\s*$", ln)
            if mm:
                c[("S", mm.group(1), mm.group(2))] += 1
                continue
            if ln == OLD_NOTE or ln == NEW_NOTE or ln.strip() == "## Synced at":
                continue
        if not ln.strip():
            continue
        if in_q and not ln.startswith((" ", "\t")):
            t = ln[2:] if ln.startswith("- ") else ln
            q = QNUM.match(t) or NUM.match(t)
            if q and (ln.startswith("- ") and QNUM.match(t) or not ln.startswith("- ")):
                t = q.group(1)
            c[("Q", t.strip())] += 1
            continue
        c[("L", ln.rstrip())] += 1
    # duplicate entries collapse in the new format
    for k in list(c):
        if k[0] == "S":
            c[k] = 1
    return c


def process(path, repos):
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    trail = raw.endswith(("\n",))
    lines = raw.replace("\r\n", "\n").split("\n")
    if trail:
        lines = lines[:-1]
    new = migrate_repos(lines) if repos else migrate_spec(lines)
    lost = items(lines, repos) - items(new, repos)
    text = nl.join(new) + (nl if trail else "")
    return raw, text, lost


def targets(root):
    docs = root / "docs"
    fs = [(p, False) for p in sorted(docs.rglob("spec.md"))] if docs.exists() else []
    r = docs / "system" / "repos.md"
    if r.exists():
        fs.append((r, True))
    return fs


def run(root, write, check):
    changed, bad = [], []
    for p, repos in targets(root):
        old, new, lost = process(p, repos)
        if lost:
            bad.append((p, lost))
            continue
        if old != new:
            changed.append(p)
            if write:
                p.write_bytes(new.encode("utf-8"))
    for p, lost in bad:
        print("LOST %s: %s (left alone)" % (p.relative_to(root), ", ".join(map(str, list(lost)[:5]))))
    for p in changed:
        print(("migrated " if write else "would migrate ") + str(p.relative_to(root)))
    if not changed and not bad:
        print("already merge-safe: nothing to change")
    if bad:
        return 2
    if check and changed:
        return 1
    return 0


def selftest():
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        s = root / "docs" / "specs" / "pantry-orders"
        s.mkdir(parents=True)
        (root / "docs" / "system").mkdir(parents=True)
        spec = ("# Pantry orders\r\n\r\nSynced at: pantry-api feat/pantry-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15\r\n"
                "Synced at: pantry-web main@abc1234, 2026-10-07 (dropped)\r\n\r\n## What\r\n\r\nText.\r\n\r\n"
                "## Open questions\r\n\r\n1. Who approves a refund?\r\n   - Asked: 2026-10-20, mail to Vega. Question 1.\r\n"
                "- **Q2.** Is the cut-off local time?\r\n  - Blocks: T2\r\n- Plain one?\r\n")
        (s / "spec.md").write_bytes(spec.encode())
        repos = ("# Repos\n\n| Repo | Purpose | Status | URL | Synced at | Merges into | Work items go to |\n"
                 "| --- | --- | --- | --- | --- | --- | --- |\n"
                 "| pantry-api | API | exists | https://example.test/a | main@abc1234, 2026-10-07; develop@def5678, 2026-10-06 | develop | |\n"
                 "| pantry-web | Web | proposed | | | | |\n\n" +
                 OLD_NOTE + "\n\n"
                 "`Merges into` is the branch.\n\n## Boundaries\n\nNone.\n")
        (root / "docs" / "system" / "repos.md").write_text(repos)
        assert run(root, False, True) == 1
        assert run(root, True, False) == 0
        a = (s / "spec.md").read_bytes().decode()
        assert "\r\n" in a and "; " not in a.split("## What")[0], a
        assert "Synced at: pantry-api develop@00344be, 2026-10-15\r\nSynced at: pantry-api feat/pantry-retry@155b5c4, 2026-10-19\r\nSynced at: pantry-web main@abc1234, 2026-10-07 (dropped)" in a, a
        assert "- Who approves a refund?" in a and "- Is the cut-off local time?" in a and "  - Blocks: T2" in a, a
        r = (root / "docs" / "system" / "repos.md").read_text()
        assert "| Repo | Purpose | Status | URL | Merges into | Work items go to |" in r, r
        assert "## Synced at\n\n- pantry-api develop@def5678, 2026-10-06\n- pantry-api main@abc1234, 2026-10-07\n" in r, r
        assert r.index("\n## Synced at") < r.index("## Boundaries") and r.index("`Merges into` is") < r.index("\n## Synced at") and OLD_NOTE not in r, r
        first = (a, r)
        assert run(root, True, True) == 0
        assert ((s / "spec.md").read_bytes().decode(), (root / "docs" / "system" / "repos.md").read_text()) == first
        # a file that would lose a line is left alone
        _, _, lost = process(s / "spec.md", False)
        assert not lost
    print("selftest ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(Path(a.root).resolve(), not (a.dry_run or a.check), a.check)


if __name__ == "__main__":
    sys.exit(main())
