#!/usr/bin/env python3
"""Change one Point's tags in a PR note's record (1.193.0), in place, only with --yes.

    pr_points.py answered --note <PR note> (--thread <id> | --number <n>) --date <YYYY-MM-DD> [--yes]
    pr_points.py in-spec  --note <PR note> (--thread <id> | --number <n>) --slug <slug> --date <YYYY-MM-DD> [--yes]

`answered` sets `answered <date>` and narrows an older `in spec <slug>` tag to
`in spec <slug> (question)`, so the Point is a candidate again. `in-spec`
writes `in spec <slug> <date>` after a Point is taken into a spec. Which
Points are candidates is decided only by `pr_common.py candidates` in
crav1-open-pr (shared with /crav1-pr-status); this script reuses its parser.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()


def _pr_common():
    path = Path(__file__).resolve().parent.parent.parent / "crav1-open-pr" / "scripts" / "pr_common.py"
    spec = importlib.util.spec_from_file_location("pr_common_points", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = _pr_common()


def emit(payload: dict, status: int = 0) -> int:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return status


def rewrite(note: str, args, fn) -> int:
    path = Path(note)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    hits, n = [], 0
    for i, line in enumerate(lines):
        point = pc.parse_point(line)
        if not point:
            continue
        n += 1
        if (args.thread and f"thread {args.thread}" in point["tags"]) or (args.number and n == args.number):
            hits.append(i)
    if len(hits) != 1:
        return emit({"status": "refused", "reason": f"{len(hits)} Points match; name one by --thread or --number"}, 2)
    i = hits[0]
    eol = "\n" if lines[i].endswith("\n") else ""
    new = fn(lines[i]) + eol
    out = {"status": "written" if args.yes else "planned", "old": lines[i].rstrip("\n"), "new": new.rstrip("\n")}
    if not args.yes:
        out["line"] = "Planned only. Run again with --yes to change this one line in place."
    elif new != lines[i]:
        lines[i] = new
        path.write_text("".join(lines), encoding="utf-8")
    return emit(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    an = sub.add_parser("answered")
    an.add_argument("--note", required=True)
    an.add_argument("--thread")
    an.add_argument("--number", type=int)
    an.add_argument("--date", required=True)
    an.add_argument("--yes", action="store_true")
    ins = sub.add_parser("in-spec")
    ins.add_argument("--note", required=True)
    ins.add_argument("--thread")
    ins.add_argument("--number", type=int)
    ins.add_argument("--slug", required=True)
    ins.add_argument("--date", required=True)
    ins.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    if not args.thread and not args.number:
        return emit({"status": "refused", "reason": "name the Point by --thread or --number"}, 2)
    if args.cmd == "answered":
        return rewrite(args.note, args, lambda line: pc.mark_answered(line, args.date))
    return rewrite(args.note, args, lambda line: pc.mark_in_spec(line, args.slug, args.date))


if __name__ == "__main__":
    sys.exit(main())
