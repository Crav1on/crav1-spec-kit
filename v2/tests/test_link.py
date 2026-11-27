"""link-to-spec: write-back, cards, endings, park, and the event fold.

Synthetic names only. The 1.x open-question and ready-check scripts are the
ones in this repo.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.cards import card_problems
from crav1_2.errors import EngineError
from crav1_2.fold import fold_events
from crav1_2.lines import one_x_lines_unchanged, strip_owned
from crav1_2.link_to_spec import _backed, link_to_spec
from crav1_2.repo import init_repo, append_events, read_events, rebuild_views
from crav1_2.schema import origin_problem, validate_event

from support import REPO, V2, note_event, remove, temp_dir, ulid_n


BLOCKS = REPO / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
WALK = REPO / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
PLAN = REPO / ".cursor/skills/crav1/crav1-plan-from-spec/scripts/plan_check.py"
SLUG = "partner-b-feed"
NOTE = "2026-11-25-outbound-channel"
ALERT = "Who gets the certificate-expiry alert, and how early?"
WINDOW = "Which window does partner B use for the weekly file?"
OUTBOUND = (
    "The outbound messaging channel is agreed long term, likely before go-live, "
    "and is not built in this slice."
)
SPEC = f"""# Partner B feed

## Problem

The weekly file to partner B has no named window.

## Acceptance criteria

- AC1: The feed to partner B stays on the existing secure channel.

## Constraints
- The feed to partner B runs over the existing secure channel.
- Security S2: inbound calls are accepted only from listed private networks.

## Open questions
- {ALERT}
  - Blocks: none
- {WINDOW}
  - Blocks: none
"""
PLAN_MD = """# Plan: partner-b-feed

## Approach

1. Keep the feed on the current channel. (T1)

## Linter

ruff

## Risks
"""
TASKS = """# Tasks

- [ ] T1 Keep the feed (spec: AC1)
"""
QUOTE = "Agreed long term, likely before go-live, not in this slice."
ALERT_QUOTE = "The certificate expiry alert goes to person A two weeks before it lapses."
WINDOW_QUOTE = "Partner B uses the Monday window for the weekly file."


def _passages():
    return [
        {
            "id": "p-001",
            "kind": "session",
            "who": "person A",
            "quote": QUOTE,
            "weak": "verbal",
            "label": "finding",
        },
        {
            "id": "p-002",
            "kind": "session",
            "who": "person A",
            "quote": ALERT_QUOTE,
            "label": "answer",
            "answers": ALERT,
        },
        {
            "id": "p-003",
            "kind": "session",
            "who": "person A",
            "quote": WINDOW_QUOTE,
            "label": "answer",
            "answers": WINDOW,
        },
    ]


def _event(n, kind, data, minute):
    return validate_event({
        "v": 1,
        "id": ulid_n(n),
        "at": f"2026-11-25T11:{minute:02d}:00+01:00",
        "by": "engine",
        "run": "s-0001",
        "type": kind,
        "data": data,
    })


def _matched(n, passage, question, minute):
    return _event(n, "answer.matched", {
        "note": NOTE, "passage": passage, "spec": SLUG, "question": question,
    }, minute)


class Repo(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: remove(self.root))
        init_repo(self.root)
        folder = self.root / "docs" / "specs" / SLUG
        folder.mkdir(parents=True)
        (folder / "spec.md").write_text(SPEC, encoding="utf-8")
        (folder / "plan.md").write_text(PLAN_MD, encoding="utf-8")
        (folder / "tasks.md").write_text(TASKS, encoding="utf-8")
        (self.root / "readme.md").write_text("partner B feed\n", encoding="utf-8")
        note = note_event(1, passage_list=_passages(), kinds=["session"], title="Outbound")
        append_events(self.root, [
            validate_event(note),
            _matched(2, "p-002", ALERT, 2),
            _matched(3, "p-003", WINDOW, 3),
        ])

    def spec_path(self):
        return self.root / "docs" / "specs" / SLUG / "spec.md"

    def tasks_path(self):
        return self.root / "docs" / "specs" / SLUG / "tasks.md"

    def finder(self, items):
        return {"at": "2026-11-26T13:31:00+01:00", "finder": {"items": items}}

    def silent(self, **over):
        row = {
            "status": "silent",
            "note": NOTE,
            "passages": ["p-001"],
            "impact": 3,
            "uncertainty": 2,
            "holds": ["T1"],
            "section": "Constraints",
            "text": OUTBOUND,
            "who": "person A",
        }
        row.update(over)
        return row

    def low(self, text, **over):
        row = {
            "status": "vague",
            "note": NOTE,
            "passages": ["p-001"],
            "impact": 1,
            "uncertainty": 1,
            "holds": [],
            "section": "Constraints",
            "text": text,
            "who": "person A",
        }
        row.update(over)
        return row

    def drive(self, items, words):
        result = link_to_spec(self.root, [SLUG], self.finder(items))
        for word in words:
            if result.get("ending"):
                break
            result = link_to_spec(self.root, word.split(), {})
        return result

    def snapshot(self):
        found = {}
        for path in self.root.rglob("*"):
            if path.is_file():
                found[path.relative_to(self.root).as_posix()] = path.read_bytes()
        return found


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc


def _questions(spec_dir):
    proc = subprocess.run(
        [sys.executable, str(BLOCKS), str(spec_dir)],
        capture_output=True,
        text=True,
    )
    return proc, json.loads(proc.stdout) if proc.returncode == 0 else None


def _lint(spec_dir):
    return subprocess.run(
        [sys.executable, str(PLAN), "lint", "--root", str(spec_dir)],
        capture_output=True,
        text=True,
    )


def _ready(spec_dir):
    env = os.environ.copy()
    env["CRAV1_NO_HOST_LOOKUP"] = "1"
    return subprocess.run(
        [sys.executable, str(WALK), "readiness", "--full", "--root", str(spec_dir), "--skip-sync"],
        capture_output=True,
        text=True,
        env=env,
    )


class WriteBack(Repo):
    def test_check_5_item_lines_and_the_1x_scripts(self):
        spec_dir = self.spec_path().parent
        _git(self.root, "init", "-b", "main")
        _git(self.root, "config", "user.email", "person-a@example.test")
        _git(self.root, "config", "user.name", "Person A")
        _git(self.root, "config", "commit.gpgsign", "false")
        _git(self.root, "add", "readme.md", "docs")
        _git(self.root, "commit", "-m", "spec")
        before_q, before_body = _questions(spec_dir)
        before_lint = _lint(spec_dir)
        before_ready = _ready(spec_dir)
        self.assertEqual(before_q.returncode, 0, before_q.stderr)
        self.assertEqual(before_lint.returncode, 0, before_lint.stderr)
        self.assertEqual(before_ready.returncode, 0, before_ready.stderr + before_ready.stdout)
        before_spec = self.spec_path().read_text(encoding="utf-8")
        before_tasks = self.tasks_path().read_bytes()
        other = self.snapshot()
        result = self.drive(
            [self.silent(), self.low("The weekly file can wait.")],
            ["add-pointer", "accept-all", "close-all"],
        )
        self.assertTrue(result["wrote"])
        after = self.spec_path().read_text(encoding="utf-8")
        self.assertTrue(one_x_lines_unchanged(before_spec, after))
        self.assertEqual(strip_owned(before_spec), strip_owned(after))
        self.assertIn("[src: F-", after)
        self.assertIn("[asm: A-", after)
        self.assertIn("[dec: D-", after)
        self.assertIn("Answered:", after)
        self.assertIn("Full source: sot/facts.md#F-", after)
        self.assertNotIn("**New:**", after)
        self.assertNotIn("\nNext:", "\n" + result["ending"])
        for line in after.splitlines():
            if "crav1-2:item" not in line or line.lstrip().startswith("- Blocks:"):
                continue
            tags = sum(token in line for token in ("[src:", "[dec:", "[asm:"))
            if line.lstrip().startswith("- ") and "Blocks:" not in line:
                self.assertEqual(tags, 1, line)
        self.assertEqual(self.tasks_path().read_bytes(), before_tasks)
        after_q, after_body = _questions(spec_dir)
        after_lint = _lint(spec_dir)
        after_ready = _ready(spec_dir)
        self.assertEqual(after_q.returncode, 0, after_q.stderr)
        self.assertEqual(after_lint.returncode, 0, after_lint.stderr)
        self.assertEqual(after_lint.stdout, before_lint.stdout)
        self.assertEqual(after_ready.returncode, 0, after_ready.stderr + after_ready.stdout)
        before_texts = [row["text"] for row in before_body["questions"]]
        after_texts = [row["text"] for row in after_body["questions"]]
        self.assertIn(ALERT, before_texts)
        self.assertIn(WINDOW, before_texts)
        self.assertEqual(after_texts, [])
        self.assertEqual(after.count("Answered:"), 2)
        self.assertIn(f"- {ALERT}", after)
        self.assertIn(f"- {WINDOW}", after)
        self.assertTrue(all(row["mark"] != "unparsed" for row in after_body["questions"]))
        self.assertFalse(any(row["blocks_slice"] for row in after_body["questions"]))
        self.assertNotIn("outbound messaging", " ".join(after_texts))
        ready = json.loads(after_ready.stdout)
        self.assertNotIn("error", ready)
        for rel, data in other.items():
            if rel.startswith(("sot/", ".crav1-2/", "docs/specs/")) or rel.startswith(".git/"):
                continue
            self.assertEqual((self.root / rel).read_bytes(), data, rel)

    def test_close_all_pick_some_and_skip(self):
        picked = self.drive([self.silent(holds=[])], ["add-pointer", "pick-some 2"])
        self.assertTrue(picked["wrote"])
        text = self.spec_path().read_text(encoding="utf-8")
        self.assertIn(WINDOW_QUOTE, text)
        self.assertNotIn(ALERT_QUOTE, text)
        self.assertEqual(text.count("Answered:"), 1)
        decisions = [event for event in read_events(self.root) if event["type"] == "decision.recorded"]
        closed = [row for row in decisions if row["data"]["chosen"] == "pick-some"]
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0]["data"]["accepting"], WINDOW)

    def test_skip_leaves_the_question_open_and_a_later_run_does_not_ask_again(self):
        skipped = self.drive([self.silent(holds=[])], ["add-pointer", "skip"])
        self.assertTrue(skipped["wrote"])
        text = self.spec_path().read_text(encoding="utf-8")
        self.assertNotIn("Answered:", text)
        body = json.loads(subprocess.run(
            [sys.executable, str(BLOCKS), str(self.spec_path().parent)],
            capture_output=True, text=True,
        ).stdout)
        texts = [row["text"] for row in body["questions"]]
        self.assertIn(ALERT, texts)
        again = link_to_spec(self.root, [SLUG], {})
        self.assertFalse(again["needs_finder"])
        self.assertEqual(again["card_text"], "")
        self.assertTrue(again["ending"].startswith("Run next:"))
        forced = link_to_spec(self.root, [SLUG, f"note-{NOTE}"], {})
        self.assertTrue(forced["needs_finder"])

    def test_assumption_batch_and_must_stays_a_source_item(self):
        must = "The feed MUST stay on the current channel."
        preview = link_to_spec(self.root, [SLUG, "dry-run"], self.finder([
            self.low("The weekly file can wait."),
            self.low("The Monday window can slip by one hour."),
            self.low(must),
        ]))
        questions = [card.split("Card: ", 1)[-1].splitlines()[0] for card in preview["cards"]]
        self.assertTrue(any(line.startswith("These ") and "assumptions" in line for line in questions))
        self.assertTrue(any("vague gap" in line for line in questions))
        self.assertNotIn("MUST", "\n".join(
            card for card in preview["cards"] if "assumptions" in card
        ))
        result = self.drive([
            self.low("The weekly file can wait."),
            self.low("The Monday window can slip by one hour."),
            self.low(must),
        ], ["use-proposed", "change-some 1", "skip"])
        text = self.spec_path().read_text(encoding="utf-8")
        self.assertIn("The weekly file can wait. [asm:", text)
        self.assertNotIn("The Monday window can slip", text)
        self.assertIn(f"{must} [src:", text)
        self.assertNotIn(f"{must} [asm:", text)
        for event in result["events"]:
            if event["type"] != "item.linked":
                continue
            self.assertIsNone(origin_problem(event["data"]["origin"], event["data"]["refs"]))
            if "MUST" in event["data"]["text"]:
                self.assertNotEqual(event["data"]["origin"], "asm")

    def test_ask_owner_writes_a_waits_line_and_no_new_task(self):
        before = self.tasks_path().read_text(encoding="utf-8")
        result = self.drive([
            {
                "status": "conflicting",
                "note": NOTE,
                "passages": ["p-001"],
                "impact": 2,
                "uncertainty": 2,
                "holds": ["T1"],
                "section": "Constraints",
                "text": "Can partner B's static address be listed without breaking Security S2?",
                "who": "person A",
            },
        ], ["ask-owner", "skip"])
        self.assertTrue(result["wrote"])
        tasks = self.tasks_path().read_text(encoding="utf-8")
        self.assertTrue(one_x_lines_unchanged(before, tasks))
        self.assertIn("Waits on: D-", tasks)
        self.assertEqual(tasks.count("- [ ]"), before.count("- [ ]"))
        spec = self.spec_path().read_text(encoding="utf-8")
        self.assertIn("- Blocks: T1 <!-- crav1-2:item", spec)


class Cards(Repo):
    def test_check_6_every_card_and_a_missing_fact(self):
        dry = link_to_spec(self.root, [SLUG, "dry-run"], self.finder([
            self.silent(),
            self.low("The weekly file can wait."),
        ]))
        self.assertGreaterEqual(len(dry["cards"]), 2)
        self.assertTrue(any("These 2 open questions have answers in the SoT" in card for card in dry["cards"]))
        shown = link_to_spec(self.root, [SLUG], self.finder([self.silent(), self.low("The weekly file can wait.")]))
        plan = json.loads((self.root / ".crav1-2" / "sessions" / f"{shown['session']}.json").read_text(encoding="utf-8"))
        for card in plan["payload"]["plan"]["cards"]:
            self.assertEqual(card_problems(card["card"]), [])
            options = card["card"]["options"]
            self.assertTrue(2 <= len(options) <= 4)
            for option in options:
                self.assertTrue(option["impact"].strip())
                self.assertTrue(option["undo"].strip())
            self.assertIn("`skip`", card["card_text"])
            if card["card"]["recommended"]:
                self.assertTrue(card["card"]["facts"])
                self.assertIn("(Recommended)", card["card_text"])
        bare = _backed("What should the spec do with this silent gap?", [
            {"word": "add-pointer", "impact": "Write the line.", "undo": "Unlink it."},
            {"word": "leave-out", "impact": "Write nothing.", "undo": "Run it again."},
        ], "add-pointer", [], "person A", "No cited passage backs a recommendation for this gap.")
        self.assertIsNone(bare["recommended"])
        self.assertEqual(card_problems(bare), [])
        self.assertIn("person A could give it", bare["missing_fact"])
        from crav1_2.link_to_spec import _render
        rendered = _render(bare, "Proposed: a line")
        self.assertIn("Missing fact:", rendered)
        self.assertIn("could give it", rendered)
        self.assertNotIn("Recommended", rendered)
        self.assertTrue(card_problems({
            "question": "q",
            "options": bare["options"],
            "recommended": "add-pointer",
            "facts": [],
        }))


class Ending(Repo):
    def test_check_7_run_next_and_no_bookkeeping_card(self):
        opened = link_to_spec(self.root, [SLUG], self.finder([self.silent(holds=[])]))
        self.assertIsNone(opened["ending"])
        self.assertIn("Card:", opened["card_text"])
        self.assertNotIn("Run next:", opened["card_text"])
        self.assertNotIn("edit the file", opened["card_text"].lower())
        step = link_to_spec(self.root, ["add-pointer"], {})
        self.assertIsNone(step["ending"])
        self.assertIn("open questions have answers in the SoT", step["card_text"])
        done = link_to_spec(self.root, ["skip"], {})
        self.assertTrue(done["ending"].startswith("Run next:"))
        self.assertLessEqual(sum(line.startswith("Also recorded:") for line in done["ending"].splitlines()), 1)
        self.assertFalse(any(line.startswith("Next:") for line in done["ending"].splitlines()))
        self.assertNotIn("edit ", done["ending"].lower())


class Park(Repo):
    def test_check_8_resume_in_a_fresh_process(self):
        before = self.snapshot()
        parked = link_to_spec(self.root, [SLUG, "park"], self.finder([self.silent(holds=[])]))
        self.assertEqual(parked["parked"], parked["session"])
        self.assertIn("Card:", parked["card_text"])
        self.assertFalse(parked["wrote"])
        after_park = self.snapshot()
        for rel, data in before.items():
            self.assertEqual(after_park[rel], data, rel)
        self.assertTrue((self.root / ".crav1-2" / "sessions" / f"{parked['session']}.json").is_file())
        with self.assertRaises(EngineError) as caught:
            link_to_spec(self.root, ["add-pointer"], {})
        self.assertIn("parked", caught.exception.message)
        fresh = _fresh(self.root, "resume")
        self.assertEqual(fresh["card_text"], parked["card_text"])
        self.assertFalse(fresh["wrote"])
        advanced = _fresh(self.root, "resume", "add-pointer")
        self.assertFalse(advanced["wrote"])
        self.assertIn("open questions have answers in the SoT", advanced["card_text"])
        written = _fresh(self.root, "resume", "skip")
        self.assertTrue(written["wrote"])
        self.assertTrue(written["ending"].startswith("Run next:"))
        self.assertIn("crav1-2:item", self.spec_path().read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing(self):
        before = self.snapshot()
        dry = link_to_spec(self.root, [SLUG, "dry-run"], self.finder([
            self.silent(), self.low("The weekly file can wait."),
        ]))
        self.assertTrue(dry["dry_run"])
        self.assertFalse(dry["wrote"])
        self.assertTrue(dry["cards"])
        self.assertTrue(dry["proposed_items"])
        self.assertEqual(dry["events"], [])
        self.assertIsNone(dry["ending"])
        self.assertEqual(self.snapshot(), before)
        cli = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "crav1_2", "link-to-spec", SLUG, "dry-run", "repo", str(self.root)],
            input=json.dumps(self.finder([self.silent(holds=[])])),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(V2)},
        )
        self.assertEqual(cli.returncode, 0, cli.stderr)
        body = json.loads(cli.stdout)
        self.assertTrue(body["dry_run"])
        self.assertEqual(self.snapshot(), before)


class Views(Repo):
    def test_check_9_sot_rebuilds_from_the_log(self):
        self.drive([self.silent(), self.low("The weekly file can wait.")], ["add-pointer", "accept-all", "close-all"])
        sot = self.root / "sot"
        before = {path.relative_to(sot).as_posix(): path.read_bytes() for path in sot.rglob("*.md")}
        self.assertTrue(before)
        for path in sot.rglob("*.md"):
            path.unlink()
        rebuild_views(self.root)
        after = {path.relative_to(sot).as_posix(): path.read_bytes() for path in sot.rglob("*.md")}
        self.assertEqual(before, after)

    def test_two_streams_fold_the_same_in_any_order(self):
        self.drive([self.silent(holds=[])], ["add-pointer", "close-all"])
        left = read_events(self.root)
        right = [
            validate_event(note_event(
                40,
                note="2026-11-26-weekly-window",
                title="Weekly window",
                date="2026-11-26",
                passage_list=[{
                    "id": "p-001", "kind": "chat", "who": "partner B",
                    "quote": "The window is Monday.",
                }],
            )),
            _event(41, "note.read", {"note": "2026-11-26-weekly-window", "spec": SLUG}, 41),
        ]
        right[1]["at"] = "2026-11-26T18:00:00+01:00"
        right[1]["run"] = "s-0041"
        right[1] = validate_event(right[1])
        master = random.Random(20261126)
        base = json.dumps(fold_events(left + right), sort_keys=True)
        for trial in range(12):
            rng = random.Random(master.randrange(2**32))
            shuffled = list(left + right)
            rng.shuffle(shuffled)
            folded = json.dumps(fold_events(shuffled), sort_keys=True)
            self.assertEqual(base, folded, f"trial {trial}")
            self.assertEqual(base, json.dumps(fold_events(right + left), sort_keys=True))


class Guard(Repo):
    def test_a_1x_mark_is_refused_and_words_are_checked(self):
        with self.assertRaises(EngineError) as caught:
            link_to_spec(self.root, [SLUG], self.finder([self.silent(text="**New:** the channel moved")]))
        self.assertIn("1.x mark", caught.exception.message)
        with self.assertRaises(EngineError) as missing:
            link_to_spec(self.root, [], {})
        self.assertIn("note-<id>", missing.exception.message)
        with self.assertRaises(EngineError):
            link_to_spec(self.root, [SLUG, "none", f"note-{NOTE}"], {})
        with self.assertRaises(EngineError):
            link_to_spec(self.root, [SLUG, "resume", "park"], self.finder([self.silent()]))
        other = self.root / "docs" / "specs" / "weekly-file"
        other.mkdir(parents=True)
        (other / "spec.md").write_text("# Weekly file\n\n## Constraints\n- The window is unnamed.\n", encoding="utf-8")
        covered = link_to_spec(self.root, ["weekly-file"], {
            "at": "2026-11-26T13:31:00+01:00",
            "finder": {"items": [{"status": "covered", "note": NOTE, "passages": ["p-001"]}]},
        })
        self.assertEqual(
            covered["ending"],
            "Run next: nothing needed; the spec already covers this note.\n",
        )
        self.assertNotIn("Also recorded:", covered["ending"])
        self.assertEqual((other / "spec.md").read_text(encoding="utf-8"), "# Weekly file\n\n## Constraints\n- The window is unnamed.\n")
        kinds = {event["type"] for event in covered["events"]}
        self.assertIn("fact.cited", kinds)
        self.assertIn("note.read", kinds)


class FinderShape(Repo):
    def test_note_prefix_is_a_note_id(self):
        opened = link_to_spec(self.root, [SLUG], self.finder([self.silent(note=f"note-{NOTE}")]))
        self.assertIn("Card:", opened["card_text"])
        self.assertIsNone(opened["ending"])
        with self.assertRaises(EngineError) as caught:
            link_to_spec(self.root, [SLUG], self.finder([self.silent(note="note-not-a-date")]))
        self.assertIn("a finder item needs a note id", caught.exception.message)

    def test_covered_dry_run_returns_an_ending(self):
        other = self.root / "docs" / "specs" / "weekly-file"
        other.mkdir(parents=True)
        (other / "spec.md").write_text("# Weekly file\n\n## Constraints\n- The window is unnamed.\n", encoding="utf-8")
        before = self.snapshot()
        dry = link_to_spec(self.root, ["weekly-file", "dry-run"], {
            "at": "2026-11-26T13:31:00+01:00",
            "finder": {"items": [{"status": "covered", "note": f"note-{NOTE}", "passages": ["p-001"]}]},
        })
        self.assertTrue(dry["dry_run"])
        self.assertFalse(dry["wrote"])
        self.assertEqual(dry["cards"], [])
        self.assertEqual(
            dry["ending"],
            "Run next: nothing needed; the spec already covers this note.\n",
        )
        self.assertFalse(any(line.startswith("Next:") for line in dry["ending"].splitlines()))
        self.assertEqual(self.snapshot(), before)

    def test_finder_inputs_are_files_and_the_spec_is_narrowed(self):
        extra = "\n## Payroll calendar\n\nThe payroll calendar lists pay dates for the year.\n"
        self.spec_path().write_text(SPEC + extra, encoding="utf-8")
        packet = link_to_spec(self.root, [SLUG], {})
        self.assertTrue(packet["needs_finder"])
        self.assertNotIn("spec_markdown", packet)
        self.assertNotIn("Payroll", json.dumps(packet))
        files = packet["finder_files"]
        self.addCleanup(lambda: shutil.rmtree(Path(files["spec"]).parent, ignore_errors=True))
        spec = Path(files["spec"]).read_text(encoding="utf-8")
        self.assertIn("## Constraints", spec)
        self.assertIn("## Open questions", spec)
        self.assertNotIn("Payroll", spec)
        self.assertIn(QUOTE, Path(files["notes"]).read_text(encoding="utf-8"))
        self.assertIn("T1", Path(files["tasks"]).read_text(encoding="utf-8"))
        for key in ("notes", "spec", "decisions", "tasks"):
            self.assertTrue(Path(files[key]).is_file(), key)
        agent = (V2 / "agents" / "crav1-2-gap-finder-agent.md").read_text(encoding="utf-8")
        read = (V2 / "skills" / "crav1-2-link-to-spec" / "references" / "read.md").read_text(encoding="utf-8")
        self.assertIn("YYYY-MM-DD-slug", agent)
        self.assertIn("Do not write the `note-` prefix", agent)
        self.assertIn("Read each path you are given", agent)
        self.assertIn("finder_files.spec", read)
        self.assertIn("Do not paste those files", read)


def _fresh(root: Path, *words) -> dict:
    code = (
        "import json,sys\n"
        "from pathlib import Path\n"
        "from crav1_2.link_to_spec import link_to_spec\n"
        "root = Path(sys.argv[1])\n"
        "print(json.dumps(link_to_spec(root, sys.argv[2:], {})))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code, str(root), *words],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(V2)},
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


if __name__ == "__main__":
    unittest.main()
