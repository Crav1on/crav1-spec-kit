"""Generated pages rebuild to the same bytes, including passage anchors."""

from __future__ import annotations

import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.fold import fold_events
from crav1_2.notes import render_note
from crav1_2.repo import init_repo, rebuild_views
from crav1_2.schema import validate_event
from crav1_2.views import view_files

from support import fact_event, note_event, temp_dir, ulid_n


def _events() -> list[dict]:
    note = note_event()
    note["data"]["know"] = [{
        "heading": "Which options are realistic before go-live?",
        "body": "The channel is agreed long term. Every claim cites passages: [p-001].",
        "cites": ["p-001"],
    }]
    note["data"]["passage_list"].append({
        "id": "p-017",
        "kind": "session",
        "who": "person A",
        "quote": "Not in this slice.",
    })
    note["data"]["passages"] = len(note["data"]["passage_list"])
    later = note_event(30)
    later["data"] = {
        "note": "2026-11-26-gateway",
        "kinds": ["mail"],
        "date": "2026-11-26",
        "files": [],
        "from_sources": None,
        "passages": 0,
        "title": "Gateway",
        "added_by": "person A",
    }
    later["at"] = "2026-11-26T09:00:00+01:00"
    fact = fact_event()
    fact["data"]["quote"] = "café — partner B says yes"
    gap = validate_event({
        "v": 1, "id": ulid_n(3), "at": "2026-11-25T12:02:11+01:00", "by": "engine", "run": "s-0008",
        "type": "gap.found",
        "data": {
            "gap": "G-0012", "spec": "partner-b-feed", "kind": "conflicting",
            "facts": ["F-0031"], "impact": 3, "uncertainty": 3, "holds": ["T12"],
        },
    })
    card = validate_event({
        "v": 1, "id": ulid_n(4), "at": "2026-11-25T12:03:00+01:00", "by": "engine", "run": "s-0008",
        "type": "card.asked",
        "data": {
            "card": "C-0003", "gap": "G-0012", "question": "Which way does partner B go?",
            "options": [
                {"word": "ask-security-owner", "impact": "T12 waits", "undo": "ask again"},
                {"word": "keep-current-rule", "impact": "no change", "undo": "reopen"},
            ],
            "recommended": "ask-security-owner",
            "facts": ["F-0031"],
        },
    })
    decision = validate_event({
        "v": 1, "id": ulid_n(5), "at": "2026-11-25T12:04:40+01:00", "by": "user", "run": "s-0008",
        "type": "decision.recorded",
        "data": {
            "decision": "D-0005", "card": "C-0003", "chosen": "ask-security-owner",
            "over": ["keep-current-rule"], "accepting": "T12 waits for the answer",
            "facts": ["F-0031"], "affects": ["T12"], "check": "T12 has a recorded security answer before it starts",
        },
    })
    superseded = validate_event({
        "v": 1, "id": ulid_n(6), "at": "2026-11-25T12:05:00+01:00", "by": "engine", "run": "s-0008",
        "type": "decision.superseded", "data": {"decision": "D-0005", "by": "D-0005"},
    })
    assumption = validate_event({
        "v": 1, "id": ulid_n(7), "at": "2026-11-25T12:06:00+01:00", "by": "engine", "run": "s-0008",
        "type": "assumption.recorded",
        "data": {
            "assumption": "A-0001", "gap": "G-0012", "text": "Partner B can wait.",
            "owner": "person A", "confirms_if": "a mail arrives", "breaks_if": "the date moves",
        },
    })
    closed = validate_event({
        "v": 1, "id": ulid_n(8), "at": "2026-11-25T12:07:00+01:00", "by": "engine", "run": "s-0008",
        "type": "assumption.closed", "data": {"assumption": "A-0001", "by": "D-0005"},
    })
    return [validate_event(note), later, fact, gap, card, decision, superseded, assumption, closed]


class Render(unittest.TestCase):
    def test_anchors_index_order_and_superseded(self):
        files = view_files(fold_events(_events()))
        note = files["sot/2026-11-25-outbound-channel/note.md"]
        self.assertIn('<a id="p-001"></a>**p-001** · chat · person A, 09:12 · "Agreed long term, likely before go-live, not in this slice."', note)
        self.assertIn('<a id="p-017"></a>**p-017** · session · person A · "Not in this slice."', note)
        self.assertIn("## Know about this", note)
        self.assertIn("### Which options are realistic before go-live?", note)
        self.assertLess(
            files["sot/index.md"].index("2026-11-26-gateway"),
            files["sot/index.md"].index("2026-11-25-outbound-channel"),
        )
        self.assertIn('**F-0031** → [sot/2026-11-25-outbound-channel/note.md#p-001]', files["sot/facts.md"])
        self.assertIn("café — partner B says yes", files["sot/facts.md"])
        self.assertIn("Superseded by D-0005", files["sot/decisions.md"])
        self.assertIn("## Closed", files["sot/assumptions.md"])
        self.assertIn("closed by D-0005", files["sot/assumptions.md"])
        self.assertNotIn("\r\n", note)

    def test_thin_note_anchor(self):
        text = render_note({
            "note": "2026-11-25-outbound-channel",
            "title": "Outbound",
            "kinds": ["document"],
            "date": "2026-11-25",
            "files": [],
            "from_sources": "docs/sources/2026-11-25-outbound-channel/",
            "passages": 1,
            "passage_list": [{
                "id": "p-017",
                "path": "docs/sources/2026-11-25-outbound-channel/README.md",
                "lines": "L40-L42",
                "quote": "The feed stays on the current channel.",
            }],
        })
        self.assertIn(
            '<a id="p-017"></a>**p-017** · `docs/sources/2026-11-25-outbound-channel/README.md` L40-L42 · "The feed stays on the current channel."',
            text,
        )

    def test_delete_and_rebuild_is_byte_identical(self):
        root = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        init_repo(root)
        from crav1_2.repo import append_events

        append_events(root, _events())
        rebuild_views(root)
        first = _snapshot(root)
        for rel in list(first):
            if rel.startswith("sot/"):
                (root / rel).unlink()
        rebuild_views(root)
        self.assertEqual(first, _snapshot(root))
        again = view_files(fold_events(_events()))
        self.assertEqual(view_files(fold_events(list(reversed(_events())))), again)


def _snapshot(root) -> dict[str, bytes]:
    out = {}
    for path in (root / "sot").rglob("*"):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = path.read_bytes()
    return out


if __name__ == "__main__":
    unittest.main()
