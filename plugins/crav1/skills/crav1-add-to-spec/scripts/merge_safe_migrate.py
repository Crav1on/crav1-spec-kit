#!/usr/bin/env python3
"""One-go migration to the CRAV1 merge-safe formats (kit 1.84.0; Branch lines 1.86.0;
PR record 1.97.0).

Rewrites every docs/**/spec.md and docs/system/repos.md once:
  - `Synced at: <repo> a@1, d; b@2, d` becomes one `Synced at:` line per repo
    and branch, sorted by repo, then branch.
  - the repos table's `Synced at` column moves into a `## Synced at` section
    right after the table: `- <repo> <branch>@<short sha>, <date>`, one bullet
    per repo and branch, sorted.
  - numbered or `Q<n>`-prefixed open questions become plain `- ` bullets.
  - (1.86.0) a `; `-joined Match `Branch:` list becomes one `Branch:` line
    per branch, markers kept, sorted by repo, then branch.
  - (1.97.0) every PR note (docs/notes/**, `kind: pull request`) gets a
    `## PR record` section with its `State` line. A review-pr follow-ups note
    (`kind: review-pr`, linked by `pr_note:` or by its PR number and repo) is
    moved into its PR note: each bullet becomes a `Point` line (text verbatim,
    status `migrated`, or `done <sha>` for `(done in <sha>)`), its dated comment
    sections go into the PR note's history in date order, its intro and bullets
    into `## Review follow-ups, moved <date>`, its front matter into one
    `Moved from` line, and `used_by` / `waiting_for` are merged. The old file is
    deleted, repo-path mentions of it are rewritten, and the notes indexes are
    rebuilt.

Every line and every entry is kept. Before anything is written, a
nothing-lost check compares old and new; a file that would lose anything is
left alone and the run exits 2. A second run changes nothing. Line endings
are kept. Never commits.

Usage (from the product repo root, or pass --root):
    python3 merge_safe_migrate.py --dry-run   list what would change, with a diff; write nothing
    python3 merge_safe_migrate.py             migrate
    python3 merge_safe_migrate.py --check     exit 1 when a file still needs it
    python3 merge_safe_migrate.py --selftest
Standard library only.
"""
import argparse, datetime, difflib, re, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

SYNC = re.compile(r"^Synced at: (\S+) (.+?)\s*$")
ENTRY = re.compile(r"^(\S+)@([0-9a-f]{7,40}), (\d{4}-\d{2}-\d{2})( \(dropped\))?$")
QNUM = re.compile(r"^(?:\d+[.)]\s+)?(?:\*\*)?Q\d+[.:)]?(?:\*\*)?\s+(.*)$")
NUM = re.compile(r"^\d+[.)]\s+(.*)$")
BRANCH = re.compile(r"^(- )?Branch: (.+?)\s*$")
OLD_NOTE = '`Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.'  # the 1.83 template paragraph, replaced only when unchanged
NEW_NOTE = ("`## Synced at` below holds one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, "
            "sorted by repo, then branch (1.84.0). A new read replaces only that repo and branch's line. "
            "A consumer measuring drift uses, for each repo and branch, the older of this line and the slice line; "
            "no line means unknown, so fall back to spec file commit dates.")


def entries(text):
    return [e.strip() for e in text.split(";") if e.strip()]


def key(repo, entry):
    return (repo.lower(), entry.split("@", 1)[0].lower(), entry)


def branch_key(entry):
    """(repo, branch) of a Branch entry; markers ignored. No repo sorts as ''."""
    words = entry.split(" (", 1)[0].split()
    repo, br = (words[0], words[1]) if len(words) >= 2 else ("", words[0] if words else "")
    return (repo.lower(), br.lower(), entry)


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
        b = BRANCH.match(ln)
        if b and ";" in b.group(2):
            seen = []
            for e in sorted(entries(b.group(2)), key=branch_key):
                if e not in seen:
                    seen.append(e)
            out += ["%sBranch: %s" % (b.group(1) or "", e) for e in seen]
            i += 1
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
        b = None if repos else BRANCH.match(ln)
        if b:
            for e in entries(b.group(2)):
                c[("B", b.group(1) or "", e)] = 1
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



# ---- PR record (1.97.0) -------------------------------------------------

HIST = re.compile(r"^## (Description as of|PR updates as of|Comment as drafted,|Comment as posted,|Replies as drafted,|Review follow-ups, moved) (\d{4}-\d{2}-\d{2})")
STATE_ON = re.compile(r"State on (\d{4}-\d{2}-\d{2}): ([A-Za-z]+)")
STATE_MAP = {"active": "active", "draft": "draft", "completed": "merged", "merged": "merged",
             "abandoned": "abandoned", "closed": "closed"}
KIND_ORDER = {"Order": 0, "Point": 1, "Read": 2, "Ready": 3, "State": 4}
REC = re.compile(r"^- (Order|Point|Read|Ready|State): ")


def split_note(lines):
    """(front matter lines incl. ---, body lines). No front matter: ([], lines)."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[:i + 1], lines[i + 1:]
    return [], lines


def fm_get(fm, key):
    for ln in fm:
        if ln.startswith(key + ":"):
            return ln[len(key) + 1:].strip()
    return None


def fm_list(v):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip() for x in v[1:-1].split(",") if x.strip()]
    return [v] if v else []


def pr_key(source):
    """('71', 'bc-operations') from `PR 71 dev.azure.com/o/p/bc-operations` or `PR 71 bc-operations`."""
    m = re.match(r"^PR (\d+) (\S+)", source or "")
    if not m:
        return None
    return (m.group(1), m.group(2).rstrip("/").split("/")[-1].lower())


def rec_sort_key(line):
    m = REC.match(line)
    kind = m.group(1) if m else "Point"
    rest = line[len(m.group(0)):] if m else line
    f = [x.strip() for x in rest.split(" | ")]
    if kind == "Order":
        n = re.search(r"PR (\d+)", rest)
        return (KIND_ORDER[kind], int(n.group(1)) if n else 0, rest.lower())
    if kind == "Point":
        return (KIND_ORDER[kind], f[0].lower(), (f[-1] if len(f) > 1 else rest).lower())
    return (KIND_ORDER[kind], f[0].lower(), "")


def insert_sorted(rec, line):
    """Put a new record line in sorted place; existing lines never move."""
    k = rec_sort_key(line)
    for i, ln in enumerate(rec):
        if REC.match(ln) and rec_sort_key(ln) > k:
            return rec[:i] + [line] + rec[i:]
    return rec + [line]


ANCHOR = [
    (re.compile(r"^`([^`]+)`, lines? (\d+)(?:\s*[\u2013-]\s*(\d+))?"), lambda m: m.group(1) + ":" + m.group(2) + ("-" + m.group(3) if m.group(3) else "")),
    (re.compile(r"^`([^`]+)`, no line"), lambda m: m.group(1)),
    (re.compile(r"^`([^`]+)`:"), lambda m: m.group(1)),
    (re.compile(r"^Branch `([^`]+)`"), lambda m: "branch " + m.group(1)),
]


def point_from_bullet(text, date):
    """A follow-ups bullet (without `- `) as a Point line, text verbatim."""
    anchor = "general"
    for rx, f in ANCHOR:
        m = rx.match(text)
        if m:
            anchor = f(m)
            break
    done = re.findall(r"\(done in ([0-9a-f]{7,40})\)", text)
    status = "done " + done[-1] if done else "migrated"
    tags = []
    if text.startswith("Asked on the PR:"):
        tags.append("asked")
    for d in re.findall(r"\(answered on the PR (\d{4}-\d{2}-\d{2})\)", text):
        tags.append("answered " + d)
    for d in re.findall(r"\(Not in the posted comment, (\d{4}-\d{2}-\d{2})", text):
        tags.append("not posted " + d)
    tags.append("from review-pr " + date)
    return "- Point: %s | %s | - | %s | %s" % (anchor, status, "; ".join(tags), text.replace("\n", " "))


def history_sections(body):
    """(lines before the first history heading, [(date, section lines)])."""
    head, secs, cur = [], [], None
    for ln in body:
        m = HIST.match(ln)
        if m:
            cur = (m.group(2), [ln])
            secs.append(cur)
        elif cur is None:
            head.append(ln)
        else:
            cur[1].append(ln)
    return head, secs


def strip_blank(xs):
    while xs and not xs[0].strip():
        xs = xs[1:]
    while xs and not xs[-1].strip():
        xs = xs[:-1]
    return xs


def migrate_pr(pr_lines, fu, fu_rel, today):
    """New PR note lines. fu: follow-ups note lines or None."""
    fm, body = split_note(pr_lines)
    head, secs = history_sections(body)
    # the record, existing or new
    rs = next((i for i, ln in enumerate(head) if ln.strip() == "## PR record"), None)
    if rs is None:
        states = []
        for ln in pr_lines:
            for d, s in STATE_ON.findall(ln):
                states.append((d, s.lower()))
        rec = []
        if states:
            d, s = max(states)
            rec.append("- State: %s | %s" % (STATE_MAP.get(s, s), d))
        pre = strip_blank(head)
        tail = []
    else:
        re_ = rs + 1
        while re_ < len(head) and not head[re_].startswith("## "):
            re_ += 1
        pre = strip_blank(head[:rs])
        rec = [ln for ln in head[rs + 1:re_] if ln.strip()]
        tail = strip_blank(head[re_:])
    moved = []
    if fu is not None:
        ffm, fbody = split_note(fu)
        date = fm_get(ffm, "imported") or fm_get(ffm, "source_date") or today
        fhead, fsecs = history_sections(fbody)
        intro = [ln for ln in fhead if not ln.startswith("# ")]
        for ln in fhead:
            if ln.startswith("- ") and not ln.startswith("- Point: "):
                pl = point_from_bullet(ln[2:], date)
                if not any(r.endswith(" | " + ln[2:]) for r in rec):
                    rec = insert_sorted(rec, pl)
        fmtext = "; ".join(x.strip() for x in ffm if x.strip() and x.strip() != "---")
        title = next((ln for ln in fhead if ln.startswith("# ")), "")
        moved = ["## Review follow-ups, moved %s" % today, "",
                 "Moved from `%s` by `migrate formats` (1.97.0). Its title: %s. Its front matter: %s." % (fu_rel, title[2:].strip() or "none", fmtext or "none"), ""] + strip_blank(intro) + [""]
        for d, s in fsecs:
            # before the first existing section with a later date; existing sections never move
            pos = next((i for i, (dd, _) in enumerate(secs) if dd > d), len(secs))
            secs = secs[:pos] + [(d, s)] + secs[pos:]
        # merge list fields
        for key in ("used_by", "waiting_for"):
            a, b = fm_list(fm_get(fm, key)), fm_list(fm_get(ffm, key))
            merged = a + [x for x in b if x not in a]
            if merged != a:
                if fm_get(fm, key) is None:
                    fm = fm[:-1] + ["%s: [%s]" % (key, ", ".join(merged))] + fm[-1:]
                else:
                    fm = ["%s: [%s]" % (key, ", ".join(merged)) if ln.startswith(key + ":") else ln for ln in fm]
    if moved:
        secs.append((today, moved))
    out = list(fm) + pre + ["", "## PR record", ""] + rec + [""]
    if tail:
        out += tail + [""]
    for _, s in secs:
        out += strip_blank(s) + [""]
    while out and not out[-1].strip():
        out.pop()
    return out


def pr_items(lines):
    """Every non-blank body line (front-matter list fields as items)."""
    c = Counter()
    fm, body = split_note(lines)
    for ln in fm:
        k = ln.split(":", 1)[0]
        if k in ("used_by", "waiting_for"):
            for x in fm_list(ln.split(":", 1)[1]):
                c[("FM", k, x)] = 1
        elif ln.strip():
            c[("F", ln.rstrip())] += 1
    for ln in body:
        if ln.strip():
            c[("L", ln.rstrip())] += 1
    return c


def pr_lost(old_pr, old_fu, new):
    """What of the old PR note and follow-ups note is missing from the new note."""
    lost = pr_items(old_pr) - pr_items(new)
    if old_fu is not None:
        ffm, fbody = split_note(old_fu)
        nc = pr_items(new)
        need = Counter()
        for ln in fbody:
            if ln.strip() and not ln.startswith("# "):
                need[("L", ln.rstrip())] += 1
        newtext = "\n".join(new)
        for k, v in (need - nc).items():
            lost[k] = v
        for ln in ffm:
            s = ln.strip()
            if s and s != "---":
                k = s.split(":", 1)[0]
                if k in ("used_by", "waiting_for"):
                    for x in fm_list(s.split(":", 1)[1]):
                        if ("FM", k, x) not in nc:
                            lost[("FM", k, x)] = 1
                elif s not in newtext:
                    lost[("F", s)] = 1
        for ln in fbody:
            if ln.startswith("# ") and ln[2:].strip() not in newtext:
                lost[("T", ln)] = 1
    return lost


def read_lines(path):
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    trail = raw.endswith("\n")
    lines = raw.replace("\r\n", "\n").split("\n")
    if trail:
        lines = lines[:-1]
    return raw, lines, nl, trail


def pr_targets(root):
    """[(pr note path, follow-ups path or None)], and follow-ups notes with no PR note."""
    notes = root / "docs" / "notes"
    if not notes.exists():
        return [], []
    prs, fus = {}, []
    for p in sorted(notes.rglob("*.md")):
        if p.name == "index.md" or "_template" in p.parts:
            continue
        _, lines, _, _ = read_lines(p)
        fm, _ = split_note(lines)
        kind = fm_get(fm, "kind")
        if kind == "pull request":
            prs[p] = (pr_key(fm_get(fm, "source")), lines)
        elif kind == "review-pr" and re.search(r"(^|/)review-pr-.*follow-ups\.md$", p.name):
            fus.append((p, fm_get(fm, "pr_note"), pr_key(fm_get(fm, "source"))))
    link, orphans = {}, []
    for p, pn, k in fus:
        hit = None
        if pn and (root / pn).resolve() in {x.resolve() for x in prs}:
            hit = next(x for x in prs if x.resolve() == (root / pn).resolve())
        if hit is None and k:
            cands = [x for x, (kk, _) in prs.items() if kk == k]
            hit = cands[0] if len(cands) == 1 else None
        if hit is None or hit in link:
            orphans.append(p)
        else:
            link[hit] = p
    return [(p, link.get(p)) for p in prs], orphans


def rel(root, p):
    return str(p.relative_to(root)).replace("\\", "/")


def run_pr(root, write, today, show_diff):
    """Returns (changed, bad, orphans, deleted, rewritten)."""
    pairs, orphans = pr_targets(root)
    changed, bad, deleted, rewritten = [], [], [], []
    for p, fu in pairs:
        raw, lines, nl, trail = read_lines(p)
        fu_lines = read_lines(fu)[1] if fu else None
        new = migrate_pr(lines, fu_lines, rel(root, fu) if fu else None, today)
        lost = pr_lost(lines, fu_lines, new)
        if lost:
            bad.append((p, lost))
            continue
        text = nl.join(new) + (nl if trail else "")
        if text == raw and not fu:
            continue
        changed.append(p)
        if show_diff:
            sys.stdout.writelines(difflib.unified_diff(lines and [x + "\n" for x in lines], [x + "\n" for x in new], "a/" + rel(root, p), "b/" + rel(root, p)))
            if fu:
                sys.stdout.writelines(difflib.unified_diff([x + "\n" for x in fu_lines], [], "a/" + rel(root, fu), "/dev/null"))
        if write:
            p.write_bytes(text.encode("utf-8"))
        if fu:
            deleted.append((fu, p))
    # mentions of a moved follow-ups note elsewhere (indexes are rebuilt instead)
    for fu, p in deleted:
        old_rel, new_rel = rel(root, fu), rel(root, p)
        for q in sorted((root / "docs").rglob("*.md")):
            if q.name == "index.md" or q == fu or q == p:
                continue
            qraw = q.read_bytes().decode("utf-8")
            qnew = qraw.replace(old_rel, new_rel)
            if q.parent == fu.parent:
                qnew = re.sub(r"(?<![\w/.-])" + re.escape(fu.name), p.name, qnew)
            if qnew != qraw:
                rewritten.append(q)
                if show_diff:
                    sys.stdout.writelines(difflib.unified_diff(qraw.splitlines(True), qnew.splitlines(True), "a/" + rel(root, q), "b/" + rel(root, q)))
                if write:
                    q.write_bytes(qnew.encode("utf-8"))
        if write:
            fu.unlink()
    return changed, bad, orphans, deleted, rewritten

def targets(root):
    docs = root / "docs"
    fs = [(p, False) for p in sorted(docs.rglob("spec.md"))] if docs.exists() else []
    r = docs / "system" / "repos.md"
    if r.exists():
        fs.append((r, True))
    return fs


def run(root, write, check, today=None, show_diff=False):
    changed, bad = [], []
    for p, repos in targets(root):
        old, new, lost = process(p, repos)
        if lost:
            bad.append((p, lost))
            continue
        if old != new:
            changed.append(p)
            if show_diff:
                sys.stdout.writelines(difflib.unified_diff(old.replace("\r\n", "\n").splitlines(True), new.replace("\r\n", "\n").splitlines(True), "a/" + rel(root, p), "b/" + rel(root, p)))
            if write:
                p.write_bytes(new.encode("utf-8"))
    today = today or datetime.date.today().isoformat()
    pchanged, pbad, orphans, deleted, rewritten = run_pr(root, write and not bad, today, show_diff)
    bad += pbad
    for p, lost in bad:
        print("LOST %s: %s (left alone)" % (rel(root, p), ", ".join(map(str, list(lost)[:5]))))
    for p in changed + pchanged:
        print(("migrated " if write and (p in changed or not bad) else "would migrate ") + rel(root, p))
    for fu, p in deleted:
        print(("moved " if write and not bad else "would move ") + "%s into %s" % (rel(root, fu), rel(root, p)))
    for q in rewritten:
        print(("rewrote " if write and not bad else "would rewrite ") + "the link in " + rel(root, q))
    for fu in orphans:
        print("NO PR NOTE %s: no PR note for it, so it was left alone; write the PR note first (/crav1-add-to-spec pr<n> all)" % rel(root, fu))
    if write and (pchanged or deleted) and not bad:
        idx = Path(__file__).with_name("notes_index.py")
        if idx.exists():
            subprocess.run([sys.executable, str(idx), "--root", str(root)], check=False, stdout=subprocess.DEVNULL)
            print("rebuilt the notes indexes")
    if not changed and not pchanged and not bad:
        print("already merge-safe: nothing to change")
    if bad:
        return 2
    if check and (changed or pchanged):
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
                "- **Q2.** Is the cut-off local time?\r\n  - Blocks: T2\r\n- Plain one?\r\n\r\n## Match\r\n\r\n"
                "- Branch: pantry-api feat/pantry-retry-t2 (into feat/pantry-retry) (PR 12); pantry-api feat/pantry-retry (spec branch); feature/pantry-openapi\r\n"
                "- Repo: pantry-api\r\n")
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
        assert ("## Match\r\n\r\n- Branch: feature/pantry-openapi\r\n- Branch: pantry-api feat/pantry-retry (spec branch)\r\n"
                "- Branch: pantry-api feat/pantry-retry-t2 (into feat/pantry-retry) (PR 12)\r\n- Repo: pantry-api") in a, a
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
        # a branch entry dropped by hand counts as lost
        old = ["## Match", "- Branch: a x; a y"]
        assert items(old, False) - items(["## Match", "- Branch: a x"], False)
        assert not items(old, False) - items(migrate_spec(old), False)
    # 1.97.0: PR note + follow-ups note become one PR note with a PR record
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        m = root / "docs" / "notes" / "2026-10"
        m.mkdir(parents=True)
        pr = ("---\ntitle: \"PR 42 (orders-api): Retry\"\nkind: pull request\nsource: PR 42 github.com/contoso/orders-api\n"
              "source_date: 2026-10-17\nimported: 2026-10-17\nused_by: [orders]\nwaiting_for: []\n---\n"
              "# PR 42 (orders-api): Retry\n\nSource date: 2026-10-17. Imported: 2026-10-17.\n\nURL: https://github.com/contoso/orders-api/pull/42\n"
              "Author: Sam Lee\ndevelop <- feat/orders-retry\nState on 2026-10-17: active\n\n## Description as of 2026-10-17\n\n## What\n\nRetries.\n\n"
              "## PR updates as of 2026-10-21\n\nDescription: unchanged. State on 2026-10-21: active.\n")
        fu = ("---\ntitle: Follow-ups from PR 42 (orders-api)\nkind: review-pr\nsource: PR 42 orders-api\nsource_date: 2026-10-19\n"
              "imported: 2026-10-20\npr_note: docs/notes/2026-10/2026-10-17-pr-orders-api-42.md\nused_by: [billing]\nwaiting_for: []\n---\n"
              "# Follow-ups from PR 42 (orders-api)\n\nFrom review 2026-10-19. PR 42, orders-api, Retry.\n\n"
              "- `src/retry.py`, lines 9\u201312: an idempotency test. (Not in the posted comment, 2026-10-19; still open.)\n"
              "- Asked on the PR: is the cut-off local time? (answered on the PR 2026-10-20)\n"
              "- `src/a.py`, line 3: guard the store. (done in abc1234)\n\n"
              "## Comment as posted, 2026-10-19 (by Alex Doe)\n\n## Not a history heading\n\nText.\n\n## Comment as drafted, 2026-10-22\n\n````text\nDraft.\n````\n")
        (m / "2026-10-17-pr-orders-api-42.md").write_text(pr)
        (m / "review-pr-orders-api-42-follow-ups.md").write_text(fu)
        (m / "2026-10-18-orders-api-feat.md").write_text("---\ntitle: x\nkind: code change\nsource: x\nsource_date: 2026-10-18\nimported: 2026-10-18\n---\n# x\n\nSee docs/notes/2026-10/review-pr-orders-api-42-follow-ups.md and [f](review-pr-orders-api-42-follow-ups.md).\n")
        assert run(root, False, True, "2026-10-27") == 1
        assert (m / "review-pr-orders-api-42-follow-ups.md").exists()
        assert run(root, True, False, "2026-10-27") == 0
        assert not (m / "review-pr-orders-api-42-follow-ups.md").exists()
        n = (m / "2026-10-17-pr-orders-api-42.md").read_text()
        assert "used_by: [orders, billing]" in n, n
        assert n.index("State on 2026-10-17: active\n\n## PR record\n\n") < n.index("## Description as of"), n
        assert ("- Point: general | migrated | - | asked; answered 2026-10-20; from review-pr 2026-10-20 | Asked on the PR: is the cut-off local time? (answered on the PR 2026-10-20)\n"
                "- Point: src/a.py:3 | done abc1234 | - | from review-pr 2026-10-20 | `src/a.py`, line 3: guard the store. (done in abc1234)\n"
                "- Point: src/retry.py:9-12 | migrated | - | not posted 2026-10-19; from review-pr 2026-10-20 |") in n, n
        assert "- State: active | 2026-10-21\n" in n, n
        h = [n.index(x) for x in ("## Description as of 2026-10-17", "## Comment as posted, 2026-10-19", "## Not a history heading",
                                   "## PR updates as of 2026-10-21", "## Comment as drafted, 2026-10-22", "## Review follow-ups, moved 2026-10-27")]
        assert h == sorted(h), n
        c = (m / "2026-10-18-orders-api-feat.md").read_text()
        assert "follow-ups" not in c and c.count("2026-10-17-pr-orders-api-42.md") == 2, c
        first = n
        assert run(root, True, True, "2026-10-28") == 0
        assert (m / "2026-10-17-pr-orders-api-42.md").read_text() == first
        # a dropped line counts as lost
        lines = pr.split("\n")
        assert pr_lost(lines, None, [x for x in migrate_pr(lines, None, None, "2026-10-27") if x != "Retries."])
        assert not pr_lost(lines, None, migrate_pr(lines, None, None, "2026-10-27"))
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
    return run(Path(a.root).resolve(), not (a.dry_run or a.check), a.check, show_diff=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
