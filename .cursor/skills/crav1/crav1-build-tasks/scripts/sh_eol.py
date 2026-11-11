#!/usr/bin/env python3
"""Note when a new shell script may be saved with Windows line endings (1.129.0).

Prints one line when a build wrote a new `.sh` file, `.gitattributes` has no
`*.sh` rule with `eol=lf`, and `core.autocrlf` is true or the host is Windows.
The line offers `*.sh text eol=lf` as an optional extra. It does not write
the file. Prints nothing when the note does not apply.

Usage:
  sh_eol.py --wrote-sh --gitattributes <file> --autocrlf <value> [--windows]

`--gitattributes -` reads the attributes text on stdin. A missing file is the
same as an empty one. The interpreter is python3, then python, then py -3.
"""
import pathlib
import re
import sys

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

SH_LF = re.compile(r"(?m)^\s*\*\.sh\b[^\n]*\beol=lf\b")
NOTE = (
    "Shell scripts may be saved with Windows line endings. "
    "Optional: add `*.sh text eol=lf` to `.gitattributes`."
)


def note(wrote_sh, gitattributes, autocrlf, windows):
    """The note to show, or None. Never describes the line as already added."""
    if not wrote_sh:
        return None
    if SH_LF.search(gitattributes or ""):
        return None
    auto = str(autocrlf or "").strip().lower() == "true"
    if not auto and not windows:
        return None
    return NOTE


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        return 0 if argv else 2
    wrote = "--wrote-sh" in argv
    windows = "--windows" in argv
    autocrlf = ""
    attributes = ""
    args = [arg for arg in argv if arg not in ("--wrote-sh", "--windows")]
    i = 0
    while i < len(args):
        if args[i] == "--autocrlf" and i + 1 < len(args):
            autocrlf = args[i + 1]
            i += 2
            continue
        if args[i] == "--gitattributes" and i + 1 < len(args):
            path = args[i + 1]
            i += 2
            if path == "-":
                attributes = sys.stdin.read()
            else:
                file = pathlib.Path(path)
                attributes = file.read_text(encoding="utf-8") if file.is_file() else ""
            continue
        sys.stdout.write(__doc__ or "")
        return 2
    line = note(wrote, attributes, autocrlf, windows)
    if line:
        sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
