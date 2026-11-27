"""add-to-sot, this-session, and show-sot. Synthetic data only."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from datetime import datetime

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


def run(repo, *args, stdin=None, env=None):
    base = {**os.environ, "PYTHONPATH": str(V2)}
    if env:
        base.update(env)
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "crav1_2", *args],
        cwd=repo,
        input=stdin,
        text=True,
        capture_output=True,
        env=base,
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


def git_identity(repo, name="Alex Example"):
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", name], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "alex@example.com"], cwd=repo, check=True)


def body_of(result):
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class Capture(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        init(self.root)
        git_identity(self.root)

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
        git_identity(self.root)
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


class MailCapture(unittest.TestCase):
    """Mail passages keep their day, the runner, the .eml, and real names."""

    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        init(self.root)
        git_identity(self.root)
        self.inbox = self.root / "inbox"
        self.inbox.mkdir()
        self.eml = self.inbox / "thread.eml"
        self.eml.write_text(
            "From: Jordan Example <jordan@example.com>\n"
            "Date: Tue, 24 Nov 2026 15:57:00 +0100\n"
            "\n"
            "Jordan Example <jordan@example.com> said the channel is agreed.\n"
            "api_key=supersecretvalue\n",
            encoding="utf-8",
        )
        self.quote = "Jordan Example <jordan@example.com> said the channel is agreed."

    def _spec(self, slug):
        path = self.root / "docs" / "specs" / slug / "spec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("## Constraints\n- The channel stays.\n", encoding="utf-8")
        return path

    def _payload(self, **extra):
        payload = {
            "title": "Outbound channel",
            "date": "2026-11-24",
            "slug": "outbound-channel",
            "source": "inbox/thread.eml",
            "extractor": {
                "passages": [
                    {
                        "kind": "mail",
                        "who": "Jordan Example",
                        "when": "2026-11-24 15:57+01:00",
                        "quote": self.quote,
                    },
                    {
                        "kind": "mail",
                        "who": "Jordan Example",
                        "when": "09:12",
                        "quote": "The same-day line keeps the clock time.",
                    },
                ]
            },
        }
        payload.update(extra)
        return payload

    def test_mail_keeps_the_day_the_runner_the_file_and_the_names(self):
        spec = self._spec("partner-b-feed")
        before_spec = spec.read_bytes()
        today = datetime.now().astimezone().date().isoformat()
        dry = body_of(run(self.root, "add-to-sot", "mail", "dry-run", stdin=json.dumps(self._payload())))
        self.assertFalse(dry["wrote"])
        self.assertTrue(dry["ending"].startswith("Run next:"))
        self.assertIn('`/crav1-add-to-spec partner-b-feed mail "inbox/thread.eml"`', dry["ending"])
        self.assertNotIn("Pick one:", dry["ending"])
        self.assertNotRegex(dry["ending"], r"(?m)^Next:")
        self.assertFalse((self.root / "sot").exists() and any((self.root / "sot").rglob("thread.eml")))
        written = body_of(run(self.root, "add-to-sot", "mail", stdin=json.dumps(self._payload())))
        self.assertTrue(written["wrote"])
        self.assertEqual(written["note_id"], "2026-11-24-outbound-channel")
        note = (self.root / "sot" / written["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("Date: 2026-11-24 · Added: %s by Alex Example" % today, note)
        if today != "2026-11-24":
            self.assertNotIn("Added: 2026-11-24 by", note)
        self.assertIn("Jordan Example, 2026-11-24 15:57+01:00", note)
        self.assertIn("Jordan Example, 09:12", note)
        self.assertIn(self.quote, note)
        self.assertIn("Originals: thread.eml", note)
        self.assertNotIn("[redacted: personal data]", note)
        copied = (self.root / "sot" / written["note_id"] / "thread.eml").read_text(encoding="utf-8")
        self.assertIn("Jordan Example", copied)
        self.assertIn("jordan@example.com", copied)
        self.assertNotIn("supersecretvalue", copied)
        self.assertIn("[redacted: secret]", copied)
        stored = {
            rel: data
            for rel, data in snapshot(self.root).items()
            if rel.startswith("sot/") or rel.startswith(".crav1-2/")
        }
        blob = b"".join(stored.values())
        self.assertNotIn(b"supersecretvalue", blob)
        self.assertNotIn(b"[redacted: personal data]", blob)
        self.assertIn(b"supersecretvalue", (self.root / "inbox" / "thread.eml").read_bytes())
        self.assertEqual(spec.read_bytes(), before_spec)
        self.assertIn('`/crav1-add-to-spec partner-b-feed mail "inbox/thread.eml"`', written["ending"])
        self.assertEqual(written["ending"].count("Also recorded:"), 1)
        event = json.loads((self.root / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8").strip())
        self.assertEqual(event["data"]["added"], today)
        self.assertEqual(event["data"]["added_by"], "Alex Example")
        self.assertEqual(event["data"]["date"], "2026-11-24")
        self.assertEqual(event["data"]["passage_list"][0]["when"], "2026-11-24 15:57+01:00")
        self.assertEqual(event["data"]["files"], ["thread.eml"])

    def test_eml_word_is_copied_when_the_extractor_omits_it(self):
        payload = self._payload()
        del payload["source"]
        written = body_of(run(
            self.root, "add-to-sot", "mail", "inbox/thread.eml", stdin=json.dumps(payload),
        ))
        copied = self.root / "sot" / written["note_id"] / "thread.eml"
        self.assertTrue(copied.is_file())
        self.assertNotIn("supersecretvalue", copied.read_text(encoding="utf-8"))
        self.assertIn('mail "inbox/thread.eml"', written["ending"])

    def test_added_by_cannot_be_a_speaker(self):
        before = snapshot(self.root)
        refused = run(self.root, "add-to-sot", "mail", stdin=json.dumps(self._payload(added_by="jordan example")))
        self.assertEqual(refused.returncode, 2)
        self.assertIn("not a speaker label", refused.stderr)
        self.assertEqual(changed(before, snapshot(self.root)), [])
        subprocess.run(["git", "config", "user.name", "Jordan Example"], cwd=self.root, check=True)
        after_rename = snapshot(self.root)
        again = run(self.root, "add-to-sot", "mail", stdin=json.dumps(self._payload()))
        self.assertEqual(again.returncode, 2, again.stderr)
        self.assertIn("not a speaker label", again.stderr)
        self.assertEqual(changed(after_rename, snapshot(self.root)), [])
        named = body_of(run(
            self.root, "add-to-sot", "mail", stdin=json.dumps(self._payload(added_by="Sam Example")),
        ))
        note = (self.root / "sot" / named["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("by Sam Example", note)
        self.assertNotIn("by Jordan Example", note)
        self.assertNotIn("by Alex Example", note)

    def test_missing_runner_name_is_refused(self):
        root = temp_dir()
        home = temp_dir()
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(home, ignore_errors=True))
        init(root)
        inbox = root / "inbox"
        inbox.mkdir()
        (inbox / "thread.eml").write_text("Hello from Jordan Example.\n", encoding="utf-8")
        payload = {
            "title": "Outbound channel",
            "date": "2026-11-24",
            "slug": "outbound-channel",
            "source": "inbox/thread.eml",
            "extractor": {
                "passages": [{
                    "kind": "mail",
                    "who": "Jordan Example",
                    "when": "2026-11-24 15:57",
                    "quote": "Hello from Jordan Example.",
                }]
            },
        }
        refused = run(
            root,
            "add-to-sot",
            "mail",
            stdin=json.dumps(payload),
            env={
                "HOME": str(home),
                "GIT_CONFIG_GLOBAL": str(home / "none"),
                "GIT_CONFIG_NOSYSTEM": "1",
            },
        )
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn("git user.name", refused.stderr)
        self.assertFalse((root / "sot").exists() and any((root / "sot").rglob("note.md")))

    def test_run_next_asks_when_the_spec_is_not_clear(self):
        self._spec("gateway-options")
        self._spec("partner-b-feed")
        vague = body_of(run(self.root, "add-to-sot", "mail", stdin=json.dumps(self._payload())))
        ending = vague["ending"]
        self.assertTrue(ending.startswith("Run next:"))
        self.assertIn('`/crav1-add-to-spec <spec-slug> mail "inbox/thread.eml"`', ending)
        self.assertIn("Which spec should this mail go into? Pick one: gateway-options, partner-b-feed.", ending)
        self.assertNotRegex(ending, r"(?m)^Next:")
        self.assertNotIn("edit ", ending)
        named = self._payload()
        named["extractor"]["passages"][0]["quote"] = "The partner-b-feed channel is agreed."
        clear = body_of(run(self.root, "add-to-sot", "mail", stdin=json.dumps(named)))
        self.assertIn('`/crav1-add-to-spec partner-b-feed mail "inbox/thread.eml"`', clear["ending"])
        self.assertNotIn("Pick one:", clear["ending"])
        self.assertNotIn("<spec-slug>", clear["ending"])

    def test_fact_suggestion_has_no_file_and_names_are_not_redacted(self):
        from crav1_2.redact import redact_text

        self._spec("partner-b-feed")
        text, kinds = redact_text("Jordan Example <jordan@example.com> set api_key=supersecretvalue")
        self.assertIn("Jordan Example", text)
        self.assertIn("jordan@example.com", text)
        self.assertNotIn("supersecretvalue", text)
        self.assertNotIn("[redacted: personal data]", text)
        self.assertEqual(kinds, ["secret"])
        payload = {
            "title": "Outbound channel",
            "date": "2026-11-24",
            "slug": "outbound-channel",
            "extractor": {"passages": [{
                "kind": "fact",
                "who": "Jordan Example",
                "quote": "Jordan Example keeps the channel on the current path.",
            }]},
        }
        written = body_of(run(self.root, "add-to-sot", "fact", stdin=json.dumps(payload)))
        self.assertIn("`/crav1-add-to-spec partner-b-feed fact`", written["ending"])
        self.assertNotIn(".eml", written["ending"])
        note = (self.root / "sot" / written["note_id"] / "note.md").read_text(encoding="utf-8")
        self.assertIn("Jordan Example keeps the channel", note)

    def test_instructions_keep_names_and_do_not_run_the_suggestion(self):
        skill = (V2 / "skills" / "crav1-2-add-to-sot" / "SKILL.md").read_text(encoding="utf-8")
        capture = (V2 / "skills" / "crav1-2-add-to-sot" / "references" / "capture.md").read_text(encoding="utf-8")
        agent = (V2 / "agents" / "crav1-2-source-extractor-agent.md").read_text(encoding="utf-8")
        self.assertIn("Do not run it.", skill)
        self.assertIn("personal data]", skill)
        self.assertIn("YYYY-MM-DD HH:MM", capture)
        self.assertIn("HH:MM", capture)
        self.assertIn("`source`", capture)
        self.assertIn("git config user.name", capture)
        self.assertNotIn("Use person A, person B", capture)
        self.assertIn("YYYY-MM-DD HH:MM", agent)
        self.assertIn("[redacted: personal data]", agent)
        self.assertNotIn("Use person A, person B, and partner B.", agent)


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
