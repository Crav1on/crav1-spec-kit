"""Command line: init, append, show-state, rebuild, lint, sessions. Read commands write nothing."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.paths import GITATTRIBUTES
from support import V2, fact_event, note_event, temp_dir


def run(repo, *args, stdin: str | None = None):
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "crav1_2", *args],
        cwd=repo,
        input=stdin,
        text=True,
        capture_output=True,
        env={**__import__("os").environ, "PYTHONPATH": str(V2)},
    )


def snapshot(repo) -> dict[str, bytes]:
    out = {}
    for path in repo.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            out[path.relative_to(repo).as_posix()] = path.read_bytes()
    return out


class Cli(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.root, ignore_errors=True))

    def test_init_append_views_and_readonly(self):
        init = run(self.root, "init")
        self.assertEqual(init.returncode, 0, init.stderr)
        self.assertEqual((self.root / ".crav1-2" / ".gitattributes").read_bytes(), GITATTRIBUTES)
        engine = json.loads((self.root / ".crav1-2" / "engine.json").read_text(encoding="utf-8"))
        self.assertEqual(engine["engine"], "2.0.0-alpha.1")
        self.assertEqual(engine["schema"], 1)
        bad = run(self.root, "append", stdin='{"v": 9}\n')
        self.assertEqual(bad.returncode, 2, bad.stderr)
        self.assertEqual((self.root / ".crav1-2" / "events.jsonl").read_bytes(), b"")
        event = note_event()
        event["data"]["passage_list"][0]["quote"] = "café — partner B says yes"
        event["data"]["passages"] = 1
        ok = run(self.root, "append", stdin=json.dumps(event, ensure_ascii=False) + "\n")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("café".encode(), (self.root / ".crav1-2" / "events.jsonl").read_bytes())
        again = run(self.root, "append", stdin=json.dumps(event) + "\n")
        self.assertEqual(again.returncode, 2)
        self.assertIn("duplicate id", again.stderr)
        before = snapshot(self.root)
        state = run(self.root, "show-state")
        lint = run(self.root, "lint")
        self.assertEqual(state.returncode, 0, state.stderr)
        self.assertEqual(lint.returncode, 0, lint.stderr)
        self.assertEqual(before, snapshot(self.root))
        body = json.loads(state.stdout)
        self.assertIn("2026-11-25-outbound-channel", body["notes"])
        self.assertIn("café — partner B says yes", json.dumps(body, ensure_ascii=False))
        rebuilt = run(self.root, "rebuild-views")
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertTrue((self.root / "sot" / "index.md").is_file())
        session = run(self.root, "session-park", "s-0008")
        self.assertEqual(session.returncode, 0, session.stderr)
        parked = json.loads((self.root / ".crav1-2" / "sessions" / "s-0008.json").read_text(encoding="utf-8"))
        self.assertEqual(parked["status"], "parked")
        flagged = run(self.root, "--flag")
        self.assertEqual(flagged.returncode, 2)
        self.assertIn("words", flagged.stderr)

    def test_second_init_keeps_events(self):
        run(self.root, "init")
        event = fact_event()
        # fact without a note still appends; schema does not require the note yet
        run(self.root, "append", stdin=json.dumps(note_event()) + "\n" + json.dumps(event) + "\n")
        before = (self.root / ".crav1-2" / "events.jsonl").read_bytes()
        again = run(self.root, "init")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual((self.root / ".crav1-2" / "events.jsonl").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
