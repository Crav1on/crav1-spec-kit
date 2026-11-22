#!/usr/bin/env python3
"""Command prefix for Run next scripts (1.201.0).

Reads the update-kit vendor table. The default prefix is `/`. `--vendor codex`
prints `$crav1-` in place of `/crav1-`. Cursor, Claude Code, and Copilot keep
`/`. A missing table keeps `/` for those names and `$` for codex, so a script
still runs. Standard library only. Writes nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COMMAND = re.compile(r"(?<![A-Za-z0-9_./-])/crav1-")
FALLBACK = {"cursor": "/", "claude": "/", "codex": "$", "copilot": "/"}


def vendors_file() -> Path | None:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "vendors.json", here / "vendors.json"):
        if candidate.is_file():
            return candidate
    return None


def load_table() -> dict | None:
    path = vendors_file()
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def prefix_for(vendor: str | None) -> str:
    """The command prefix for a vendor. Empty means `/`, today's output."""
    if not vendor:
        return "/"
    table = load_table()
    rows = (table or {}).get("vendors") if isinstance(table, dict) else None
    row = rows.get(vendor) if isinstance(rows, dict) else None
    if isinstance(row, dict) and row.get("prefix"):
        return str(row["prefix"])
    if vendor in FALLBACK:
        return FALLBACK[vendor]
    print(f"Refused: {vendor} is not a vendor.", file=sys.stderr)
    raise SystemExit(2)


def rewrite(text: str, vendor: str | None) -> str:
    """Replace `/crav1-` command prefixes. Paths such as `crav1/crav1-help` stay."""
    prefix = prefix_for(vendor)
    if prefix == "/":
        return text
    return COMMAND.sub(prefix + "crav1-", text)


class _Rewriter:
    """Line-buffer stdout and rewrite command prefixes. Flush writes the tail."""

    def __init__(self, raw, prefix: str):
        self.raw = raw
        self.prefix = prefix
        self.buf = ""

    def write(self, data) -> int:
        text = data if isinstance(data, str) else str(data)
        self.buf += text
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            self.raw.write(COMMAND.sub(self.prefix + "crav1-", line) + "\n")
        return len(text)

    def flush(self) -> None:
        if self.buf:
            self.raw.write(COMMAND.sub(self.prefix + "crav1-", self.buf))
            self.buf = ""
        self.raw.flush()

    def __getattr__(self, name):
        return getattr(self.raw, name)


def pop_vendor(argv: list[str]) -> tuple[str | None, list[str]]:
    vendor = None
    out: list[str] = []
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--vendor":
            if index + 1 >= len(argv):
                print("Refused: --vendor needs a name.", file=sys.stderr)
                raise SystemExit(2)
            vendor = argv[index + 1]
            index += 2
            continue
        if item.startswith("--vendor="):
            vendor = item.split("=", 1)[1]
            index += 1
            continue
        out.append(item)
        index += 1
    return vendor, out


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        return


def main(argv: list[str] | None = None) -> int:
    """`--help` only. Run next scripts import this module; they do not shell out to it."""
    _utf8_stdout()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print("Rewrites /crav1- in Run next output. Imported by those scripts. --vendor codex prints $crav1-.")
        return 0
    print("Refused: import this module from a Run next script.", file=sys.stderr)
    return 2


def install_from_argv(argv: list[str] | None) -> list[str] | None:
    """Drop `--vendor` from argv. When the prefix is not `/`, wrap stdout.

    With no flag, return argv unchanged (None stays None) and leave stdout alone.
    """
    source = sys.argv[1:] if argv is None else list(argv)
    if "--vendor" not in source and not any(item.startswith("--vendor=") for item in source):
        return argv
    vendor, rest = pop_vendor(source)
    prefix = prefix_for(vendor)
    if prefix != "/":
        sys.stdout = _Rewriter(sys.stdout, prefix)
    return rest


if __name__ == "__main__":
    raise SystemExit(main())
