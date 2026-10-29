#!/usr/bin/env python3
"""Dependency order for a slice's tasks.md (kit 1.103.0).

Reads `- [ ] T#: ...` / `- [x] T#: ...` lines. A task's dependencies are its `(after: T1, T3)` mark; a task
with no `(after: ...)` waits on the task just before it in the file (the first task waits on nothing).
Dependency order is a topological sort in waves (a task's wave is one more than its latest dependency's),
lowest task number first inside a wave.
Ready: unticked, every dependency ticked, no missing dependency, not in a cycle. Next: the ready task that
unblocks the most unticked tasks (all tasks downstream of it), lowest number on a tie.

Usage: task_order.py <tasks.md> [--failed T7,T9] [--json]
Standard library only. Prints nothing secret; reads only the file it is given.
"""
import json
import re
import sys

TASK = re.compile(r"^\s*- \[( |x|X)\] T(\d+)\b[:.]?\s*(.*)$")
AFTER = re.compile(r"\(after:\s*([^)]*)\)")


def parse(text):
    tasks, prev = [], None
    for line in text.splitlines():
        m = TASK.match(line)
        if not m:
            continue
        num, rest = int(m.group(2)), m.group(3)
        a = AFTER.search(rest)
        if a:
            deps = [int(x) for x in re.findall(r"T(\d+)", a.group(1))]
            recorded = True
        else:
            deps = [prev] if prev is not None else []
            recorded = False
        title = re.sub(r"\s*\((verify|spec|after|branch):[^)]*\)", "", rest).strip()
        tasks.append({"id": num, "done": m.group(1) != " ", "title": title, "deps": deps, "recorded": recorded})
        prev = num
    return tasks


def _cycles(ids, deps):
    """Tasks that sit on a dependency cycle, with one cycle path for each."""
    on_cycle, color, stack = {}, {}, []

    def visit(n):
        color[n] = 1
        stack.append(n)
        for d in deps.get(n, []):
            if d not in ids:
                continue
            if color.get(d) == 1:
                path = stack[stack.index(d):] + [d]
                for p in path[:-1]:
                    on_cycle.setdefault(p, path)
            elif not color.get(d):
                visit(d)
        stack.pop()
        color[n] = 2

    for n in sorted(ids):
        if not color.get(n):
            visit(n)
    return on_cycle


def analyse(tasks, failed=()):
    ids = {t["id"] for t in tasks}
    by = {t["id"]: t for t in tasks}
    deps = {t["id"]: t["deps"] for t in tasks}
    users = {i: [] for i in ids}
    for t in tasks:
        for d in t["deps"]:
            if d in ids:
                users[d].append(t["id"])
    cyc = _cycles(ids, deps)

    # Kahn in waves: a task's wave is one more than its latest dependency's wave. Order is wave by wave,
    # lowest number first inside a wave (tasks in one wave can run in parallel). Cycle members go last.
    indeg = {i: sum(1 for d in deps[i] if d in ids) for i in ids}
    wave = {i: 0 for i in ids if indeg[i] == 0}
    frontier = sorted(wave)
    while frontier:
        nxt_frontier = []
        for n in frontier:
            for u in users[n]:
                indeg[u] -= 1
                wave[u] = max(wave.get(u, 0), wave[n] + 1)
                if indeg[u] == 0:
                    nxt_frontier.append(u)
        frontier = sorted(nxt_frontier)
    placed = [i for i in ids if indeg[i] == 0]
    order = sorted(placed, key=lambda i: (wave[i], i)) + sorted(ids - set(placed))

    def downstream(n):
        seen, todo = set(), list(users[n])
        while todo:
            u = todo.pop()
            if u not in seen:
                seen.add(u)
                todo.extend(users[u])
        return seen

    failed = set(failed)
    rows = []
    for n in order:
        t = by[n]
        if t["done"]:
            continue
        missing = [d for d in t["deps"] if d not in ids]
        open_deps = [d for d in t["deps"] if d in ids and not by[d]["done"]]
        tag = "recorded" if t["recorded"] else "inferred"
        if n in cyc:
            reason = "cycle " + " → ".join(f"T{x}" for x in cyc[n]) + " (recorded)"
        elif missing:
            reason = "after: " + ", ".join(f"T{x}" for x in missing) + " names no task (recorded)"
        elif open_deps:
            reason = "waits on " + ", ".join(f"T{x}" for x in open_deps) + f" ({tag})"
        else:
            reason = None
        rows.append({"id": n, "title": t["title"], "ready": reason is None, "reason": reason,
                     "unblocks": len([u for u in downstream(n) if not by[u]["done"]])})
    ready = [r for r in rows if r["ready"]]
    nxt = min(ready, key=lambda r: (-r["unblocks"], r["id"]))["id"] if ready else None
    failed_deps = {}
    for f in sorted(failed):
        if f in ids:
            for u in downstream(f):
                failed_deps.setdefault(u, f)
    return {"order": [n for n in order if not by[n]["done"]], "ready": [r["id"] for r in ready],
            "blocked": [r for r in rows if not r["ready"]], "next": nxt,
            "depends_on_failed": {f"T{k}": f"depends on T{v} (failed)" for k, v in sorted(failed_deps.items())},
            "rows": rows}


def render(res):
    out = ["Ready (dependency order)"]
    out += [f"- T{r['id']}: {r['title']}" for r in res["rows"] if r["ready"]] or ["- none"]
    out.append("Blocked (dependency order)")
    out += [f"- T{r['id']}: {r['reason']}" for r in res["blocked"]] or ["- none"]
    out.append("Order: " + " → ".join(f"T{n}" for n in res["order"]))
    out.append(f"Next: T{res['next']}" if res["next"] else "Next: none ready")
    for k, v in res["depends_on_failed"].items():
        out.append(f"{k}: {v}")
    return "\n".join(out)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    failed = []
    if "--failed" in argv:
        failed = [int(x) for x in re.findall(r"\d+", argv[argv.index("--failed") + 1])]
    with open(argv[0], encoding="utf-8") as fh:
        res = analyse(parse(fh.read()), failed)
    print(json.dumps(res, ensure_ascii=False, indent=1) if "--json" in argv else render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
