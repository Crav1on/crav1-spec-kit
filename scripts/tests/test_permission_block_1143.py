"""1.143.0: a recorded yes the assistant's permission check refused is not a missing yes."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-build-tasks/scripts/permission_block.py"
WALK = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/build_walk.py"
COMMAND = "bash infra/ado/develop-build-policy.sh apply"
TASK = "T3 Apply the CI build policy"


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pb = load(SCRIPT, "permission_block")
bw = load(WALK, "build_walk_1143")


class Distinguish(unittest.TestCase):
    def test_a_missing_yes_does_not_say_the_check_blocked_the_command(self):
        missing = pb.classify(False, False, COMMAND, "/crav1-build-tasks T3", TASK)
        refused_flag_without_yes = pb.classify(False, True, COMMAND, "/crav1-build-tasks T3", TASK)
        for outcome in (missing, refused_flag_without_yes):
            self.assertEqual(outcome["kind"], "yes-missing")
            self.assertTrue(outcome["says_yes_missing"])
            self.assertIn("not on record", outcome["waiting"])
            self.assertNotIn("permission check", outcome["waiting"])
            self.assertNotIn("yes is on record", outcome["waiting"])
            self.assertIn("needs your yes", outcome["next"])
            self.assertEqual(outcome["offer"], [])
            self.assertFalse(pb.suggests_workaround(pb._fixed(outcome["waiting"], outcome["offer"], outcome["next"])))

    def test_a_recorded_yes_the_check_refused_does_not_say_the_yes_is_missing(self):
        outcome = pb.classify(True, True, COMMAND, "/crav1-build-walk", TASK)
        text = "\n".join(pb.printable(outcome))
        self.assertEqual(outcome["kind"], "permission-refused")
        self.assertTrue(outcome["yes_on_record"])
        self.assertFalse(outcome["says_yes_missing"])
        self.assertIn("your yes is on record", outcome["waiting"])
        self.assertIn("assistant's permission check blocked the command", outcome["waiting"])
        self.assertNotIn("not on record", text)
        self.assertNotIn("needs your yes", text)
        self.assertNotIn("yes is missing", text.casefold())
        self.assertEqual(outcome["offer"], [
            f"Run it yourself: {COMMAND}",
            "Or allow that one command and rerun.",
        ])
        self.assertTrue(outcome["next"].startswith("Next: /crav1-build-walk,"))
        self.assertIn("can rerun after the command has run", outcome["next"])
        self.assertEqual(outcome["next"].count("/crav1-"), 1)
        self.assertFalse(pb.suggests_workaround(pb._fixed(outcome["waiting"], outcome["offer"], outcome["next"])))
        self.assertFalse(outcome["workaround"])

    def test_a_recorded_yes_with_no_refusal_may_run(self):
        outcome = pb.classify(True, False, COMMAND, "/crav1-build-tasks T3", TASK)
        self.assertEqual(outcome["kind"], "run")
        self.assertIsNone(outcome["waiting"])
        self.assertIsNone(outcome["next"])
        self.assertEqual(pb.printable(outcome), [])

    def test_the_command_prints_the_same_lines(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--user-yes", "yes",
                "--permission-refused", "yes",
                "--command", COMMAND,
                "--rerun", "/crav1-build-tasks T3",
                "--task", TASK,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["kind"], "permission-refused")
        self.assertEqual(payload["lines"][0], payload["waiting"])
        self.assertIn(COMMAND, payload["lines"][1])
        self.assertTrue(payload["lines"][-1].startswith("Next: /crav1-build-tasks T3,"))


class WalkLive(unittest.TestCase):
    line = "- [ ] T3: Apply the CI build policy (Runs live) (after: )"

    def test_the_walk_does_not_call_a_recorded_refusal_a_missing_yes(self):
        missing = bw.live_gate(self.line, dry_ran=True, user_yes=False, permission_refused=True, live_command=COMMAND)
        self.assertEqual(missing["phase"], "live-yes")
        self.assertTrue(missing["says_yes_missing"])
        self.assertNotIn("live yes:", missing["line"])

        blocked = bw.live_gate(
            self.line,
            dry_ran=True,
            user_yes=True,
            permission_refused=True,
            live_command=COMMAND,
            name="person A",
            date="2026-11-13",
        )
        self.assertEqual(blocked["phase"], "permission-refused")
        self.assertFalse(blocked["run_live"])
        self.assertFalse(blocked["says_yes_missing"])
        self.assertIn("(live yes: person A, 2026-11-13)", blocked["line"])
        self.assertIn("[ ]", blocked["line"])
        self.assertIn("your yes is on record", blocked["waiting"])
        self.assertIn(COMMAND, blocked["offer"][0])
        self.assertNotIn("needs your yes", blocked["next_line"])

        phase = bw.current_phase({
            "owner": "self",
            "runs_live": True,
            "dry_ran": True,
            "live_yes": False,
            "permission_refused": True,
        })
        self.assertEqual(phase, "live-yes")
        phase = bw.current_phase({
            "owner": "self",
            "runs_live": True,
            "dry_ran": True,
            "live_yes": True,
            "permission_refused": True,
        })
        self.assertEqual(phase, "permission-refused")

        result = bw.next_for({
            "mode": "walk",
            "owner": "self",
            "phase": "permission-refused",
            "branch": "feat/orders-host-setup-scripts",
            "tasks": [{"id": 3, "title": "Apply the CI build policy"}],
            "command": COMMAND,
        })
        line = result["next"][0]
        self.assertEqual(result["count"], 1)
        self.assertEqual(line.count("Next:"), 1)
        self.assertEqual(len([part for part in line.split() if part.startswith("/crav1-")]), 1)
        self.assertIn("/crav1-build-walk", line)
        self.assertIn("can rerun after the command has run", line)
        self.assertNotIn("needs your yes", line)
        self.assertIn("your yes is on record", result["waiting"])
        self.assertIn(COMMAND, "\n".join(result["offer"]))
        self.assertNotIn("needs your yes", "\n".join(result["lines"]))


class SkillText(unittest.TestCase):
    def test_the_skills_name_the_distinction_and_forbid_a_workaround(self):
        files = [
            ROOT / ".cursor/skills/crav1/crav1-build-tasks/references/permission-block.md",
            ROOT / ".cursor/skills/crav1/crav1-build-tasks/SKILL.md",
            ROOT / ".cursor/skills/crav1/crav1-build-tasks/branches/one-task/BRANCH.md",
            ROOT / ".cursor/skills/crav1/crav1-build-tasks/branches/several-tasks/BRANCH.md",
            ROOT / ".cursor/skills/crav1/crav1-build-tasks/branches/one-task/references/run.md",
            ROOT / ".cursor/skills/crav1/crav1-build-walk/references/live.md",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertIn("permission", text.casefold(), path.name)
        block = files[0].read_text(encoding="utf-8")
        self.assertIn("yes is on record", block)
        self.assertIn("Do not suggest working around the check.", block)
        self.assertIn("exact command", block)
        live = files[-1].read_text(encoding="utf-8")
        self.assertIn("do not say the yes is missing", live.casefold())
        self.assertIn("permission-block.md", live)


if __name__ == "__main__":
    unittest.main()
