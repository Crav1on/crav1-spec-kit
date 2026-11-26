"""Schema v1 accepts the phase-1 shape and refuses bad events."""

from __future__ import annotations

import copy
import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.errors import SchemaError
from crav1_2.schema import validate_event
from crav1_2.ulid import decode, encode, is_ulid, ulid

from support import fact_event, note_event, ulid_n


class Ulid(unittest.TestCase):
    def test_roundtrip_and_order(self):
        self.assertEqual(encode(0, 0), "0" * 26)
        self.assertEqual(decode(encode(0, 0)), (0, 0))
        first = encode(1_000, 1)
        second = encode(1_001, 1)
        self.assertLess(first, second)
        self.assertEqual(decode(first), (1_000, 1))
        self.assertTrue(is_ulid(ulid()))
        self.assertFalse(is_ulid("01JDX7K2M4"))
        self.assertTrue(is_ulid(ulid_n(3)))


class Accept(unittest.TestCase):
    def test_note_and_fact_with_utf8(self):
        event = note_event()
        event["data"]["passage_list"][0]["quote"] = "café — partner B says yes"
        cleaned = validate_event(event)
        self.assertEqual(cleaned["v"], 1)
        self.assertEqual(cleaned["data"]["passage_list"][0]["quote"], "café — partner B says yes")
        fact = fact_event()
        fact["data"]["quote"] = "café — partner B says yes"
        self.assertEqual(validate_event(fact)["data"]["weak"], "verbal")

    def test_from_sources_trailing_slash(self):
        event = note_event(from_sources="docs/sources/2026-11-25-outbound-channel/", passage_list=[
            {
                "id": "p-017",
                "path": "docs/sources/2026-11-25-outbound-channel/README.md",
                "lines": "L40-L42",
                "quote": "The feed stays on the current channel.",
            }
        ])
        cleaned = validate_event(event)
        self.assertEqual(cleaned["data"]["passages"], 1)
        self.assertEqual(cleaned["data"]["passage_list"][0]["lines"], "L40-L42")

    def test_zulu_time_is_an_offset(self):
        event = note_event()
        event["at"] = "2026-11-25T10:41:00Z"
        self.assertEqual(validate_event(event)["at"], "2026-11-25T10:41:00Z")


class Refuse(unittest.TestCase):
    def test_unknown_version_tells_the_user_to_update(self):
        event = note_event()
        event["v"] = 2
        with self.assertRaises(SchemaError) as caught:
            validate_event(event)
        self.assertIn("unknown events schema version 2", caught.exception.message)
        self.assertIn("Update kit 2.0", caught.exception.message)

    def test_missing_field_bad_type_extra_field_bad_time_bad_id(self):
        missing = note_event()
        del missing["data"]["date"]
        self._refuses(missing, "date")
        bad_type = note_event()
        bad_type["data"]["passages"] = True
        self._refuses(bad_type, "passages")
        extra = note_event()
        extra["data"]["extra"] = "no"
        self._refuses(extra, "extra")
        bad_time = note_event()
        bad_time["at"] = "2026-11-25T11:41:00"
        self._refuses(bad_time, "offset")
        bad_id = note_event()
        bad_id["id"] = "not-a-ulid"
        self._refuses(bad_id, "ULID")

    def test_mixed_origin_and_short_card(self):
        item = {
            "v": 1,
            "id": ulid_n(9),
            "at": "2026-11-25T12:04:41+01:00",
            "by": "engine",
            "run": "s-0008",
            "type": "item.linked",
            "data": {
                "item": "I-0017",
                "spec": "partner-b-feed",
                "file": "spec.md",
                "section": "Constraints",
                "text": "The channel is not built in this slice.",
                "origin": "src",
                "refs": ["F-0031", "D-0005"],
            },
        }
        self._refuses(item, "one origin")
        card = {
            "v": 1,
            "id": ulid_n(10),
            "at": "2026-11-25T12:03:00+01:00",
            "by": "engine",
            "run": "s-0008",
            "type": "card.asked",
            "data": {
                "card": "C-0003",
                "gap": "G-0012",
                "question": "Which way?",
                "options": [{"word": "only-one", "impact": "high", "undo": "drop it"}],
                "recommended": None,
                "missing_fact": "who can answer",
            },
        }
        self._refuses(card, "2 to 4")

    def _refuses(self, event, snippet):
        with self.assertRaises(SchemaError) as caught:
            validate_event(copy.deepcopy(event))
        self.assertIn(snippet, caught.exception.message)


if __name__ == "__main__":
    unittest.main()
