"""1.172.0: walk state from files and the progress CLI, the Azure DevOps thread
helper, fewer reference reads, and scoped verify with a row helper."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bw = load(SK / "crav1-build-walk/scripts/build_walk.py", "build_walk_1172")
ado = load(SK / "crav1-review-pr/scripts/ado_threads.py", "ado_threads_1172")
vr = load(SK / "crav1-verify-build-against-spec/scripts/verify_rows.py", "verify_rows_1172")


def read(rel: str) -> str:
    return (SK / rel).read_text(encoding="utf-8")


def run(mod, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(argv)
    return code, json.loads(buf.getvalue())


TASKS = (
    "# Tasks\n\n"
    "- [ ] T5 READMEs describe the orders table, malformed payloads and audit rows written by orders-api (branch: feat/orders-readme)\n"
    "- [ ] T9 Bicep for orders-api on dev, test and prod (branch: feat/orders-cicd)\n"
)


class SpecRepo:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root = base / "docs/specs/orders-api"
        self.root.mkdir(parents=True)
        (self.root / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (self.root / "tasks.md").write_text(TASKS, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=base, check=True)
        subprocess.run(["git", "add", "-A"], cwd=base, check=True)
        subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@example.com", "commit", "-qm", "i"], cwd=base, check=True)
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()


class WalkStateFromFiles(unittest.TestCase):
    def test_progress_init_record_and_next(self):
        with SpecRepo() as repo:
            r = str(repo.root)
            code, out = run(bw, ["progress", "init", "--root", r, "--branch", "feat/orders-readme", "--owner", "other", "--tasks", "T5"])
            self.assertEqual(code, 0)
            self.assertFalse(out["wrote"])
            self.assertFalse((repo.root / "build-progress").exists())
            run(bw, ["progress", "init", "--root", r, "--branch", "feat/orders-readme", "--owner", "other", "--tasks", "T5", "--yes"])
            code, out = run(bw, ["progress", "record", "--root", r, "--branch", "feat/orders-readme", "--step", "comment", "--result", "done, PR 71", "--yes"])
            self.assertTrue(out["wrote"])
            text = (repo.root / "build-progress/feat--orders-readme.md").read_text(encoding="utf-8")
            self.assertIn("Owner: other", text)
            self.assertIn("- Step: comment", text)
            self.assertRegex(text, r"Done: \d{4}-\d{2}-\d{2}T")
            self.assertRegex(text, r"Tasks version: [0-9a-f]{12}")
            self.assertIn("Content stamp: normalized", text)
            code, out = run(bw, ["next", "--root", r, "--branch", "feat/orders-readme", "--who", "person A"])
            self.assertEqual(code, 0)
            self.assertEqual(out["phase"], "wait-merge")
            self.assertIn("PR 71", out["lead"])
            self.assertIn("person A to merge pull request 71", out["ending"])
            self.assertNotIn("/crav1-build-walk orders-api T5", out["ending"])
            self.assertIn("Uncommitted: 1 file (feat--orders-readme.md)", out["ending"])

    def test_phase_order(self):
        info = {"owner": "self", "steps": [{"step": "build", "result": "done"}]}
        self.assertEqual(bw.phase_from_progress(info), "verify")
        info["steps"].append({"step": "verify", "result": "paused"})
        self.assertEqual(bw.phase_from_progress(info), "verify")
        self.assertEqual(bw.phase_from_progress({"owner": "self", "steps": []}), "build")
        other = {"owner": "other", "steps": [{"step": "commit", "result": "done"}]}
        self.assertEqual(bw.phase_from_progress(other), "comment")

    def test_full_titles_from_tasks(self):
        with SpecRepo() as repo:
            state = bw.state_from_files(repo.root, "feat/orders-readme")
            self.assertEqual(state["phase"], "build")
            self.assertTrue(state["tasks"][0]["title"].endswith("written by orders-api"))

    def test_bad_input(self):
        code, out = run(bw, ["next"])
        self.assertNotEqual(code, 0)
        self.assertFalse(out["ok"])
        with SpecRepo() as repo:
            code, out = run(bw, ["progress", "record", "--root", str(repo.root), "--branch", "feat/x", "--step", "build", "--result", "done"])
            self.assertEqual(out["code"], "file")


THREADS = {
    "value": [
        {"id": 112, "status": 2, "comments": [{"id": 1, "parentCommentId": 0, "author": {"displayName": "Person Å"}, "content": "Ändring behövs – old"}]},
        {"id": 124, "status": 1, "comments": [{"id": 1, "parentCommentId": 0, "author": {"displayName": "person A"}, "content": "Review\r\nLooks good  \r\n"}]},
    ]
}


class AdoThreads(unittest.TestCase):
    def test_decode_cp1252_bytes(self):
        raw = json.dumps(THREADS, ensure_ascii=False).encode("cp1252")
        with self.assertRaises(UnicodeDecodeError):
            raw.decode("utf-8")
        data = json.loads(ado.decode(raw))
        self.assertEqual(data["value"][0]["comments"][0]["author"]["displayName"], "Person Å")
        bom = b"\xef\xbb\xbf" + json.dumps(THREADS).encode("utf-8")
        self.assertEqual(json.loads(ado.decode(bom))["value"][1]["id"], 124)

    def test_list_and_compare_with_mocked_az(self):
        raw = json.dumps(THREADS, ensure_ascii=False).encode("cp1252")
        calls = []

        def fake(args):
            calls.append(args)
            return raw

        old = ado.run_az
        ado.run_az = fake
        try:
            code, out = run(ado, ["list", "--pr", "73"])
            self.assertEqual(code, 0)
            self.assertEqual(out["count"], 2)
            self.assertEqual(out["threads"][0]["status"], "fixed")
            self.assertIn("-o", calls[0])
            self.assertNotIn(">", calls[0])
            with tempfile.TemporaryDirectory() as tmp:
                draft = Path(tmp) / "d.md"
                draft.write_bytes(b"Review\nLooks good\n")
                code, out = run(ado, ["compare", "--pr", "73", "--draft", str(draft)])
                self.assertTrue(out["same"])
                self.assertEqual(out["thread"], 124)
                draft.write_text("Something else", encoding="utf-8")
                code, out = run(ado, ["compare", "--pr", "73", "--draft", str(draft)])
                self.assertFalse(out["same"])
        finally:
            ado.run_az = old

    def test_post_is_new_top_level_thread(self):
        seen = {}

        def fake(args):
            body = Path(args[args.index("--in-file") + 1]).read_text(encoding="utf-8")
            seen["body"] = json.loads(body)
            seen["args"] = args
            return b'{"id": 160}'

        old = ado.run_az
        ado.run_az = fake
        try:
            with tempfile.TemporaryDirectory() as tmp:
                block = Path(tmp) / "b.md"
                block.write_text("Re-review: ändrat", encoding="utf-8")
                code, out = run(ado, ["post", "--pr", "73", "--file", str(block)])
                self.assertFalse(out["posted"])
                self.assertNotIn("body", seen)
                code, out = run(ado, ["post", "--pr", "73", "--file", str(block), "--yes"])
                self.assertTrue(out["posted"])
                self.assertEqual(out["thread"], 160)
                self.assertEqual(seen["body"]["comments"][0]["parentCommentId"], 0)
                self.assertEqual(seen["body"]["comments"][0]["content"], "Re-review: ändrat")
                self.assertIn("POST", seen["args"])
        finally:
            ado.run_az = old

    def test_az_failure_is_json(self):
        def boom(args):
            raise RuntimeError("az: not logged in")

        old = ado.run_az
        ado.run_az = boom
        try:
            code, out = run(ado, ["list", "--pr", "1"])
            self.assertNotEqual(code, 0)
            self.assertFalse(out["ok"])
        finally:
            ado.run_az = old


VERIFY = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Implemented, verified | 1 | T1 |
| Implemented, verified, tick pending | 0 | |
| Implemented, verify failed | 0 | |
| Not implemented | 2 | T3, T6 |
| Claimed done, unverified | 0 | |
| Acceptance with no task | 0 | |

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T1 | Host setup | Implemented, verified | live check ok |
| T3 | CI policy | Not implemented | |
| T6 | Cursor 404 | Not implemented | |

## Commands run

- Live host: in-process tests only
"""


class ScopedVerify(unittest.TestCase):
    def test_set_and_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "tasks.md").write_text("- [ ] T1 Host setup\n", encoding="utf-8")
            path = folder / "verify.md"
            path.write_text(VERIFY, encoding="utf-8")
            code, out = run(vr, ["set", "--file", str(path), "--task", "T6", "--status", "Implemented, verified", "--evidence", "tests pass at abc1234", "--branch", "feat/orders-fixes", "--tip", "abc1234def567", "--yes"])
            self.assertTrue(out["wrote"])
            for task, branch, tip in (("T1", "feat/orders-host", "1111111aaaa"), ("T3", "feat/orders-ci", "2222222bbbb")):
                run(vr, ["set", "--file", str(path), "--task", task, "--status", "Implemented, verified" if task == "T1" else "Not implemented", "--evidence", "x", "--branch", branch, "--tip", tip, "--yes"])
            text = path.read_text(encoding="utf-8")
            self.assertIn("| Implemented, verified | 2 | T1, T6 |", text)
            self.assertIn("| Not implemented | 1 | T3 |", text)
            self.assertIn("- T6: feat/orders-fixes abc1234def56", text)
            self.assertIn("## Commands run", text)
            tips = folder / "tips.json"
            tips.write_text(json.dumps({"T1": "1111111aaaa", "T3": "2222222bbbb", "T6": "9999999"}), encoding="utf-8")
            code, out = run(vr, ["scope", "--file", str(path), "--tips-json", str(tips)])
            self.assertEqual(out["rerun"], ["T6"])
            self.assertEqual(out["kept"], ["T1", "T3"])
            self.assertIn("Kept from the last verify: T1, T3", out["kept_line"])
            (folder / "tasks.md").write_text("- [ ] T1 Host setup, changed\n", encoding="utf-8")
            code, out = run(vr, ["scope", "--file", str(path), "--tips-json", str(tips)])
            self.assertTrue(out["stamp_moved"])
            self.assertEqual(out["kept"], [])
            (folder / "tasks.md").write_text("- [x] T1 Host setup\n", encoding="utf-8")
            code, out = run(vr, ["scope", "--file", str(path), "--tips-json", str(tips)])
            self.assertFalse(out["stamp_moved"])

    def test_unknown_task_and_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "verify.md"
            path.write_text(VERIFY, encoding="utf-8")
            code, out = run(vr, ["set", "--file", str(path), "--task", "T9", "--status", "Not implemented", "--evidence", "x"])
            self.assertFalse(out["ok"])
            code, out = run(vr, ["set", "--file", str(path), "--task", "3", "--status", "Implemented, verify failed", "--evidence", "x"])
            self.assertFalse(out["wrote"])
            self.assertEqual(path.read_text(encoding="utf-8"), VERIFY)


class FewerReads(unittest.TestCase):
    def test_skill_routing(self):
        walk = read("crav1-build-walk/SKILL.md")
        self.assertIn("next --root <spec folder> --branch <branch>", walk)
        self.assertIn("Read no reference (1.172.0)", walk)
        self.assertIn("progress record --root <spec> --branch <branch> --step", read("crav1-build-walk/references/progress.md"))
        self.assertIn("does not open `tool-approvals.md`", read("crav1-build-walk/references/common.md"))
        self.assertLessEqual(len(walk.split()), 1600)
        self.assertIn("do not open `tool-approvals.md`", read("crav1-build-tasks/branches/one-task/BRANCH.md"))
        review = read("crav1-review-pr/SKILL.md")
        self.assertIn("draft with no posted section", review)
        self.assertLessEqual(len(review.split()), 1275)
        self.assertIn("scripts/ado_threads.py post", read("crav1-review-pr/references/posting.md"))
        self.assertIn("ado_threads.py", read("crav1-open-pr/references/host.md"))
        self.assertIn("references/scoped-verify.md", read("crav1-verify-build-against-spec/SKILL.md"))
        self.assertIn("verify_rows.py scope", read("crav1-verify-build-against-spec/references/scoped-verify.md"))

    def test_house_rules(self):
        for rel in ("crav1-build-walk/references/common.md", "crav1-review-pr/references/posting.md", "crav1-verify-build-against-spec/references/scoped-verify.md"):
            text = read(rel)
            new = "\n".join(p for p in text.split("\n\n") if "1.172.0" in p)
            self.assertNotIn("rebase", new.lower(), rel)
            self.assertNotIn("\nNext:", text, rel)


if __name__ == "__main__":
    unittest.main()
