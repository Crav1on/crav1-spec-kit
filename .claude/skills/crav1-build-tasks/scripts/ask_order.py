#!/usr/bin/env python3
"""Say whether a branch answer or a permissions answer has to be asked again (1.129.0).

The branch question and the permissions question are separate cards. A typed
branch name belongs on the branch card. continue, click, and stop belong on
the permissions card. A missing answer, or an answer that belongs on the
other card, is re-asked. Do not guess.

Usage:
  ask_order.py branch "<text>"
  ask_order.py permissions "<text>"

Prints `ok` or `re-ask`. Exit 0 either way. Exit 2 when the slot is unknown.
The interpreter is python3, then python, then py -3.
"""
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

PERMISSIONS = {"continue", "click", "stop"}
# A label with no branch name is not an answer. There is no follow-up card.
OTHER = {"other", "other name", "other-name"}


def reask(slot, text):
    """True when this one question must be asked again."""
    raw = (text or "").strip().lower()
    if slot == "permissions":
        return raw not in PERMISSIONS
    if slot == "branch":
        return raw == "" or raw in PERMISSIONS or raw in OTHER
    raise ValueError(slot)


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 0
    if len(argv) != 2 or argv[0] not in ("branch", "permissions"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 2
    sys.stdout.write("re-ask\n" if reask(argv[0], argv[1]) else "ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
