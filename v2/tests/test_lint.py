"""Lint reports unresolved ids, broken pointers, mixed origin, and MUST on asm items."""

from __future__ import annotations

import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.lint import lint_events
from crav1_2.schema import validate_event

from support import fact_event, note_event, temp_dir, ulid_n


def _item(origin: str, refs: list[str], text: str, n: int = 11) -> dict:
    return validate_event({
        "v": 1,
        "id": ulid_n(n),
        "at": "2026-11-25T12:08:00+01:00",
        "by": "engine",
        "run": "s-0008",
        "type": "item.linked",
        "data": {
            "item": "I-0017",
            "spec": "partner-b-feed",
            "file": "spec.md",
            "section": "Constraints",
            "text": text,
            "origin": origin,
            "refs": refs,
        },
    })


class Lint(unittest.TestCase):
    def test_clean_log_and_the_failures(self):
        note = note_event()
        fact = fact_event()
        clean = lint_events([validate_event(note), fact])
        self.assertEqual(clean, [])
        broken = lint_events([fact])
        self.assertEqual(broken[0]["code"], "broken-pointer")
        note_gap = validate_event(note)
        note_gap["data"]["passage_list"] = [{
            "id": "p-002",
            "kind": "chat",
            "who": "person A",
            "when": "09:12",
            "quote": "A different line.",
        }]
        note_gap["data"]["passages"] = 1
        mismatch = lint_events([validate_event(note_gap), fact])
        self.assertIn("p-001", mismatch[0]["message"])
        must = _item("asm", ["A-0001"], "The channel MUST stay closed.", 12)
        assumption = validate_event({
            "v": 1, "id": ulid_n(13), "at": "2026-11-25T12:01:00+01:00", "by": "engine", "run": "s-0008",
            "type": "assumption.recorded",
            "data": {
                "assumption": "A-0001", "gap": "G-0012", "text": "Partner B can wait.",
                "owner": "person A", "confirms_if": "a mail arrives", "breaks_if": "the date moves",
            },
        })
        gap = validate_event({
            "v": 1, "id": ulid_n(14), "at": "2026-11-25T12:00:00+01:00", "by": "engine", "run": "s-0008",
            "type": "gap.found",
            "data": {
                "gap": "G-0012", "spec": "partner-b-feed", "kind": "vague",
                "facts": ["F-0031"], "impact": 1, "uncertainty": 2, "holds": [],
            },
        })
        findings = lint_events([validate_event(note), fact, gap, assumption, must])
        self.assertIn("must-on-assumption", [row["code"] for row in findings])
        self.assertNotIn("origin-kind", [row["code"] for row in findings])

    def test_pointer_finds_a_quote_in_a_source_file(self):
        root = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        source = root / "docs" / "sources" / "2026-11-25-outbound-channel" / "README.md"
        source.parent.mkdir(parents=True)
        source.write_text("line\nThe feed stays on the current channel.\n", encoding="utf-8")
        note = note_event(from_sources="docs/sources/2026-11-25-outbound-channel/", passage_list=[{
            "id": "p-017",
            "path": "docs/sources/2026-11-25-outbound-channel/README.md",
            "lines": "L2-L2",
            "quote": "The feed stays on the current channel.",
        }])
        fact = fact_event()
        fact["data"]["passage"] = "p-017"
        fact["data"]["quote"] = "The feed stays on the current channel."
        self.assertEqual(lint_events([validate_event(note), validate_event(fact)], root), [])
        fact["data"]["quote"] = "this quote is gone"
        fact = validate_event(fact)
        gone = lint_events([validate_event(note), fact], root)
        self.assertEqual(gone[0]["code"], "broken-pointer")


if __name__ == "__main__":
    unittest.main()
