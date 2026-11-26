"""Fold drops duplicate ids and does not depend on merge order."""

from __future__ import annotations

import json
import random
import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.fold import fold_events
from crav1_2.schema import validate_event
from crav1_2.ulid import encode

from support import ulid_n


def _dump(state: dict) -> str:
    return json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _note(n: int, stream: str, minute: int, eid: str | None = None, files: list[str] | None = None) -> dict:
    return validate_event({
        "v": 1,
        "id": eid or ulid_n(n),
        "at": f"2026-11-25T12:{minute:02d}:00+01:00",
        "by": "engine",
        "run": f"s-{n:04d}",
        "type": "note.added",
        "data": {
            "note": f"2026-11-25-{stream}-note-{n:04d}",
            "kinds": ["chat"],
            "date": "2026-11-25",
            "files": files or ["note.md"],
            "from_sources": None,
            "passages": 0,
        },
    })


class Duplicates(unittest.TestCase):
    def test_exact_duplicate_is_dropped(self):
        event = _note(1, "a", 1)
        state = fold_events([event, event, dict(event)])
        self.assertEqual(list(state["notes"]), ["2026-11-25-a-note-0001"])
        self.assertEqual(state["dropped_duplicate_ids"], [event["id"]])

    def test_different_body_same_id_gets_a_stable_suffix(self):
        first = _note(4, "a", 1, eid=ulid_n(4), files=["note.md"])
        second = _note(4, "a", 2, eid=ulid_n(4), files=["other.md"])
        second["run"] = "s-0099"
        second = validate_event(second)
        left = fold_events([first, second])
        right = fold_events([second, first])
        self.assertEqual(_dump(left), _dump(right))
        self.assertEqual(len(left["disambiguated"]), 1)
        self.assertTrue(left["disambiguated"][0]["to"].startswith(ulid_n(4) + "-"))
        self.assertEqual(left["notes"]["2026-11-25-a-note-0004"]["files"], ["other.md"])


class MergeOrder(unittest.TestCase):
    def test_two_streams_fold_the_same_in_any_order(self):
        master = random.Random(20261126)
        for trial in range(40):
            seed = master.randrange(2**32)
            rng = random.Random(seed)
            left = _stream(rng, "a", 6)
            right = _stream(rng, "b", 6)
            right.append(json.loads(json.dumps(left[0])))
            clash = json.loads(json.dumps(left[1]))
            clash["data"]["files"] = ["other.md"]
            clash["run"] = "s-8800"
            clash = validate_event(clash)
            right.append(clash)
            merged = left + right
            shuffled = list(merged)
            rng.shuffle(shuffled)
            folded = [_dump(fold_events(order)) for order in (left + right, right + left, shuffled, list(reversed(merged)))]
            self.assertEqual(folded[0], folded[1], f"trial {trial} seed {seed}")
            self.assertEqual(folded[0], folded[2], f"trial {trial} seed {seed}")
            self.assertEqual(folded[0], folded[3], f"trial {trial} seed {seed}")
            state = json.loads(folded[0])
            self.assertIn(left[0]["id"], state["dropped_duplicate_ids"])
            self.assertTrue(state["disambiguated"])


def _stream(rng: random.Random, stream: str, count: int) -> list[dict]:
    events = []
    used = set()
    for i in range(count):
        while True:
            eid = encode(1_700_000_000_000 + rng.randrange(0, 50_000), rng.randrange(0, 2**80))
            if eid not in used:
                used.add(eid)
                break
        minute = rng.randrange(0, 60)
        number = rng.randrange(1, 9000)
        events.append(_note(number + (0 if stream == "a" else 10000), stream, minute, eid=eid))
    return events


if __name__ == "__main__":
    unittest.main()
