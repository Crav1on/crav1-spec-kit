"""1.180.0: one shared task-state module (task_state.py); claimed rows keep
their file order; the merge list counts a branch's open tasks; a task that
waits on its own PR's merge is Blocked; built-and-waiting is waiting, never a
silent blocker; tighten-plan's empty queue names the ready check; reopen
reasons name only sections that reopen the step; the uncommitted count
includes the map; held lines name unbuilt deps; owner names are cleaned on
write and read."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ts = load("crav1-tasks-ready-to-build/scripts/task_state.py", "ts_1180")
cl = load("crav1-build-walk/scripts/claims.py", "cl_1180")
wp = load("crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py", "wp_1180")
bm = load("crav1-tasks-ready-to-build/scripts/build_map.py", "bm_1180")
pc = load("crav1-plan-from-spec/scripts/plan_check.py", "pc_1180")
we = load("crav1-tasks-ready-to-build/scripts/walk_ending.py", "we_1180")
VR = SK / "crav1-verify-build-against-spec/scripts/verify_rows.py"


class TaskState(unittest.TestCase):
    def test_states(self):
        self.assertEqual(ts.task_state(True)["state"], "done")
        merged = ts.task_state(False, merged=True, verify="Implemented, verified")
        self.assertEqual(merged["state"], "tick-pending")
        self.assertTrue(merged["offer_tick"] and merged["counts_done"])
        self.assertFalse(merged["stop"], "recorded merged is never a reason to stop a commit")
        self.assertTrue(ts.task_state(False, merged=True, verify="Not implemented")["verify_first"])
        self.assertEqual(ts.task_state(False, built=True)["state"], "merge-wait")
        self.assertEqual(ts.task_state(False)["state"], "open")

    def test_clean_names(self):
        self.assertEqual(ts.clean_name("Admin Person A"), "Person A")
        self.assertEqual(ts.clean_name("Person B (Tag)"), "Person B")
        self.assertEqual(ts.clean_name("  Admin  Person B  (Tag) "), "Person B")
        self.assertEqual(ts.clean_name("Adminton Person"), "Adminton Person")
        self.assertTrue(ts.same_person("Admin Person A", "person a"))
        self.assertEqual(ts.unique_names(["Admin Person A", "Person A", "Person B (Tag)"]), ["Person A", "Person B"])

    def test_waiting_reason(self):
        self.assertTrue(ts.is_waiting_reason("built by person B, waits for PR 82 to merge"))
        self.assertFalse(ts.is_waiting_reason("waits on T3"))

    def test_used_by_every_owner(self):
        for rel in ("crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py",
                    "crav1-tasks-ready-to-build/scripts/build_map.py",
                    "crav1-verify-build-against-spec/scripts/verify_rows.py"):
            self.assertIn("task_state", (SK / rel).read_text(encoding="utf-8"), rel)
        self.assertIn("task_state.py", (SK / "crav1-finalize-commit/references/choice-words.md").read_text(encoding="utf-8"))


class ClaimsOrder(unittest.TestCase):
    BEFORE = "- [ ] T5 a\n- [ ] T8 b\n- [ ] T9 c\n- [ ] T12 d\n- [ ] T43 e\n"

    def test_claims_order_differs_from_file_order(self):
        after = "- [ ] T5 a\n- [ ] T8 b2\n- [ ] T43 e\n- [ ] T9 c\n- [ ] T12 d\n"
        out = cl.preserve_claimed(self.BEFORE, after, ["T5", "T43", "T9", "T12"])
        ids = [line.split()[3] for line in out["text"].splitlines()]
        self.assertEqual(ids, ["T5", "T8", "T9", "T12", "T43"])

    def test_unchanged_order_stays(self):
        after = "- [ ] T5 a\n- [ ] T8 b2\n- [ ] T9 c\n- [ ] T12 d\n- [ ] T43 e\n"
        out = cl.preserve_claimed(self.BEFORE, after, ["T5", "T43", "T9", "T12"])
        self.assertEqual(out["text"], after)

    def test_write_keeps_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before.md"
            after = Path(tmp) / "tasks.md"
            before.write_bytes(self.BEFORE.replace("\n", "\r\n").encode())
            after.write_bytes("- [ ] T5 a\r\n- [ ] T8 b\r\n- [ ] T43 e\r\n- [ ] T9 c\r\n- [ ] T12 d\r\n".encode())
            proc = subprocess.run([sys.executable, str(SK / "crav1-build-walk/scripts/claims.py"), "preserve",
                                   "--before", str(before), "--after", str(after), "--tasks", "T5,T43,T9,T12", "--write"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            raw = after.read_bytes().decode()
            self.assertIn("\r\n", raw)
            self.assertNotIn("\n- [ ] T43 e\r\n- [ ] T9", raw)
            self.assertTrue(raw.rstrip().endswith("T43 e"))


class MergeOrder(unittest.TestCase):
    def rows(self):
        return [
            {"task": "T8", "bucket": "waiting", "deps": [], "task_branch": "feat/a"},
            {"task": "T9", "bucket": "waiting", "deps": [], "task_branch": "feat/orders-cicd"},
            {"task": "T46", "bucket": "waits-in-order", "deps": ["T8"], "task_branch": "feat/orders-cicd"},
        ]

    def prs(self):
        return {82: {"branch": "feat/orders-cicd", "tasks": ["T9"], "owner": "Person B"},
                73: {"branch": "feat/a", "tasks": ["T8"], "owner": "Person A"}}

    def test_open_task_on_branch_orders_the_prs(self):
        order = wp.merge_order(self.rows(), self.prs())
        self.assertEqual([item["pr"] for item in order], [73, 82])
        block = wp.merge_order_block(self.rows(), self.prs())
        self.assertIn("not ready to merge: T46 waits on T8 (PR 73)", block)

    def test_task_branches_from_tasks_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "tasks.md").write_text("- [ ] T46 Take in develop (after: T8) (branch: feat/orders-cicd)\n", encoding="utf-8")
            rows = [{"task": "T46"}]
            wp.apply_task_branches(Path(tmp), rows)
            self.assertEqual(rows[0]["task_branch"], "feat/orders-cicd")


class Deadlock(unittest.TestCase):
    def test_ready_check_blocks_a_deadlock(self):
        rows = [
            {"task": "T43", "bucket": "waiting", "deps": [], "merge_wait": {"branch": "feat/a", "pr": 73}},
            {"task": "T8", "bucket": "ready", "deps": ["T43"], "task_branch": "feat/a"},
        ]
        lines = wp.apply_merge_deadlocks(rows)
        self.assertEqual(len(lines), 1)
        self.assertEqual(rows[1]["bucket"], "blocked")
        hit = wp.classify(rows[1])
        self.assertEqual(hit["kind"], "blocker")
        self.assertIn("/crav1-tighten-plan", hit["why"])
        self.assertIn("PR 73", hit["why"])

    def test_other_branch_is_not_a_deadlock(self):
        rows = [
            {"task": "T43", "bucket": "waiting", "deps": [], "merge_wait": {"branch": "feat/a", "pr": 73}},
            {"task": "T8", "bucket": "ready", "deps": ["T43"], "task_branch": "feat/b"},
        ]
        self.assertEqual(wp.apply_merge_deadlocks(rows), [])

    def test_map_says_blocked(self):
        tasks = [{"id": 43, "done": False, "deps": []}, {"id": 8, "done": False, "deps": [43]}]
        text = bm.merge_deadlock(tasks, {43}, 73)
        self.assertTrue(text.startswith("blocked, merge deadlock: T8 waits on T43"))
        self.assertIsNone(bm.merge_deadlock(tasks, {43, 8}, 73))
        self.assertEqual(bm._ready_now({"deadlock": text, "status": "blocked"}), text)


class BuiltWaiting(unittest.TestCase):
    def test_built_claim_is_waiting(self):
        row = {"task": "T9", "bucket": "waiting", "claim": True, "claim_built": {"pr": 82},
               "reason": "built by person B, waits for PR 82 to merge"}
        self.assertEqual(wp.classify(row)["kind"], "waiting")
        row2 = {"task": "T9", "bucket": "blocked", "reason": "built by person B, waits for PR 82 to merge"}
        self.assertEqual(wp.classify(row2)["kind"], "waiting")

    def test_unrecognized_blocker_is_counted(self):
        source = (SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py").read_text(encoding="utf-8")
        self.assertEqual(source.count('row["unrecognized"] = True'), 2)


class EmptyQueue(unittest.TestCase):
    def test_names_ready_check_not_build_tasks(self):
        out = pc.empty_queue_next([], True, False, "orders-api")
        self.assertIn("/crav1-tasks-ready-to-build orders-api", out)
        self.assertNotIn("/crav1-build-tasks", out)
        self.assertTrue(out.startswith("Run next:"))

    def test_commit_first_inside_run_next(self):
        out = pc.empty_queue_next([], True, False, "orders-api", 7)
        self.assertLess(out.index("/crav1-finalize-commit"), out.index("/crav1-tasks-ready-to-build"))
        self.assertIn("Commit the 7 changed spec files:", out)


class ReopenTitles(unittest.TestCase):
    def test_match_and_in_the_code_are_not_named(self):
        titles = wp.reopen_titles("tighten-spec", ["match", "acceptance-criteria", "in-the-code"], [])
        self.assertEqual(titles, [wp.section_title("acceptance-criteria")])

    def test_synced_at_only_kept(self):
        self.assertEqual(wp.reopen_titles("tighten-spec", [], ["Synced at"]), ["Synced at"])


class UncommittedWording(unittest.TestCase):
    def test_changed_spec_files(self):
        text = we.catch_up_block("orders-api", [], [], 0, uncommitted=["a.md", "b.md", "c.md", "d.md"])
        self.assertIn("Commit the 4 changed spec files:\n`/crav1-finalize-commit`", text)
        self.assertNotIn("walk's changes", text)


class HeldDeps(unittest.TestCase):
    def test_unbuilt_dep_is_named(self):
        rows = [
            {"task": "T12", "bucket": "waiting", "deps": []},
            {"task": "T8", "bucket": "ready", "deps": []},
            {"task": "T17", "bucket": "waits-in-order", "deps": ["T12", "T8"]},
        ]
        hits = [{"task": "T12", "kind": "waiting"}]
        wp.propagate_held(rows, hits)
        self.assertIn("held, waits on T12", rows[2]["reason"])
        self.assertIn("and T8 (not built)", rows[2]["reason"])


class OwnerNames(unittest.TestCase):
    def test_read_cleans_stored_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(wp.pr_author(Path(tmp), 73, "PR author: Admin Person A\n"), "Person A")
            self.assertEqual(wp.pr_author(Path(tmp), 82, "PR author: Person B (Tag)\n"), "Person B")

    def test_rewrite_stored_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build-progress"
            folder.mkdir()
            (folder / "feat--a.md").write_bytes(b"Branch: feat/a\r\nPR author: Admin Person A\r\n- Step: build T8\r\n")
            (folder / "feat--b.md").write_text("Branch: feat/b\nPR author: Person B\n", encoding="utf-8")
            cleaned = wp.clean_stored_authors(Path(tmp))
            self.assertEqual(cleaned, ["feat--a.md"])
            self.assertEqual((folder / "feat--a.md").read_bytes(), b"Branch: feat/a\r\nPR author: Person A\r\n- Step: build T8\r\n")
            self.assertEqual(wp.clean_stored_authors(Path(tmp)), [])

    def test_recorded_line_names_files(self):
        line = wp.recorded_line({"merged": [71], "owners": {73: "Person A", 82: "Person B"},
                                 "files": ["feat--a.md"], "cleaned": []})
        self.assertEqual(line, "Recorded: PR 71 merged; PR authors for PR 73 and PR 82 (in build-progress/feat--a.md).")
        self.assertIsNone(wp.recorded_line({}))


class VerifyTick(unittest.TestCase):
    def run_tick(self, tmp, *extra):
        return json.loads(subprocess.run([sys.executable, str(VR), "tick", "--file", str(Path(tmp) / "verify.md"),
                                          "--task", "T5", *extra], capture_output=True, text=True).stdout)

    def test_tick_offer_and_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "tasks.md").write_text("- [ ] T5 Merge the PR\n", encoding="utf-8")
            Path(tmp, "verify.md").write_text("| Task | Title | Status | Verify |\n|---|---|---|---|\n"
                                              "| T5 | Merge | Implemented, verified | pass |\n", encoding="utf-8")
            out = self.run_tick(tmp, "--merged", "yes")
            self.assertTrue(out["offer"])
            label, command = out["run_next"].split("\n")
            self.assertTrue(label.endswith(":"))
            self.assertTrue(command.startswith("`") and command.endswith("`"))
            out = self.run_tick(tmp, "--merged", "yes", "--yes")
            self.assertTrue(out["wrote"])
            self.assertIn("- [x] T5", Path(tmp, "tasks.md").read_text(encoding="utf-8"))

    def test_not_implemented_verifies_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "tasks.md").write_text("- [ ] T5 Merge the PR\n", encoding="utf-8")
            Path(tmp, "verify.md").write_text("| Task | Title | Status | Verify |\n|---|---|---|---|\n"
                                              "| T5 | Merge | Not implemented | - |\n", encoding="utf-8")
            out = self.run_tick(tmp, "--merged", "yes")
            self.assertFalse(out["offer"])
            self.assertIn("/crav1-verify-build-against-spec", out["run_next"])


class Snapshots(unittest.TestCase):
    def test_snapshots_match_and_invariants_hold(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/snapshot-check.py")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("orders-api-deadlock: matches", proc.stdout)

    def test_deadlock_snapshot_leads_with_the_plan_fix(self):
        reply = (ROOT / "scripts/tests/snapshots/orders-api-deadlock/expected/reply.txt").read_text(encoding="utf-8")
        ending = reply.split("Result: not-ready", 1)[1].strip()
        self.assertTrue(ending.startswith("Run next:\n\nFix the merge deadlock in the plan"))
        self.assertIn("`/crav1-tighten-plan orders-api-deadlock`", reply)
        self.assertNotIn("then T2 can start", reply)

    def test_merge_wait_snapshot_cleans_names(self):
        folder = ROOT / "scripts/tests/snapshots/orders-api-merge-wait/expected/build-progress"
        texts = "".join(p.read_text(encoding="utf-8") for p in folder.glob("*.md"))
        self.assertIn("PR author: Person A\n", texts)
        self.assertIn("PR author: Person B\n", texts)
        reply = (ROOT / "scripts/tests/snapshots/orders-api-merge-wait/expected/reply.txt").read_text(encoding="utf-8")
        self.assertIn("Recorded: author names cleaned", reply)


class Invariants(unittest.TestCase):
    inv = load("crav1-tasks-ready-to-build/scripts/task_invariants.py", "inv_1180")

    def test_broken_invariants_are_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "tasks.md").write_text("- [x] T1 a\n- [ ] T2 b\n", encoding="utf-8")
            out = {"rows": [{"task": "T1", "bucket": "ready"}, {"task": "T2", "bucket": "blocked", "deadlock": "x"}],
                   "counts": {"ready": 1}, "reply": "Next: something\n", "result": "not-ready"}
            broken = " ".join(self.inv.check(Path(tmp), out))
            for code in ("I1", "I2", "I3", "I5", "I6"):
                self.assertIn(code, broken)


class SharedStateAgrees(unittest.TestCase):
    """The ready check, the build map and finalize-commit agree (1.180.0)."""

    def check_folder(self, name):
        import os
        import re
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / name
            shutil.copytree(ROOT / "scripts/tests/snapshots" / name / "spec", work)
            env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
            proc = subprocess.run([sys.executable, str(SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"),
                                   "readiness", "--root", str(work), "--full", "--write-map", "--skip-sync",
                                   "--user", "Person C"], capture_output=True, text=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
            ready = {row["task"]: row["state"] for row in out["rows"] if row.get("task")}
            parsed = bm.parse_tasks((work / "tasks.md").read_text(encoding="utf-8"))
            mapped = bm.apply_task_states(parsed, bm.progress_state(work))
            sliced = {task: state["state"] for task, state in ts.slice_states(work).items()}
            colour = ts.STATE_COLOUR
            self.assertEqual(set(ready), set(mapped))
            for task in ready:
                self.assertEqual(colour[ready[task]], colour[mapped[task]], f"{name} {task}: ready check vs build map")
                self.assertEqual(sliced[task], mapped[task], f"{name} {task}: finalize-commit vs build map")
            check = ts.commit_check(work)
            self.assertEqual(check["tick_pending"], sorted(t for t, st in mapped.items() if st == ts.TICK_PENDING))
            self.assertFalse(check["stop"])
            for task in check["tick_pending"]:
                self.assertEqual(ready[task], ts.DONE, "the ready check counts a tick-pending task done")
            # Box colours on the written map follow the same task states.
            text = (work / "build-map.md").read_text(encoding="utf-8")
            boxes = dict(re.findall(r'^\s*(b\d+)\["([^"]+)"\]', text, re.M))
            classes = {}
            for cls_ids, cls in re.findall(r"^\s*class ([\w,]+) (\w+)$", text, re.M):
                for box in cls_ids.split(","):
                    classes[box] = cls
            branch_of = {f"T{t['id']}": t.get("branch") for t in parsed}
            branches = {}
            tasks_md = (work / "tasks.md").read_text(encoding="utf-8")
            for num, branch in re.findall(r"T(\d+)\b.*\(branch: ([^)]+)\)", tasks_md):
                branches.setdefault(branch, []).append(f"T{int(num)}")
            for box, branch in boxes.items():
                ids = branches.get(branch) or []
                if ids and all(colour[ready[t]] == "done" for t in ids):
                    self.assertEqual(classes.get(box), "done", f"{name} {branch}")
                if any(ready[t] == ts.MERGE_WAIT for t in ids):
                    self.assertIn(classes.get(box), ("waiting", "blocked"), f"{name} {branch}")
            inv = load("crav1-tasks-ready-to-build/scripts/task_invariants.py", "inv_agree")
            self.assertEqual(inv.check(work, out), [])
            return check

    def test_tick_pending_snapshot(self):
        check = self.check_folder("orders-api-tick-pending")
        self.assertEqual(check["tick_pending"], ["T1"])
        self.assertEqual(check["recommend"], "commit")
        self.assertIn("/crav1-verify-build-against-spec orders-api-tick-pending", check["run_next"])

    def test_merge_wait_snapshot(self):
        self.check_folder("orders-api-merge-wait")

    def test_deadlock_snapshot(self):
        self.check_folder("orders-api-deadlock")

    def test_finalize_commit_wrapper_runs_the_shared_module(self):
        wrapper = SK / "crav1-finalize-commit/scripts/task_state.py"
        self.assertLess(len(wrapper.read_text(encoding="utf-8").splitlines()), 60, "a thin wrapper, no copied logic")
        proc = subprocess.run([sys.executable, str(wrapper), "commit-check", "--root",
                               str(ROOT / "scripts/tests/snapshots/orders-api-tick-pending/spec")],
                              capture_output=True, text=True)
        self.assertEqual(json.loads(proc.stdout)["tick_pending"], ["T1"])
        self.assertIn("scripts/task_state.py commit-check",
                      (SK / "crav1-finalize-commit/references/choice-words.md").read_text(encoding="utf-8"))

    def test_map_colour_is_box_state(self):
        self.assertIn("task_state.box_state(branch)", (SK / "crav1-tasks-ready-to-build/scripts/build_map.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
