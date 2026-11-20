#!/usr/bin/env python3
"""Find a local test dependency's container before offering an install (1.198.0).

Read-only. Looks for docker or podman, a container whose name or image matches
the service (running or stopped), and, for podman, a stopped machine. Prints one
JSON object with `state` and the commands to recommend:

- running: the container is up; check its port.
- stopped: start it (`podman machine start` first when the machine is down,
  then `podman start <name>` / `docker start <name>`).
- no-container: a runtime exists but no container; use the repo's documented
  start command.
- no-runtime: neither docker nor podman; only now offer an install.

Usage: dep_check.py containers --service <name> [--service <name> ...]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

TIMEOUT = 8


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL, check=False)
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return done.returncode, done.stdout or ""


def _rows(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            parts = line.split("\t")
            if len(parts) >= 3:
                rows.append({"Names": parts[0], "Image": parts[1], "State": parts[2]})
    return rows


def _name(row: dict) -> str:
    names = row.get("Names") or row.get("Name") or ""
    if isinstance(names, list):
        names = names[0] if names else ""
    return str(names).lstrip("/")


def _running(row: dict) -> bool:
    state = str(row.get("State") or row.get("Status") or "").lower()
    return state.startswith("running") or state.startswith("up")


def check(services: list[str], which=shutil.which, run=_run) -> dict:
    wanted = [s.lower() for s in services if s.strip()]
    runtimes = [tool for tool in ("podman", "docker") if which(tool)]
    if not runtimes:
        return {"ok": True, "state": "no-runtime", "runtime": None, "containers": [], "start": [],
                "install": True,
                "line": "No docker or podman found. Offer to install the dependency or a container runtime."}
    found: list[dict] = []
    machine_down = False
    used = runtimes[0]
    for tool in runtimes:
        code, out = run([tool, "ps", "-a", "--format", "{{.Names}}\t{{.Image}}\t{{.State}}"])
        if tool == "podman" and code != 0:
            mcode, mout = run(["podman", "machine", "list", "--format", "{{.Name}}\t{{.Running}}"])
            if mcode == 0 and mout.strip() and "true" not in mout.lower():
                machine_down = True
                used = tool
                # Containers live inside the stopped machine; we cannot list them yet.
                continue
        for row in _rows(out):
            name = _name(row)
            hay = (name + " " + str(row.get("Image", ""))).lower()
            if any(w in hay for w in wanted):
                found.append({"runtime": tool, "name": name, "running": _running(row)})
                used = tool
    if any(item["running"] for item in found):
        up = next(item for item in found if item["running"])
        return {"ok": True, "state": "running", "runtime": up["runtime"], "containers": found, "start": [],
                "install": False, "line": f"Container {up['name']} is running; check its port."}
    start: list[str] = []
    if machine_down:
        start.append("podman machine start")
    for item in found:
        start.append(f"{item['runtime']} start {item['name']}")
    if found or machine_down:
        named = ", ".join(item["name"] for item in found) or "its containers"
        why = "The podman machine is stopped" if machine_down else "The container is stopped"
        return {"ok": True, "state": "stopped", "runtime": used, "containers": found, "start": start,
                "install": False, "machine_stopped": machine_down,
                "line": f"{why}. Start {named}: " + "; ".join(f"`{c}`" for c in start) + ". No install needed."}
    return {"ok": True, "state": "no-container", "runtime": used, "containers": [], "start": [], "install": False,
            "line": f"{used} is installed but has no container for {', '.join(services)}. Use the repo's documented start command."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cont = sub.add_parser("containers")
    cont.add_argument("--service", action="append", required=True)
    args = parser.parse_args(argv)
    json.dump(check(args.service), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
