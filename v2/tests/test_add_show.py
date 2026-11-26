"""add-to-sot, this-session, and show-sot. Synthetic data only."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.cards import build_keep_card, card_problems
from support import REPO, V2, temp_dir

SPEC = """## Constraints
- The feed to partner B runs over the existing secure channel.

## Open questions
- Who gets the certificate-expiry alert, and how early?
  Blocks: T9
"""

ANSWER = "The certificate expiry alert goes to person A two weeks before it lapses."
FINDING = "The gateway stays on the current channel for this slice."
ASSISTANT = "Partner B already signed the gateway change."
QUESTION = "Who gets the certificate-expiry alert, and how early?"


def run(repo, *args, stdin=None):
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "crav1_2", *args],
        cwd=repo,
        input=stdin,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": str(V2)},
    )


def snapshot(repo):
    out = {}
    for path in repo.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            out[path.relative_to(repo).as_posix()] = path.read_bytes()
    return out


def changed(before, after):
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def init(repo):
    created = run(repo, "init")
    assert created.returncode == 0, created.stderr
    built = run(repo, "rebuild-views")
    assert built.returncode == 0, built.stderr


def body_of(result):
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class Capture(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        init(self.root)

    def test_session_chat_writes_one_note_one_event_and_the_index(self):
        staging = self.root / "staging"
        staging.mkdir()
        originals = []
        for number in range(1, 5):
            name = f"screenshot-{number}.png"
            data = b"\x89PNG\r\n\x1a\nstand-in-" + str(number).encode()
            (staging / name).write_bytes(data)
            originals.append({"name": name, "from": str(staging / name)})
        session = "Person A, 09:12: The outbound channel is agreed long term.\nPerson A: Not in this slice.\n"
        (staging / "session.md").write_text(session, encoding="utf-8")
        originals.append({"name": "session.md", "from": str(staging / "session.md")})
        payload = {
            "title": "Outbound messaging channel and gateway options",
            "date": "2026-11-25",
            "added_by": "person A",
            "slug": "outbound-channel",
            "at": "2026-11-25T11:41:00+01:00",
            "extractor": {
                "passages": [
                    {
                        "kind": "chat",
                        "who": "person A",
                        "when": "09:12",
                        "quote": "The outbound channel is agreed long term.",
                    },
                    {"kind": "session", "who": "person A", "quote": "Not in this slice."},
                ],
                "know": [{
                    "heading": "Which options are realistic before go-live?",
                    "body": "The channel is agreed long term.",
                    "cites": [0, 1],
                }],
            },
            "originals": originals,
        }
        before = snapshot(self.root)
        dry = run(self.root, "add-to-sot", "session", "chat", "dry-run", stdin=json.dumps(payload))
        preview = body_of(dry)
        self.assertTrue(preview["dry_run"])
        self.assertFalse(preview["wrote"])
        self.assertIn("The outbound channel is agreed long term.", preview["note_markdown"])
        self.assertEqual(preview["events"][0]["type"], "note.added")
        self.assertEqual(changed(before, snapshot(self.root)), [])
        result = run(self.root, "add-to-sot", "session", "chat", stdin=json.dumps(payload))
        written = body_of(result)
        self.assertTrue(written["wrote"])
        self.assertTrue(written["ending"].startswith("Run next:"))
        self.assertNotIn("\nNext:", "\n" + written["ending"])
        self.assertEqual(written["ending"].count("Also recorded:"), 1)
        note_id = "2026-11-25-outbound-channel"
        self.assertEqual(written["note_id"], note_id)
        diff = changed(before, snapshot(self.root))
        expected = [
            ".crav1-2/events.jsonl",
            "sot/index.md",
            f"sot/{note_id}/note.md",
            f"sot/{note_id}/session.md",
        ] + [f"sot/{note_id}/screenshot-{number}.png" for number in range(1, 5)]
        self.assertEqual(diff, sorted(expected))
        events = [
            json.loads(line)
            for line in (self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "note.added")
        self.assertEqual(events[0]["data"]["kinds"], ["session", "chat"])
        self.assertEqual(events[0]["data"]["passages"], 2)
        self.assertEqual(len(events[0]["data"]["know"]), 1)
        self.assertIsNone(events[0]["data"]["from_sources"])
        note = (self.root / "sot" / note_id / "note.md").read_text(encoding="utf-8")
        self.assertIn("## Know about this", note)
        self.assertIn("Cites: [p-001], [p-002]", note)
        self.assertIn("## Passages", note)
        self.assertIn('<a id="p-001"></a>', note)
        self.assertIn('<a id="p-002"></a>', note)
        index = (self.root / "sot" / "index.md").read_text(encoding="utf-8")
        self.assertIn(note_id, index)
        self.assertIn("session, chat", index)
        for number in range(1, 5):
            name = f"screenshot-{number}.png"
            self.assertEqual((self.root / "sot" / note_id / name).read_bytes(), (staging / name).read_bytes())
        self.assertEqual((self.root / "sot" / note_id / "session.md").read_bytes(), session.encode())
        self.assertEqual(list((self.root / ".crav1-2" / "sessions").glob("*.json")), [])
        markdown = {
            rel: data
            for rel, data in snapshot(self.root).items()
            if rel in {"sot/index.md", "sot/facts.md", "sot/decisions.md", "sot/assumptions.md"}
            or rel.endswith("/note.md")
        }
        for rel in markdown:
            (self.root / rel).unlink()
        rebuilt = run(self.root, "rebuild-views")
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        after = snapshot(self.root)
        for rel, data in markdown.items():
            self.assertEqual(after[rel], data, rel)

    def test_from_sources_writes_a_thin_note_and_copies_nothing(self):
        folder = self.root / "docs" / "sources" / "2026-11-25-outbound-channel"
        folder.mkdir(parents=True)
        source = folder / "README.md"
        source.write_text("Intro\nThe feed stays on the current channel.\n", encoding="utf-8")
        before_source = source.read_bytes()
        payload = {
            "title": "Outbound messaging channel",
            "date": "2026-11-25",
            "slug": "outbound-channel",
            "at": "2026-11-25T11:41:00+01:00",
            "from_sources": "docs/sources/2026-11-25-outbound-channel/",
            "extractor": {
                "passages": [{
                    "path": "docs/sources/2026-11-25-outbound-channel/README.md",
                    "quote": "The feed stays on the current channel.",
                }]
            },
        }
        result = run(self.root, "add-to-sot", "from-sources", stdin=json.dumps(payload))
        written = body_of(result)
        note_id = written["note_id"]
        note = (self.root / "sot" / note_id / "note.md").read_text(encoding="utf-8")
        self.assertIn("`docs/sources/2026-11-25-outbound-channel/README.md` L2-L2", note)
        self.assertIn("The feed stays on the current channel.", note)
        names = sorted(path.name for path in (self.root / "sot" / note_id).iterdir())
        self.assertEqual(names, ["note.md"])
        self.assertEqual(source.read_bytes(), before_source)
        event = json.loads((self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8").strip())
        self.assertEqual(event["data"]["from_sources"], "docs/sources/2026-11-25-outbound-channel/")
        self.assertEqual(event["data"]["files"], [])

    def test_missing_word_stops_and_lists_the_words(self):
        before = snapshot(self.root)
        missing = run(self.root, "add-to-sot")
        self.assertEqual(missing.returncode, 2)
        for word in ("mail", "chat", "meeting", "session", "document", "fact", "from-sources", "this-session", "dry-run"):
            self.assertIn(word, missing.stderr)
        unknown = run(self.root, "add-to-sot", "banana")
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("banana", unknown.stderr)
        self.assertEqual(changed(before, snapshot(self.root)), [])

    def test_show_sot_writes_nothing(self):
        payload = {
            "title": "Outbound messaging channel",
            "date": "2026-11-25",
            "slug": "outbound-channel",
            "extractor": {"passages": [{"kind": "fact", "who": "person A", "quote": "The feed stays on the current channel."}]},
        }
        self.assertEqual(run(self.root, "add-to-sot", "fact", stdin=json.dumps(payload)).returncode, 0)
        before = snapshot(self.root)
        shown = body_of(run(self.root, "show-sot"))
        self.assertFalse(shown["wrote"])
        self.assertIn("2026-11-25-outbound-channel", shown["text"])
        named = body_of(run(self.root, "show-sot", "none"))
        self.assertEqual(named["text"], shown["text"])
        self.assertFalse(named["wrote"])
        facts = body_of(run(self.root, "show-sot", "facts"))
        self.assertIn("(none)", facts["text"])
        about = body_of(run(self.root, "show-sot", "about-channel"))
        self.assertIn("The feed stays on the current channel.", about["text"])
        bad = run(self.root, "show-sot", "banana")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("about-<topic>", bad.stderr)
        self.assertEqual(changed(before, snapshot(self.root)), [])

    def test_secret_value_is_not_stored(self):
        payload = {
            "title": "A token arrived",
            "date": "2026-11-25",
            "slug": "token-arrived",
            "extractor": {
                "passages": [{
                    "kind": "document",
                    "who": "person A",
                    "quote": "The api_key=supersecretvalue must stay out of the note.",
                }]
            },
            "originals": [{"name": "mail.md", "text": "api_key=supersecretvalue\n"}],
        }
        result = body_of(run(self.root, "add-to-sot", "document", stdin=json.dumps(payload)))
        blob = b"".join(snapshot(self.root).values())
        self.assertNotIn(b"supersecretvalue", blob)
        note = (self.root / "sot" / result["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("[redacted: secret]", note)
        self.assertIn("Redactions: secret", note)

    def test_bad_original_name_is_refused(self):
        before = snapshot(self.root)
        payload = {
            "title": "Nope",
            "date": "2026-11-25",
            "extractor": {"passages": [{"kind": "document", "who": "person A", "quote": "A line."}]},
            "originals": [{"name": "../secret.txt", "text": "no"}],
        }
        refused = run(self.root, "add-to-sot", "document", stdin=json.dumps(payload))
        self.assertEqual(refused.returncode, 2)
        self.assertFalse((self.root.parent / "secret.txt").exists())
        self.assertEqual(changed(before, snapshot(self.root)), [])


class ThisSession(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.home = temp_dir()
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(self.home, ignore_errors=True))
        init(self.root)
        spec = self.root / "docs" / "specs" / "partner-b-feed" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(SPEC, encoding="utf-8")
        self.spec_bytes = spec.read_bytes()
        encoded = self.root.resolve().as_posix().replace("/", "-")
        folder = self.home / ".claude" / "projects" / encoded
        folder.mkdir(parents=True)
        line = {
            "type": "user",
            "message": {"role": "user", "content": ANSWER},
            "timestamp": "2026-11-26T10:02:00Z",
        }
        self.jsonl = folder / "sess.jsonl"
        self.jsonl.write_text(json.dumps(line) + "\n", encoding="utf-8")

    def _payload(self, **extra):
        payload = {
            "title": "Certificate alert",
            "date": "2026-11-26",
            "slug": "certificate-alert",
            "added_by": "person A",
            "vendor": "claude",
            "session_id": "sess-synthetic-1",
            "home": str(self.home),
            "at": "2026-11-26T10:05:00+01:00",
            "extractor": {
                "passages": [
                    {"kind": "session", "who": "user", "label": "finding", "quote": FINDING},
                    {
                        "kind": "session",
                        "who": "user",
                        "label": "answer",
                        "quote": ANSWER,
                        "answers": "who gets the certificate expiry alert",
                    },
                    {"kind": "session", "who": "assistant", "label": "decision", "quote": ASSISTANT},
                ]
            },
        }
        payload.update(extra)
        return payload

    def test_claude_checks_quotes_and_a_parked_run_resumes(self):
        parked = body_of(run(self.root, "add-to-sot", "this-session", stdin=json.dumps(self._payload())))
        self.assertFalse(parked["wrote"])
        self.assertIsNone(parked["ending"])
        self.assertEqual(parked["card"]["recommended"], "keep-all")
        self.assertTrue(parked["card"]["facts"])
        self.assertIn("(Recommended)", parked["card_text"])
        self.assertIn("unverified", parked["proposal"])
        self.assertFalse((self.root / "sot").joinpath("2026-11-26-certificate-alert", "note.md").exists())
        session = next((self.root / ".crav1-2" / "sessions").glob("s-*.json"))
        stored = json.loads(session.read_text(encoding="utf-8"))
        self.assertEqual(stored["status"], "parked")
        self.jsonl.unlink()
        resumed = body_of(run(
            self.root,
            "add-to-sot",
            "this-session",
            "keep-all",
            stdin=json.dumps({"card": "keep-all"}),
        ))
        self.assertTrue(resumed["wrote"])
        self.assertTrue(resumed["ending"].startswith("Run next:"))
        self.assertIn("`/crav1-2-link-to-spec partner-b-feed`", resumed["ending"])
        self.assertNotRegex(resumed["ending"], r"(?m)^Next:")
        self.assertEqual(resumed["ending"].count("Also recorded:"), 1)
        note = (self.root / "sot" / resumed["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("Quotes: checked against the session file.", note)
        self.assertIn("· verified ·", note)
        self.assertIn("· unverified ·", note)
        self.assertIn("ai-summary", note)
        self.assertIn(f"answers: who gets the certificate expiry alert", note)
        self.assertIn("Captured from: live context", note)
        self.assertIn("Vendor: claude", note)
        events = [
            json.loads(line)
            for line in (self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        kinds = [event["type"] for event in events]
        self.assertEqual(kinds[0], "note.added")
        self.assertIn("fact.cited", kinds)
        self.assertIn("answer.matched", kinds)
        matched = next(event for event in events if event["type"] == "answer.matched")
        self.assertEqual(matched["data"]["question"], QUESTION)
        self.assertEqual(matched["data"]["spec"], "partner-b-feed")
        self.assertEqual((self.root / "docs" / "specs" / "partner-b-feed" / "spec.md").read_bytes(), self.spec_bytes)
        self.assertNotIn(b"Answered:", self.spec_bytes)
        ended = json.loads(session.read_text(encoding="utf-8"))
        self.assertEqual(ended["status"], "ended")
        again = self._payload(at="2026-11-26T18:00:00+01:00")
        again["extractor"]["passages"].append({
            "kind": "session", "who": "user", "label": "open", "quote": "Person A still owes the expiry owner.",
        })
        extended = body_of(run(self.root, "add-to-sot", "this-session", "keep-all", stdin=json.dumps(again)))
        self.assertEqual(extended["note_id"], resumed["note_id"])
        more = [
            json.loads(line)
            for line in (self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(more[-1]["type"], "note.extended")
        self.assertEqual(more[-1]["data"]["passages"], 1)
        text = (self.root / "sot" / resumed["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(ANSWER), 1)
        self.assertIn("Person A still owes the expiry owner.", text)
        self.assertIn('<a id="p-004"></a>', text)

    def test_cursor_marks_quotes_unchecked_even_when_a_file_has_them(self):
        payload = self._payload(vendor="cursor", session_file=str(self.jsonl))
        result = body_of(run(self.root, "add-to-sot", "this-session", "keep-all", stdin=json.dumps(payload)))
        self.assertIsNone(result["card"]["recommended"])
        self.assertNotIn("facts", result["card"])
        self.assertIn("Missing fact", result["card_text"] if result["card_text"] else "Missing fact: " + result["card"]["missing_fact"])
        self.assertNotIn("(Recommended)", result.get("card_text") or "")
        note = (self.root / "sot" / result["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("Quotes: not checked against a file.", note)
        self.assertNotIn("· verified ·", note)
        self.assertNotIn("· unverified ·", note)
        self.assertIn("ai-summary", note)
        events = (self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn("answer.matched", events)
        self.assertNotIn("fact.cited", events)
        self.assertEqual((self.root / "docs" / "specs" / "partner-b-feed" / "spec.md").read_bytes(), self.spec_bytes)

    def test_codex_session_file_verifies_a_quote(self):
        quote = "Person A keeps the feed on the current channel."
        path = self.home / ".codex" / "sessions" / "2026" / "11" / "26" / "rollout.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"cwd": self.root.resolve().as_posix(), "text": quote}) + "\n", encoding="utf-8")
        payload = {
            "title": "Feed stays",
            "date": "2026-11-26",
            "slug": "feed-stays",
            "vendor": "codex",
            "home": str(self.home),
            "extractor": {"passages": [{"kind": "session", "who": "user", "label": "finding", "quote": quote}]},
        }
        result = body_of(run(self.root, "add-to-sot", "this-session", "keep-all", stdin=json.dumps(payload)))
        note = (self.root / "sot" / result["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("Quotes: checked against the session file.", note)
        self.assertIn("· verified ·", note)

    def test_dry_run_and_stop_write_nothing(self):
        before = snapshot(self.root)
        dry = body_of(run(self.root, "add-to-sot", "this-session", "dry-run", stdin=json.dumps(self._payload())))
        self.assertTrue(dry["dry_run"])
        self.assertIn("`/crav1-2-link-to-spec partner-b-feed`", dry["ending"])
        self.assertNotIn("Also recorded:", dry["ending"])
        self.assertIn(ANSWER, dry["note_markdown"])
        self.assertIn("· verified ·", dry["note_markdown"])
        self.assertIn("· unverified ·", dry["note_markdown"])
        stopped = body_of(run(self.root, "add-to-sot", "this-session", "stop", stdin=json.dumps(self._payload())))
        self.assertFalse(stopped["wrote"])
        self.assertTrue(stopped["ending"].startswith("Run next: nothing needed now."))
        self.assertNotIn("Also recorded:", stopped["ending"])
        self.assertEqual(changed(before, snapshot(self.root)), [])

    def test_pick_some_keeps_the_numbered_line(self):
        result = body_of(run(
            self.root,
            "add-to-sot",
            "this-session",
            "pick-some",
            "2",
            stdin=json.dumps(self._payload()),
        ))
        note = (self.root / "sot" / result["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn(ANSWER, note)
        self.assertNotIn(FINDING, note)
        self.assertNotIn(ASSISTANT, note)
        self.assertIn('<a id="p-001"></a>', note)
        self.assertNotIn("p-002", note)


class Cards(unittest.TestCase):
    def test_a_recommendation_needs_a_backing_fact(self):
        empty = build_keep_card([])
        self.assertIsNone(empty["recommended"])
        self.assertNotIn("facts", empty)
        self.assertEqual(card_problems(empty), [])
        backed = build_keep_card(["F-0001"])
        self.assertEqual(backed["recommended"], "keep-all")
        self.assertEqual(backed["facts"], ["F-0001"])
        self.assertEqual(card_problems(backed), [])
        self.assertEqual(len(backed["options"]), 3)
        for option in backed["options"]:
            self.assertRegex(option["word"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertTrue(option["impact"])
            self.assertTrue(option["undo"])
        bare = dict(backed)
        bare.pop("facts")
        self.assertTrue(card_problems(bare))
        short = dict(empty)
        short["options"] = short["options"][:1]
        self.assertTrue(any("2 to 4" in problem for problem in card_problems(short)))


class OneX(unittest.TestCase):
    def test_v1_names_do_not_match_crav1_2(self):
        import re

        pattern = re.compile(r"crav1-[a-z]")
        for name in ("crav1-2-add-to-sot", "crav1-2-show-sot", "crav1-2-link-to-spec", "crav1-2-source-extractor-agent", "crav1-2-gap-finder-agent"):
            self.assertIsNone(pattern.match(name), name)
        self.assertIsNotNone(pattern.match("crav1-help"))
        lint = (REPO / "scripts" / "kit-lint.py").read_text(encoding="utf-8")
        docs = (REPO / "scripts" / "gen-skill-docs.py").read_text(encoding="utf-8")
        sync = (REPO / "scripts" / "sync-crav1-claude.py").read_text(encoding="utf-8")
        for text in (lint, docs, sync):
            self.assertIn("crav1-[a-z]", text)


if __name__ == "__main__":
    unittest.main()
