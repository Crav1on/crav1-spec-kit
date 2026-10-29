"""Unit and golden tests for the dependency-order sort. Run: python3 -m unittest discover -s scripts/tests"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("task_order", ROOT / "scripts/task-order.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
to = wrapper.load()
FIX = pathlib.Path(__file__).parent / "fixtures"


def run(text, failed=()):
    return to.analyse(to.parse(text), failed)


class TaskOrder(unittest.TestCase):
    def test_golden_xbid(self):
        res = run((FIX / "xbid-tasks.md").read_text())
        self.assertEqual(to.render(res) + "\n", (FIX / "xbid-expected.txt").read_text())

    def test_xbid_from_start(self):
        text = (FIX / "xbid-tasks.md").read_text().replace("- [x] T1", "- [ ] T1")
        res = run(text)
        self.assertEqual(res["order"], [1, 2, 7, 3, 6, 4, 5])
        self.assertEqual(res["ready"], [1])
        self.assertEqual(res["next"], 1)

    def test_linear_no_after_matches_file_order(self):
        res = run("- [ ] T1: a\n- [ ] T2: b\n- [ ] T3: c\n")
        self.assertEqual(res["order"], [1, 2, 3])
        self.assertEqual(res["ready"], [1])
        self.assertEqual(res["blocked"][0]["reason"], "waits on T1 (inferred)")

    def test_mixed_no_after_waits_on_previous_only(self):
        res = run("- [ ] T1: a\n- [x] T2: b (after: T1)\n- [ ] T3: c\n")
        self.assertIn(3, res["ready"])  # T3 waits on T2 only, which is done

    def test_parallel_tie_break_and_next_unblocks_most(self):
        text = "- [x] T1: a\n- [ ] T2: b (after: T1)\n- [ ] T3: c (after: T1)\n- [ ] T4: d (after: T3)\n- [ ] T5: e (after: T4)\n"
        res = run(text)
        self.assertEqual(res["order"], [2, 3, 4, 5])
        self.assertEqual(res["ready"], [2, 3])
        self.assertEqual(res["next"], 3)  # T3 unblocks T4 and T5

    def test_next_tie_lowest_number(self):
        res = run("- [ ] T1: a (after: )\n- [ ] T2: b (after: )\n")
        self.assertEqual(res["next"], 1)

    def test_cycle(self):
        res = run("- [ ] T1: a\n- [ ] T2: b (after: T3)\n- [ ] T3: c (after: T2)\n")
        reasons = {r["id"]: r["reason"] for r in res["blocked"]}
        self.assertTrue(reasons[2].startswith("cycle T2 → T3 → T2"))
        self.assertTrue(reasons[3].startswith("cycle"))
        self.assertEqual(res["ready"], [1])
        self.assertEqual(res["order"][-2:], [2, 3])

    def test_missing_dependency(self):
        res = run("- [ ] T1: a (after: T9)\n- [ ] T2: b (after: T1)\n")
        reasons = {r["id"]: r["reason"] for r in res["blocked"]}
        self.assertEqual(reasons[1], "after: T9 names no task (recorded)")
        self.assertEqual(reasons[2], "waits on T1 (recorded)")
        self.assertIsNone(res["next"])

    def test_ticked_tasks_left_out(self):
        res = run("- [x] T1: a\n- [x] T2: b\n- [ ] T3: c\n")
        self.assertEqual(res["order"], [3])
        self.assertEqual(res["ready"], [3])

    def test_depends_on_failed(self):
        res = run((FIX / "xbid-tasks.md").read_text(), failed=[7])
        self.assertEqual(res["depends_on_failed"], {"T3": "depends on T7 (failed)", "T4": "depends on T7 (failed)",
                                                    "T5": "depends on T7 (failed)", "T6": "depends on T7 (failed)"})

    def test_titles_strip_marks(self):
        res = run("- [ ] T1: Do it (verify: unit — x) (spec: R1) (branch: feat/orders-retry)\n")
        self.assertEqual(res["rows"][0]["title"], "Do it")


if __name__ == "__main__":
    unittest.main()
