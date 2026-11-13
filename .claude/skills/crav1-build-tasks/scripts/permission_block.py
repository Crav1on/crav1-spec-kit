#!/usr/bin/env python3
"""A missing yes is not a permission refusal (1.143.0).

permission_block.py --user-yes yes|no --permission-refused yes|no
    --command '<exact command>' --rerun '/crav1-build-walk'
    [--task 'T3 Apply the CI build policy']

--user-yes yes when the user's yes is on record: said in this run, or
`(live yes: …)` on the task line. --permission-refused yes when the coding
assistant's own permission check refused the command, for example as
modifying shared resources. The host check is not the user's yes.

yes-missing: the yes is not on record. Waiting says that. Do not say the
permission check blocked the command.

permission-refused: the yes is on record and the check blocked the command.
Waiting says both. The offer is only the two lines: run that exact command,
or allow that one command and rerun. Next is the build step again after the
command has run. This result never says the yes is missing and never suggests
working around the check.

run: the command may proceed. No waiting line.

Prints JSON. Standard library only. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
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


# Fixed sentences only. The exact command is not scanned: it is the user's text.
BANNED = (
    "workaround",
    "work around",
    "bypass",
    "skip the check",
    "disable the permission",
    "another way",
    "different command",
)


def _yes(value: str) -> bool:
    text = (value or "").strip().casefold()
    if text in ("yes", "true", "1"):
        return True
    if text in ("no", "false", "0", ""):
        return False
    raise ValueError(f"expected yes or no, got {value!r}")


def suggests_workaround(text: str) -> bool:
    """True when fixed wording tells the user to get around the check."""
    low = (text or "").casefold()
    return any(phrase in low for phrase in BANNED)


def _fixed(waiting: str | None, offer: list[str], nxt: str | None) -> str:
    parts = [waiting or ""]
    if len(offer) > 1:
        parts.append(offer[1])
    parts.append(nxt or "")
    return "\n".join(parts)


def classify(
    user_yes: bool,
    permission_refused: bool,
    command: str = "",
    rerun: str = "/crav1-build-tasks",
    task: str = "",
) -> dict:
    """Distinguish a missing yes from a recorded yes the check refused.

    A permission refusal does not count when the user's yes is not on record.
    That case stays yes-missing, so the lines cannot say the yes is on record.
    """
    shown = " ".join((command or "").split()) or "the live command"
    step = " ".join((rerun or "").split()) or "/crav1-build-tasks"
    label = " ".join((task or "").split())
    if not user_yes:
        why = (
            f"{label} runs live and the live run needs your yes"
            if label
            else "the live run needs your yes"
        )
        waiting = "Waiting: your yes to run the live command is not on record."
        nxt = f"Next: {step}, because {why}."
        out = {
            "kind": "yes-missing",
            "yes_on_record": False,
            "permission_refused": False,
            "waiting": waiting,
            "offer": [],
            "next": nxt,
            "says_yes_missing": True,
        }
    elif permission_refused:
        why = (
            f"{label} can rerun after the command has run"
            if label
            else "the command has run and the build step can rerun"
        )
        waiting = (
            "Waiting: your yes is on record. "
            "The assistant's permission check blocked the command."
        )
        offer = [
            f"Run it yourself: {shown}",
            "Or allow that one command and rerun.",
        ]
        nxt = f"Next: {step}, because {why}."
        out = {
            "kind": "permission-refused",
            "yes_on_record": True,
            "permission_refused": True,
            "waiting": waiting,
            "offer": offer,
            "next": nxt,
            "says_yes_missing": False,
        }
    else:
        out = {
            "kind": "run",
            "yes_on_record": True,
            "permission_refused": False,
            "waiting": None,
            "offer": [],
            "next": None,
            "says_yes_missing": False,
        }
    fixed = _fixed(out["waiting"], out["offer"], out["next"])
    if suggests_workaround(fixed):
        raise RuntimeError("permission-block wording suggests a workaround")
    out["workaround"] = False
    return out


def printable(outcome: dict) -> list[str]:
    lines = []
    if outcome.get("waiting"):
        lines.append(outcome["waiting"])
    lines.extend(outcome.get("offer") or [])
    if outcome.get("next"):
        lines.append(outcome["next"])
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Missing yes versus a permission refusal")
    parser.add_argument("--user-yes", required=True, help="yes when the user's yes is on record")
    parser.add_argument("--permission-refused", required=True, help="yes when the assistant's check refused the command")
    parser.add_argument("--command", default="", help="the exact command that was refused")
    parser.add_argument("--rerun", default="/crav1-build-tasks", help="the build step to run after the command has run")
    parser.add_argument("--task", default="", help="T# plus the short name, when one task is in view")
    args = parser.parse_args(argv)
    try:
        user_yes = _yes(args.user_yes)
        refused = _yes(args.permission_refused)
    except ValueError as exc:
        json.dump({"ok": False, "error": str(exc)}, sys.stdout)
        sys.stdout.write("\n")
        return 2
    outcome = classify(user_yes, refused, args.command, args.rerun, args.task)
    outcome["ok"] = True
    outcome["lines"] = printable(outcome)
    json.dump(outcome, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
