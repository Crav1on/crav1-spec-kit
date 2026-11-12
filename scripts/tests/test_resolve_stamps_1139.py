"""1.139.0: a walk-progress.md conflict that is only hash lines is settled.

The merged spec and tasks supply the new hash when every side that matches
its own file differs from the merge only by progress marks. A real edit keeps
the upstream hash so the walk reopens the steps that edit affects. A hunk
that touches Done or Result is left alone.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"

SPEC = """# Orders export

The receipt lists the order id.

## Open questions

- Which lane prints the label?
  - Asked: 2026-10-10, mail to person A.
  - Blocks: T3
"""

PLAN = """# Plan: orders export

Reviewed: 2026-11-12, P# open: 0
"""

TASKS = """# Tasks

- [ ] T2 export the receipt (branch: feat/orders-export)
- [ ] T3 record the order (branch: feat/orders-record)
"""

VERIFY = """# Verify

No rows yet.
"""

STEPS = (
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)


def load_mod():
    spec = importlib.util.spec_from_file_location("walk_progress_1139", WALK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = load_mod()


def raw_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def norm_hash(kind: str, text: str) -> str:
    return MOD.version_text(MOD.normalize_text(kind, text))


def split_spec(text: str) -> tuple[str, str]:
    body, questions = MOD.spec_parts(text)
    return body, questions


def tick(tasks: str, tid: str) -> str:
    return tasks.replace(f"- [ ] {tid} ", f"- [x] {tid} ", 1)


def sentence(tasks: str) -> str:
    return tasks.replace("export the receipt", "export the receipt and the tax line", 1)


def crlf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\n", "\r\n")


def write_files(folder: Path, spec: str, plan: str, tasks: str, verify: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "spec.md").write_bytes(spec.encode("utf-8"))
    (folder / "plan.md").write_bytes(plan.encode("utf-8"))
    (folder / "tasks.md").write_bytes(tasks.encode("utf-8"))
    (folder / "verify.md").write_bytes(verify.encode("utf-8"))


def stamp_set(spec: str, plan: str, tasks: str, verify: str, normalized: bool) -> dict[str, str]:
    if normalized:
        body, questions = split_spec(spec)
        return {
            "spec": norm_hash("spec", spec),
            "plan": norm_hash("plan", plan),
            "tasks": norm_hash("tasks", tasks),
            "verify": norm_hash("verify", verify),
            "spec_body": norm_hash("spec", body),
            "questions": norm_hash("questions", questions),
        }
    body, questions = split_spec(spec)
    return {
        "spec": raw_hash(spec),
        "plan": raw_hash(plan),
        "tasks": raw_hash(tasks),
        "verify": raw_hash(verify),
        "spec_body": MOD.version_text(body),
        "questions": MOD.version_text(questions),
    }


def progress(steps: list[str], stamps: dict[str, str], normalized: bool, tasks_override: dict[str, str] | None = None) -> str:
    lines = [
        "# Walk progress",
        "",
        "Walk: tighten-and-plan-ready-to-build",
        "Slice: docs/specs/orders-export/",
        "",
    ]
    for index, step in enumerate(steps):
        lines.append(f"- Step: {step}")
        lines.append(f"  Done: 2026-11-12T09:0{index}:00+00:00")
        result = "ready-partial" if step == "tasks-ready-to-build" else "done"
        lines.append(f"  Result: {result}")
        lines.append(f"  Spec version: {stamps['spec']}")
        lines.append(f"  Plan version: {stamps['plan']}")
        tasks_hash = (tasks_override or {}).get(step, stamps["tasks"])
        lines.append(f"  Tasks version: {tasks_hash}")
        if step == "tasks-ready-to-build":
            lines.append(f"  Verify version: {stamps['verify']}")
        lines.append(f"  Spec body: {stamps['spec_body']}")
        lines.append(f"  Questions version: {stamps['questions']}")
        if normalized:
            lines.append("  Content stamp: normalized")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def mark(ours: str, theirs: str) -> str:
    own_lines = ours.splitlines()
    their_lines = theirs.splitlines()
    if len(own_lines) != len(their_lines):
        raise AssertionError(f"line count {len(own_lines)} vs {len(their_lines)}")
    out: list[str] = []
    index = 0
    while index < len(own_lines):
        if own_lines[index] == their_lines[index]:
            out.append(own_lines[index])
            index += 1
            continue
        start = index
        while index < len(own_lines) and own_lines[index] != their_lines[index]:
            index += 1
        out.append("<<<<<<< HEAD")
        out.extend(own_lines[start:index])
        out.append("=======")
        out.extend(their_lines[start:index])
        out.append(">>>>>>> upstream")
    return "\n".join(out) + "\n"


def run(args: list[str]) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [sys.executable, str(WALK), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload, proc.stderr


class ResolveStampsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.merged = self.tmp / "merged"
        self.ours = self.tmp / "ours"
        self.theirs = self.tmp / "theirs"

    def _layout(self, ours_tasks: str, theirs_tasks: str, merged_tasks: str, spec: str = SPEC, newline: str = "\n") -> None:
        def apply(text: str) -> str:
            return crlf(text) if newline == "\r\n" else text

        write_files(self.ours, apply(spec), apply(PLAN), apply(ours_tasks), apply(VERIFY))
        write_files(self.theirs, apply(spec), apply(PLAN), apply(theirs_tasks), apply(VERIFY))
        write_files(self.merged, apply(spec), apply(PLAN), apply(merged_tasks), apply(VERIFY))

    def _conflict(self, steps: list[str], ours_tasks: str, theirs_tasks: str, normalized: bool, newline: str = "\n") -> None:
        def apply(text: str) -> str:
            return crlf(text) if newline == "\r\n" else text

        spec, plan, verify = apply(SPEC), apply(PLAN), apply(VERIFY)
        ours_tasks, theirs_tasks = apply(ours_tasks), apply(theirs_tasks)
        ours_stamps = stamp_set(spec, plan, ours_tasks, verify, normalized)
        theirs_stamps = stamp_set(spec, plan, theirs_tasks, verify, normalized)
        text = mark(
            progress(steps, ours_stamps, normalized),
            progress(steps, theirs_stamps, normalized),
        )
        if newline == "\r\n":
            text = crlf(text)
        (self.merged / "walk-progress.md").write_bytes(text.encode("utf-8"))

    def _resolve(self, extra: list[str] | None = None) -> tuple[int, dict]:
        args = [
            "resolve-stamps",
            "--root", str(self.merged),
            "--ours-root", str(self.ours),
            "--theirs-root", str(self.theirs),
            "--yes",
            *(extra or []),
        ]
        code, payload, _err = run(args)
        return code, payload

    def _resume(self) -> dict[str, str]:
        code, payload, err = run(["resume", "--root", str(self.merged), "--no-playbook"])
        self.assertEqual(code, 0, payload or err)
        return {row["id"]: row["status"] for row in payload["steps"]}

    def _tasks_versions(self) -> dict[str, str]:
        text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        found: dict[str, str] = {}
        step = None
        for line in text.splitlines():
            if line.startswith("- Step: "):
                step = line[len("- Step: "):]
            elif line.startswith("  Tasks version: ") and step:
                found[step] = line.split(": ", 1)[1]
        return found

    def test_stamp_only_one_two_and_three_steps(self) -> None:
        ours_tasks = tick(TASKS, "T2")
        theirs_tasks = tick(TASKS, "T3")
        merged_tasks = tick(tick(TASKS, "T2"), "T3")
        expected = norm_hash("tasks", merged_tasks)
        for count in (1, 2, 3):
            with self.subTest(steps=count):
                steps = list(STEPS[:count])
                self._layout(ours_tasks, theirs_tasks, merged_tasks)
                self._conflict(steps, ours_tasks, theirs_tasks, normalized=False)
                before = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
                self.assertIn("<<<<<<<", before)
                code, payload = self._resolve()
                self.assertEqual(code, 0, payload)
                self.assertTrue(payload["resolved"])
                self.assertNotIn("<<<<<<<", (self.merged / "walk-progress.md").read_text(encoding="utf-8"))
                versions = self._tasks_versions()
                for step in steps:
                    self.assertEqual(versions[step], expected, step)
                text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
                self.assertIn("  Done: 2026-11-12T09:00:00+00:00", text)
                self.assertIn("  Result: done", text)
                if "tasks-ready-to-build" in steps:
                    self.assertIn("  Result: ready-partial", text)
                self.assertIn("restamped", payload["line"])
                for step in steps:
                    self.assertIn(step, payload["line"])
                statuses = self._resume()
                for step in steps:
                    self.assertEqual(statuses[step], "keep", payload["line"])

    def test_mixed_conflict_refuses(self) -> None:
        ours_tasks = tick(TASKS, "T2")
        theirs_tasks = tick(TASKS, "T3")
        merged_tasks = tick(tick(TASKS, "T2"), "T3")
        self._layout(ours_tasks, theirs_tasks, merged_tasks)
        self._conflict(list(STEPS), ours_tasks, theirs_tasks, normalized=False)
        text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        rewritten = []
        for line in lines:
            if line == "  Result: done" and "<<<<<<<" not in "\n".join(rewritten):
                rewritten.extend([
                    "<<<<<<< HEAD",
                    "  Result: done",
                    "=======",
                    "  Result: skipped",
                    ">>>>>>> upstream",
                ])
            else:
                rewritten.append(line)
        mixed = "\n".join(rewritten) + "\n"
        (self.merged / "walk-progress.md").write_text(mixed, encoding="utf-8")
        original = (self.merged / "walk-progress.md").read_bytes()
        code, payload = self._resolve()
        self.assertEqual(code, 1, payload)
        self.assertEqual(payload["code"], "mixed-conflict")
        self.assertFalse(payload["resolved"])
        self.assertIsNone(payload["wrote"])
        self.assertEqual((self.merged / "walk-progress.md").read_bytes(), original)
        self.assertTrue(payload["stamp_hunks"])
        self.assertTrue(payload["blocked_hunks"])
        blocked_lines = [name for hunk in payload["blocked_hunks"] for name in hunk["lines"]]
        self.assertIn("Result", blocked_lines)
        stamp_lines = [name for hunk in payload["stamp_hunks"] for name in hunk["lines"]]
        self.assertIn("Tasks version", stamp_lines)
        self.assertIn("settle stamps", payload["line"])
        self.assertEqual(payload["offer"], "settle stamps")
        code, payload = self._resolve(["--settle-stamps"])
        self.assertEqual(code, 1, payload)
        self.assertTrue(payload.get("settled_stamps"))
        self.assertFalse(payload["resolved"])
        settled = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Result: skipped", settled)
        self.assertIn("<<<<<<<", settled)
        self.assertIn(norm_hash("tasks", merged_tasks), settled)
        self.assertNotIn("Tasks version: " + raw_hash(ours_tasks), settled)

    def test_crlf_file(self) -> None:
        ours_tasks = tick(TASKS, "T2")
        theirs_tasks = tick(TASKS, "T3")
        merged_tasks = tick(tick(TASKS, "T2"), "T3")
        self._layout(ours_tasks, theirs_tasks, merged_tasks, newline="\r\n")
        self._conflict(["review-and-tighten-plan"], ours_tasks, theirs_tasks, normalized=False, newline="\r\n")
        expected = norm_hash("tasks", merged_tasks)
        code, payload = self._resolve()
        self.assertEqual(code, 0, payload)
        data = (self.merged / "walk-progress.md").read_bytes()
        self.assertIn(b"\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertEqual(self._tasks_versions()["review-and-tighten-plan"], expected)
        self.assertEqual(self._resume()["review-and-tighten-plan"], "keep")

    def test_genuine_change_keeps_upstream_and_reopens(self) -> None:
        ours_tasks = sentence(TASKS)
        theirs_tasks = TASKS
        merged_tasks = ours_tasks
        self._layout(ours_tasks, theirs_tasks, merged_tasks)
        self._conflict(list(STEPS), ours_tasks, theirs_tasks, normalized=True)
        upstream = norm_hash("tasks", theirs_tasks)
        code, payload = self._resolve()
        self.assertEqual(code, 0, payload)
        self.assertIn("kept upstream", payload["line"])
        self.assertIn("reopens", payload["line"])
        versions = self._tasks_versions()
        for step in STEPS:
            self.assertEqual(versions[step], upstream, step)
        text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("  Done: 2026-11-12T09:00:00+00:00", text)
        self.assertIn("  Result: done", text)
        self.assertIn("  Result: ready-partial", text)
        statuses = self._resume()
        # plan-from-spec records tasks and does not reopen for a tasks edit.
        self.assertEqual(statuses["plan-from-spec"], "keep")
        self.assertEqual(statuses["review-and-tighten-plan"], "reopen")
        self.assertEqual(statuses["tasks-ready-to-build"], "reopen")

    def test_old_format_progress_restamps_and_genuine_keeps(self) -> None:
        ours_tasks = tick(TASKS, "T2")
        theirs_tasks = tick(TASKS, "T3")
        merged_tasks = tick(tick(TASKS, "T2"), "T3")
        self._layout(ours_tasks, theirs_tasks, merged_tasks)
        self._conflict(["tasks-ready-to-build"], ours_tasks, theirs_tasks, normalized=False)
        before = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        self.assertNotIn("Content stamp:", before)
        code, payload = self._resolve()
        self.assertEqual(code, 0, payload)
        text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("  Content stamp: normalized", text)
        self.assertEqual(self._tasks_versions()["tasks-ready-to-build"], norm_hash("tasks", merged_tasks))
        self.assertEqual(self._resume()["tasks-ready-to-build"], "keep")
        self.assertIn("  Result: ready-partial", text)

        ours_tasks = sentence(TASKS)
        theirs_tasks = TASKS
        self._layout(ours_tasks, theirs_tasks, ours_tasks)
        self._conflict(["review-and-tighten-plan", "tasks-ready-to-build"], ours_tasks, theirs_tasks, normalized=False)
        upstream = raw_hash(theirs_tasks)
        code, payload = self._resolve()
        self.assertEqual(code, 0, payload)
        self.assertIn("kept upstream", payload["line"])
        versions = self._tasks_versions()
        self.assertEqual(versions["review-and-tighten-plan"], upstream)
        self.assertEqual(versions["tasks-ready-to-build"], upstream)
        text = (self.merged / "walk-progress.md").read_text(encoding="utf-8")
        self.assertNotIn("Content stamp:", text)
        statuses = self._resume()
        self.assertEqual(statuses["review-and-tighten-plan"], "reopen")
        self.assertEqual(statuses["tasks-ready-to-build"], "reopen")

    def test_git_merge_reads_both_sides_and_stages(self) -> None:
        repo = self.tmp / "orders-api"
        spec = repo / "docs" / "specs" / "orders-export"
        spec.mkdir(parents=True)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "a@contoso.example"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Person A"], cwd=repo, check=True)

        def commit(message: str) -> None:
            subprocess.run(["git", "add", "--", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True)

        def put(tasks: str) -> None:
            write_files(spec, SPEC, PLAN, tasks, VERIFY)
            stamps = stamp_set(SPEC, PLAN, tasks, VERIFY, normalized=False)
            (spec / "walk-progress.md").write_text(
                progress(list(STEPS), stamps, normalized=False),
                encoding="utf-8",
            )

        # A task between the two ticks keeps tasks.md a clean merge.
        # The hash line in walk-progress.md is still one line, so it conflicts.
        base = TASKS.replace(
            "- [ ] T3 ",
            "- [ ] T4 file the copy (branch: feat/orders-file)\n- [ ] T3 ",
            1,
        )
        put(base)
        commit("Record the walk for orders export")
        subprocess.run(["git", "checkout", "-b", "upstream"], cwd=repo, check=True, capture_output=True)
        put(tick(base, "T3"))
        commit("Tick T3 on upstream")
        subprocess.run(["git", "checkout", "main"], cwd=repo, check=True, capture_output=True)
        put(tick(base, "T2"))
        commit("Tick T2 locally")
        merged = subprocess.run(
            ["git", "merge", "--no-commit", "--no-ff", "upstream"],
            cwd=repo, capture_output=True, text=True,
        )
        self.assertNotEqual(merged.returncode, 0, merged.stdout + merged.stderr)
        conflicted = (spec / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("<<<<<<<", conflicted)
        code, payload, err = run([
            "resolve-stamps", "--root", str(spec), "--yes",
        ])
        self.assertEqual(code, 0, payload or err)
        self.assertTrue(payload["resolved"], payload)
        self.assertTrue(payload["staged"], payload)
        self.assertNotIn("<<<<<<<", (spec / "walk-progress.md").read_text(encoding="utf-8"))
        unmerged = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=repo, capture_output=True, text=True, check=True,
        )
        self.assertEqual(unmerged.stdout.strip(), "")
        for step in STEPS:
            self.assertIn(step, payload["line"])


if __name__ == "__main__":
    unittest.main()
