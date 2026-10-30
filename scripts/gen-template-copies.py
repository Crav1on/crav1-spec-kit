#!/usr/bin/env python3
"""Write every skill template copy from docs/*/_template/ (1.107.0).

scripts/template-copies.tsv lists each copy under .cursor/skills/crav1/ and its
source. A source is a template file, a template plus an insert from
scripts/template-overlays/ ("<base> + insert <file> before <heading>"), or an
overlay file that is its own template (the architecture and matched-slice specs).
sync-crav1-plugin.sh runs this first, so the plugin and Claude copies follow.

  gen-template-copies.py          write the copies
  gen-template-copies.py --check  exit 1 when a copy is stale
"""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".cursor/skills/crav1"
INSERT = re.compile(r"^(\S+) \+ insert (\S+) before (.+)$")


def build(src: str) -> bytes:
    m = INSERT.match(src)
    if not m:
        return (ROOT / src).read_bytes()
    base, ins, heading = (ROOT / m[1]).read_text(), (ROOT / m[2]).read_text(), m[3]
    if heading not in base:
        raise SystemExit(f"{m[1]} has no {heading!r} for the insert {m[2]}")
    return base.replace(heading, ins + heading, 1).encode()


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale = []
    rows = [l.split("\t") for l in (ROOT / "scripts/template-copies.tsv").read_text().splitlines() if l and not l.startswith("#")]
    for rel, src in rows:
        dest, body = SKILLS / rel, build(src)
        if dest.is_file() and dest.read_bytes() == body:
            continue
        stale.append(rel)
        if not check:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
    if check and stale:
        print("Stale template copies (run scripts/sync-crav1-plugin.sh):\n  " + "\n  ".join(stale))
        return 1
    print(f"Template copies {'match' if check else 'written from'} docs/*/_template/ ({len(rows)} copies, {len(stale)} {'stale' if check else 'updated'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
