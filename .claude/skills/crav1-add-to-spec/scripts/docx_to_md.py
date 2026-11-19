#!/usr/bin/env python3
"""Turn a .docx (for example a meeting summary) into Markdown, word for word (1.195.0).

    docx_to_md.py convert --docx <file.docx> [--out <file.md>]
    docx_to_md.py check   --docx <file.docx> --md <file.md>

Standard library only, no network. Keeps paragraphs, headings (Heading 1-6),
list items with their level, and bold runs (**bold**). Prints the document's
created date from docProps/core.xml when it has one. `check` compares the
words of the .docx with the words of the Markdown (markup ignored) and lists
the first difference, so the converted source can be checked before it is
saved, as references/sources-binary.md says.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

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

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/terms/}"


def _run_text(run) -> str:
    out = []
    for node in run:
        if node.tag == W + "t":
            out.append(node.text or "")
        elif node.tag == W + "tab":
            out.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            out.append(" ")
    return "".join(out)


def _is_bold(run) -> bool:
    props = run.find(W + "rPr")
    if props is None:
        return False
    b = props.find(W + "b")
    return b is not None and b.get(W + "val", "true") not in ("0", "false")


def paragraph_md(p) -> str:
    props = p.find(W + "pPr")
    style = ""
    level = None
    if props is not None:
        st = props.find(W + "pStyle")
        style = st.get(W + "val", "") if st is not None else ""
        num = props.find(W + "numPr")
        if num is not None:
            lvl = num.find(W + "ilvl")
            level = int(lvl.get(W + "val", "0")) if lvl is not None else 0
    parts = []
    for run in p.iter(W + "r"):
        text = _run_text(run)
        if not text:
            continue
        if _is_bold(run) and text.strip():
            lead = text[: len(text) - len(text.lstrip())]
            tail = text[len(text.rstrip()):]
            parts.append(f"{lead}**{text.strip()}**{tail}")
        else:
            parts.append(text)
    line = re.sub(r"\*\*\*\*", "", "".join(parts)).rstrip()
    if not line.strip():
        return ""
    m = re.match(r"(?i)heading\s*(\d)", style)
    if m:
        return "#" * min(int(m.group(1)), 6) + " " + line.replace("**", "").strip()
    if level is not None or style.lower().startswith("list"):
        return "  " * (level or 0) + "- " + line.strip()
    return line


def convert(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read("word/document.xml"))
        created = None
        if "docProps/core.xml" in z.namelist():
            core = ET.fromstring(z.read("docProps/core.xml"))
            node = core.find(DC + "created")
            created = node.text if node is not None else None
    body = doc.find(W + "body")
    lines = []
    for p in body.iter(W + "p") if body is not None else []:
        md = paragraph_md(p)
        if md:
            lines.append(md)
    text = "\n\n".join(lines) + "\n" if lines else ""
    return {"markdown": text, "created": created, "paragraphs": len(lines)}


def words(text: str) -> list[str]:
    text = re.sub(r"[*#`]", " ", text)
    text = re.sub(r"(?m)^\s*-\s+", " ", text)
    return text.split()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("--docx", required=True)
    c.add_argument("--out", help="write the Markdown here (UTF-8); otherwise print it in the JSON")
    k = sub.add_parser("check")
    k.add_argument("--docx", required=True)
    k.add_argument("--md", required=True)
    a = ap.parse_args(argv)
    try:
        got = convert(Path(a.docx))
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        json.dump({"ok": False, "error": "docx", "line": f"Not a readable .docx: {exc}"}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 1
    if a.cmd == "convert":
        out = {"ok": True, "created": got["created"], "paragraphs": got["paragraphs"]}
        if a.out:
            Path(a.out).write_text(got["markdown"], encoding="utf-8")
            out["wrote"] = a.out
        else:
            out["markdown"] = got["markdown"]
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    want, have = words(got["markdown"]), words(Path(a.md).read_text(encoding="utf-8"))
    first = next((i for i, (x, y) in enumerate(zip(want, have)) if x != y), None)
    if first is None and len(want) == len(have):
        out = {"ok": True, "same": True, "words": len(want), "line": "The Markdown has every word of the .docx, in order."}
    else:
        i = first if first is not None else min(len(want), len(have))
        out = {"ok": True, "same": False, "at_word": i, "docx": " ".join(want[i:i + 8]), "md": " ".join(have[i:i + 8]),
               "line": f"The Markdown differs from the .docx at word {i}."}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if out["same"] else 2


if __name__ == "__main__":
    sys.exit(main())
