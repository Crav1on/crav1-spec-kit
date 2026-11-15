"""1.160.0: your own claim does not hold a task, and claims are written in local time."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
import test_claims_sync_1151 as base  # noqa: E402

CLAIMS = base.CLAIMS
WALK = base.WALK


def load_claims():
    spec = importlib.util.spec_from_file_location("claims_1160", CLAIMS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_env(script, args, tz=None):
    env = dict(os.environ)
    if tz:
        env["TZ"] = tz
    proc = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False, env=env)
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    return proc.returncode, payload, proc.stderr or ""


@unittest.skipUnless(hasattr(__import__("time"), "tzset"), "needs time.tzset")
class LocalTimeTests(unittest.TestCase):
    def setUp(self):
        import time
        self._tz = os.environ.get("TZ")
        os.environ["TZ"] = "Europe/Stockholm"
        time.tzset()
        self.claims = load_claims()
        self.tmp = Path(tempfile.mkdtemp())
        self.root = base.write_slice(self.tmp)

    def tearDown(self):
        import time
        if self._tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = self._tz
        time.tzset()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_format_is_local_offset_to_the_second(self):
        when = datetime(2026, 11, 14, 22, 40, 0, 123456, tzinfo=timezone.utc)
        self.assertEqual(self.claims.format_when(when), "2026-11-14T23:40:00+01:00")

    def test_old_utc_line_still_reads(self):
        text = "# Claims\n\nIn progress: feat/orders-api-host-setup, T2, person A, since 2026-11-14T22:40:00.654321+00:00\n"
        parsed = self.claims.parse_claims(text, now=datetime(2026, 11, 15, tzinfo=timezone.utc))
        claim = parsed["claims"][0]
        self.assertEqual(claim["user"], "person A")
        self.assertEqual(claim["since"], "2026-11-14T23:40:00+01:00")
        self.assertEqual(parsed["raw"][0]["when"], datetime(2026, 11, 14, 22, 40, 0, 654321, tzinfo=timezone.utc))

    def test_add_writes_local_time_without_microseconds(self):
        code, payload, err = run_env(CLAIMS, [
            "add", "--root", str(self.root), "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2", "--user", "person A",
        ], tz="Europe/Stockholm")
        self.assertEqual(code, 0, err)
        line = [l for l in (self.root / "claims.md").read_text(encoding="utf-8").splitlines() if l.startswith("In progress:")][0]
        since = line.rsplit("since ", 1)[1]
        self.assertRegex(since, r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+0[12]:00$")
        self.assertNotIn(".", since)


class OwnClaimTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = base.write_slice(self.tmp)
        code, _, err = base.run_py(CLAIMS, [
            "add", "--root", str(self.root), "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2", "--user", "person A", "--since", "2026-11-13T15:50:00+01:00",
        ])
        self.assertEqual(code, 0, err)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def readiness(self, *extra):
        code, payload, err = base.run_py(WALK, ["readiness", "--full", "--skip-sync", "--root", str(self.root), *extra])
        self.assertEqual(code, 0, err + json.dumps(payload)[:500])
        gate = next(g for g in payload["gates"] if g["task"] == "T2")
        return payload, gate

    def test_own_claim_is_not_refused(self):
        payload, gate = self.readiness("--user", "Person A")
        self.assertFalse(gate["refused"])
        self.assertTrue(gate["allow"])
        self.assertEqual(gate["reason"], "in progress by you")
        self.assertIn("T2", payload.get("can_start") or [])
        self.assertIn("In progress by you: T2.", payload.get("ending") or "")

    def test_own_claim_on_the_walked_branch(self):
        _, gate = self.readiness("--user", "person A", "--branch", "feat/orders-api-host-setup")
        self.assertFalse(gate["refused"])

    def test_own_claim_on_another_branch_still_holds(self):
        _, gate = self.readiness("--user", "person A", "--branch", "feat/orders-api-export")
        self.assertTrue(gate["refused"])

    def test_someone_elses_claim_still_refuses(self):
        payload, gate = self.readiness("--user", "person B")
        self.assertTrue(gate["refused"])
        self.assertIn("in progress by person A", gate["reason"])
        self.assertNotIn("T2", payload.get("can_start") or [])

    def test_user_defaults_to_git_config(self):
        base.git(self.tmp, "init", "-b", "main")
        base.git(self.tmp, "config", "user.name", "person A")
        _, gate = self.readiness()
        self.assertFalse(gate["refused"])
        base.git(self.tmp, "config", "user.name", "person B")
        _, gate = self.readiness()
        self.assertTrue(gate["refused"])


if __name__ == "__main__":
    unittest.main()
