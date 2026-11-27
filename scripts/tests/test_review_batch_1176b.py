"""1.176.0 review batch (part 2): ordered merge list, two-repo record,
verified-on-branch status, ending from build-progress, ADO body limit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import test_walk_owner_claims_1175 as base  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wp = load(WALK, "walk_progress_1176b")

README_PROGRESS = """# Build progress

Walk: build-walk
Branch: feat/orders-readme
Owner: self
PR author: person A
Tasks: T5 Orders README

- Step: open-pr
  Done: 2026-11-16T10:00:00+01:00
  Result: PR 71

- Step: wait-merge
  Done: 2026-11-16T10:05:00+01:00
  Result: waiting (PR 71)
"""


def two_pr_slice(tmp: str, t9_after: str = "T1", extra: str = "") -> Path:
    root = base.make_slice(tmp, user="person A")
    tasks = base.TASKS.replace("(after: T1)\n", f"(after: {t9_after})\n", 1)
    tasks += ("- [ ] T5: Orders README (branch: feat/orders-readme) (after: )\n"
              "- [ ] T6: Orders README links (branch: feat/orders-links) (after: T5)\n") + extra
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    (root / "claims.md").write_text(base.CLAIMS + "In progress: feat/orders-readme, T5, person A, since 2026-11-16T09:00:00+01:00\n", encoding="utf-8")
    (root / "build-progress" / "feat--orders-readme.md").write_text(README_PROGRESS, encoding="utf-8")
    base.stopped_walk(root)
    return root


def ending(root: Path) -> str:
    proc = subprocess.run([sys.executable, str(WALK), "readiness", "--root", str(root), "--skip-sync"],
                          capture_output=True, text=True, check=False)
    payload = json.loads(proc.stdout)
    return payload["ending"]


class OrderedMergeList(unittest.TestCase):
    def test_owners_and_unblocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = two_pr_slice(tmp)
            prs = wp.open_prs(root)
            self.assertEqual(prs[71]["owner"], "yours")
            self.assertEqual(prs[82]["owner"], "person B")
            text = ending(root)
            self.assertIn("Merge these PRs, in this order:\n"
                          "1. PR 71 (yours, feat/orders-readme): ticks T5, then T6 can start.\n"
                          "2. PR 82 (person B's, feat/orders-cicd): ticks T9 to T12, then T13 can start.", text)
            self.assertNotIn("Waiting: PR 71 to merge", text)
            self.assertNotIn("built, and wait for PR 82", text)
            self.assertNotIn("Next:", text.replace("Run next:", ""))
            self.assertIn("- feat/orders-cicd: built, PR 82 open", text)

    def test_a_pr_others_depend_on_comes_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            extra = "- [ ] T14: Orders alerts (branch: feat/orders-alerts) (after: T12)\n"
            root = two_pr_slice(tmp, extra=extra)
            order = [item["pr"] for item in wp.merge_order(wp.build_rows(root), wp.open_prs(root))]
            self.assertEqual(order, [82, 71], "more unblocked tasks wins a tie")
        with tempfile.TemporaryDirectory() as tmp:
            extra = "- [ ] T14: Orders alerts (branch: feat/orders-alerts) (after: T12)\n"
            root = two_pr_slice(tmp, t9_after="T1, T5", extra=extra)
            order = [item["pr"] for item in wp.merge_order(wp.build_rows(root), wp.open_prs(root))]
            self.assertEqual(order, [71, 82], "a PR the other depends on comes first")


import test_branch_run_1155 as brt  # noqa: E402

br = brt.br


def clone_pair(base_dir: Path, name: str) -> Path:
    bare = base_dir / f"{name}.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], check=True, capture_output=True)
    work = base_dir / name
    subprocess.run(["git", "clone", str(bare), str(work)], check=True, capture_output=True)
    for key, value in (("user.email", "person-a@example.com"), ("user.name", "person A"), ("commit.gpgsign", "false")):
        brt.git(work, "config", key, value)
    return work


class TwoRepoRecord(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.specs = clone_pair(self.base, "specs")
        self.code = clone_pair(self.base, "code")
        self.root = brt.write_slice(self.specs)
        (self.root / "verify.md").write_text("# Verify\n", encoding="utf-8")
        (self.root / "work-item.md").write_text("# Work item\n\nAB#2 Orders CI/CD\n", encoding="utf-8")
        brt.git(self.specs, "add", "-A")
        brt.git(self.specs, "commit", "-m", "Start")
        brt.git(self.specs, "push", "-u", "origin", "main")
        brt.git(self.code, "checkout", "-b", "feat/orders-cicd")
        (self.code / "a.txt").write_text("a", encoding="utf-8")
        brt.git(self.code, "add", "-A")
        brt.git(self.code, "commit", "-m", "Build T2")
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        brt.git(self.specs, "add", "-A")
        brt.git(self.specs, "commit", "-m", "Claim")

    def test_code_repo_passed_as_repo_no_longer_crashes(self):
        sha = brt.git(self.code, "rev-parse", "HEAD").stdout.strip()
        (self.root / "verify.md").write_text("# Verify\n\n- T2 evidence\n", encoding="utf-8")
        out = br.record(self.root, "feat/orders-cicd", "T2", sha, "green", self.code, push=True)
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["code_repo"], str(self.code.resolve()))
        self.assertEqual(out["specs_repo"], str(self.specs.resolve()))
        self.assertIn("docs/specs/orders-api/verify.md", out["files"])
        self.assertTrue(out["code_pushed"] and out["specs_pushed"], out)
        message = brt.git(self.specs, "log", "-1", "--format=%B").stdout
        self.assertIn("Record T2 on feat/orders-cicd with its verify evidence", message)
        self.assertIn("AB#2", message)
        self.assertEqual(brt.git(self.specs, "status", "--porcelain").stdout.strip(), "")

    def test_bad_specs_repo_writes_nothing(self):
        before = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        progress = br.progress_path(self.root, "feat/orders-cicd").read_text(encoding="utf-8")
        out = br.record(self.root, "feat/orders-cicd", "T2", "a1b2c3d", "green",
                        specs_repo=self.code, code_repo=self.code)
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "specs-repo")
        self.assertIn("Nothing was written", out["line"])
        self.assertEqual((self.root / "walk-progress.md").read_text(encoding="utf-8"), before)
        self.assertEqual(br.progress_path(self.root, "feat/orders-cicd").read_text(encoding="utf-8"), progress)


VERIFY_ON_BRANCH = """# Verify

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T5 | Orders README | Implemented, verified on branch | pass at 61dc1ce on feat/orders-readme, PR 71 open |
"""


class VerifiedOnBranch(unittest.TestCase):
    def test_status_is_known_everywhere(self):
        vr = load(SK / "crav1-verify-build-against-spec/scripts/verify_rows.py", "verify_rows_1176b")
        self.assertIn("Implemented, verified on branch", vr.STATUSES)
        tick = load(SK / "crav1-build-tasks/scripts/tick_only.py", "tick_only_1176b")
        self.assertFalse(tick.already_verified("Implemented, verified on branch"))
        self.assertTrue(tick.already_verified("Implemented, verified, tick pending"))
        we = load(SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py", "walk_ending_1176b")
        # 1.182.0: the old on-branch wording is the same state as tick pending.
        self.assertEqual(we.status_key("Implemented, verified on branch"), "tick_pending")
        self.assertEqual(we.status_key("Implemented, verified"), "verified")

    def test_ready_check_says_verified_on_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = two_pr_slice(tmp)
            (root / "verify.md").write_text(VERIFY_ON_BRANCH, encoding="utf-8")
            text = ending(root)
            self.assertIn("Orders README (T5) — verified on feat/orders-readme, waits for PR 71 to merge", text)
            self.assertNotIn("Not implemented", text)


BRANCH_RUN = SK / "crav1-build-walk/scripts/branch_run.py"


def run_cli(*args: str) -> dict:
    proc = subprocess.run([sys.executable, str(BRANCH_RUN), *args], capture_output=True, text=True, check=False)
    return json.loads(proc.stdout)


class EndingFromProgress(unittest.TestCase):
    def test_ending_reads_build_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = base.make_slice(tmp, user="person B")
            out = run_cli("ending", "--root", str(root), "--branch", "feat/orders-cicd",
                          "--note", "PR 82 needs one approver.")
            self.assertTrue(out["ok"], out)
            text = out["ending"]
            self.assertTrue(text.startswith("Run next:"))
            self.assertIn("Merge PR 82 into develop, after your yes:\n`/crav1-build-walk", text)
            self.assertIn("- Orders CI/CD: infra Bicep for dev, test and prod (T9): commit 1f2e3d4, tests green", text)
            self.assertTrue(text.rstrip().endswith("Before the merge:\n- PR 82 needs one approver."))
            self.assertNotIn("Next:", text.replace("Run next:", ""))

    def test_plain_stop_and_partial_rows_do_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "ending.json"
            state.write_text(json.dumps({"branch": "feat/orders-cicd", "stop": "merge", "pr": 82,
                                         "built": [{"task": "T9"}, "T10"]}), encoding="utf-8")
            out = run_cli("ending", "--json", str(state))
            self.assertTrue(out["ok"], out)
            self.assertIn("- T9\n- T10", out["ending"])


PR_COMMON = SK / "crav1-open-pr/scripts/pr_common.py"


def long_body(n: int = 40) -> str:
    tasks = "\n".join(
        f"- T{k} Orders CI/CD: deploy stage {k} with approvals. It deploys stage {k} after the stage before it passes, "
        f"waits for the approver, and runs the smoke checks against the environment before the next stage starts."
        for k in range(1, n + 1)
    )
    return ("Adds the orders-api deploy pipeline. Every stage deploys after the one before it passes.\n\n"
            "### Tasks\n" + tasks + "\n\n### Verified\nPipeline run 265 is green on feat/orders-cicd, 2026-11-14.\n\nAB#2\n")


class AdoBody(unittest.TestCase):
    def setUp(self):
        self.pc = load(PR_COMMON, "pr_common_1176b")

    def test_short_body_is_untouched(self):
        out = self.pc.fit_body("Adds the pipeline.\n\n### Tasks\n- T1 Add the pipeline. It builds.\n\nAB#2\n")
        self.assertEqual(out["trimmed"], [])
        self.assertTrue(out["fits"])

    def test_long_body_shortens_task_lines_and_adds_no_link(self):
        text = long_body()
        self.assertGreater(len(text), 4000)
        out = self.pc.fit_body(text)
        self.assertTrue(out["fits"], out["length"])
        body = out["body"]
        self.assertEqual(out["trimmed"], ["task-names"])
        self.assertIn("- T7 Orders CI/CD: deploy stage 7 with approvals.\n", body)
        self.assertIn("Task lines were shortened to fit.\n\n### Verified", body)
        self.assertNotIn("http", body)
        self.assertNotIn("Full notes", body)
        self.assertIn("Pipeline run 265 is green", body)
        self.assertTrue(body.rstrip().endswith("AB#2"))

    def test_very_long_task_names_are_cut_at_a_word(self):
        out = self.pc.fit_body(long_body(90), limit=4000)
        self.assertTrue(out["fits"], out["length"])
        self.assertIn("task-cut", out["trimmed"])
        self.assertNotIn("...", out["body"])
        self.assertIn("AB#2", out["body"])

    def test_no_notes_link_option(self):
        src = PR_COMMON.read_text(encoding="utf-8")
        self.assertNotIn("--notes-link", src)
        self.assertNotIn("Full notes", src)

    def test_cli_prints_the_body_and_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "body.md"
            body.write_text(long_body(), encoding="utf-8")
            proc = subprocess.run([sys.executable, "-X", "utf8", str(PR_COMMON), "fit", "--body", str(body), "--text"],
                                  capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertLessEqual(len(proc.stdout), 4000)
            self.assertEqual(body.read_text(encoding="utf-8"), long_body())


class OpenPrFormatB(unittest.TestCase):
    def test_draft_is_the_short_fixed_shape_with_no_links(self):
        text = (SK / "crav1-open-pr/references/draft.md").read_text(encoding="utf-8")
        self.assertIn("format B", text)
        self.assertIn("### Tasks", text)
        self.assertIn("No links at all", text)
        for gone in ("### Changes", "### Merge order", "head-commit link", "Full notes:"):
            self.assertNotIn(gone, text)
        ado = (SK / "crav1-open-pr/references/azure-devops.md").read_text(encoding="utf-8")
        self.assertNotIn("--notes-link", ado)
        self.assertIn("Task lines were shortened to fit.", ado)


class HelpSharedEnding(unittest.TestCase):
    def test_status_takes_run_next_from_the_ready_check(self):
        text = (SK / "crav1-help/references/status.md").read_text(encoding="utf-8")
        self.assertIn("readiness --root <spec-folder> --skip-sync --text", text)
        self.assertIn("Never write a `Next:` line", text)
        self.assertNotIn("--write-map`, so", text.replace("without `--write-map`, so", ""))


VERIFY_CRLF = (
    "# Verify\r\n\r\n| | Count | Ids |\r\n| --- | --- | --- |\r\n"
    "| Implemented, verified | 2 | T3, T1 |\r\n| Not implemented | 1 | T2 |\r\n"
    "| Implemented, verified on branch | 0 | |\r\n\r\n"
    "| T# | Title | Status | Verify |\r\n| --- | --- | --- | --- |\r\n"
    "| T1 | One | Implemented, verified | pass |\r\n| T2 | Two | Not implemented | none |\r\n"
    "| T3 | Three | Implemented, verified | pass |\r\n"
)


class VerifyRowsKeepTheFile(unittest.TestCase):
    def test_crlf_stays_and_unchanged_lists_keep_their_order(self):
        script = SK / "crav1-verify-build-against-spec/scripts/verify_rows.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "verify.md"
            path.write_bytes(VERIFY_CRLF.encode("utf-8"))
            proc = subprocess.run([sys.executable, str(script), "set", "--file", str(path), "--task", "T2",
                                   "--status", "Implemented, verified on branch",
                                   "--evidence", "pass at 61dc1ce on feat/orders-readme, PR 71 open", "--yes"],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            raw = path.read_bytes()
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
            text = raw.decode("utf-8")
            self.assertIn("| Implemented, verified | 2 | T3, T1 |", text)
            # 1.182.0: written as tick pending, the old count row renamed.
            self.assertIn("| Implemented, verified, tick pending | 1 | T2 |", text)
            self.assertNotIn("verified on branch", text)
            self.assertIn("| Not implemented | 0 |", text)


class SmallDocs(unittest.TestCase):
    def test_build_tasks_implement_has_no_next_line(self):
        text = (SK / "crav1-build-tasks/branches/implement/BRANCH.md").read_text(encoding="utf-8")
        self.assertNotIn("Next:", text)
        self.assertIn("`Verify this turn's tasks:` above `/crav1-verify-build-against-spec`", text)

    def test_branch_run_commit_needs_no_extra_reads(self):
        text = (SK / "crav1-build-walk/references/branch-run.md").read_text(encoding="utf-8")
        self.assertIn("Do not open finalize-commit for that commit", text)
        self.assertIn("ending --root <spec-folder> --branch <branch>", text)
        self.assertIn("--code-repo <code repo>", text)


LONG_TASKS = """# Tasks

- [ ] T2: `azuredevops/cd-orders.yml` , from PR 74's `cd-orders-prod.yml` , triggers on the develop branch and deploys every stage with approvals between them and a manual gate before production (branch: feat/orders-cicd) (after: )
- [ ] T3: Add the test stage (branch: feat/orders-cicd) (after: T2)
"""

VERIFY_TITLES = """# Verify

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | Orders CI/CD: deploy pipeline | Not implemented | none |
| T3 | Orders CI/CD: test stage | Not implemented | none |
"""


class PlanLabels(unittest.TestCase):
    def test_plan_label_is_the_verify_short_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = brt.write_slice(Path(tmp), tasks=LONG_TASKS)
            (root / "verify.md").write_text(VERIFY_TITLES, encoding="utf-8")
            plan = br.branch_plan(root, "feat/orders-cicd")
            labels = {row["id"]: row["label"] for row in plan["tasks"]}
            self.assertEqual(labels["T2"], "T2 Orders CI/CD: deploy pipeline")
            full = {row["id"]: row["full"] for row in plan["tasks"]}
            self.assertIn("azuredevops/cd-orders.yml,", full["T2"])
            self.assertNotIn(" ,", full["T2"])

    def test_without_verify_the_label_is_never_cut_with_dots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = brt.write_slice(Path(tmp), tasks=LONG_TASKS)
            plan = br.branch_plan(root, "feat/orders-cicd")
            label = plan["tasks"][0]["label"]
            self.assertFalse(label.endswith("..."), label)
            self.assertNotIn(" ,", label)


class BuildTasksHintInHelp(unittest.TestCase):
    def test_ready_check_ending_leaves_the_hint_to_help(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = base.make_slice(tmp, user="person B")
            text = ending(root)
            self.assertNotIn("/crav1-build-tasks builds one task without the walk.", text)
        status = (SK / "crav1-help/references/status.md").read_text(encoding="utf-8")
        self.assertIn("`/crav1-build-tasks <T#>` builds one task without the walk", status)


UK = load(SK / "crav1-update-kit/scripts/update_kit.py", "update_kit_1176b")
ASSETS = ".cursor/skills/crav1/crav1-finalize-commit/branches/message-only/assets"


class StyleRuleRewrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        b = Path(self.tmp.name)
        self.root, self.old, self.new = b / "repo", b / "old", b / "new"
        for tree, text in ((self.old, "style v1\r\n"), (self.new, "style v2 (crav1-finalize-commit/branches/message-only/references/style.md)\n")):
            path = tree / ASSETS / "draft-commit-style.mdc"
            path.parent.mkdir(parents=True)
            path.write_text(text, encoding="utf-8", newline="")
        (self.root / ".cursor/rules").mkdir(parents=True)
        (self.root / ".claude/rules").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stale_and_unchanged_rules_are_rewritten_and_hand_edits_stay(self):
        (self.root / ".cursor/rules/draft-commit-style.mdc").write_bytes(b"style v1\r\n")
        (self.root / ".claude/rules/draft-commit-style.md").write_text(
            "Read crav1-draft-commit-message/references/style.md\n", encoding="utf-8")
        (self.root / ".claude/rules/draft-commit-gitlog.md").write_text("my own words\n", encoding="utf-8")
        out = UK.style_rule_actions(self.root, self.old, self.new)
        self.assertEqual(sorted(out["update"]), [".claude/rules/draft-commit-style.md", ".cursor/rules/draft-commit-style.mdc"])
        self.assertEqual(out["payloads"][".cursor/rules/draft-commit-style.mdc"],
                         b"style v2 (crav1-finalize-commit/branches/message-only/references/style.md)\r\n")
        self.assertEqual(out["left"], [])

    def test_a_hand_edited_rule_is_left_and_listed(self):
        (self.root / ".cursor/rules/draft-commit-style.mdc").write_text("style stays\n", encoding="utf-8")
        out = UK.style_rule_actions(self.root, self.old, self.new)
        self.assertEqual(out["update"], [])
        self.assertEqual(out["left"][0]["path"], ".cursor/rules/draft-commit-style.mdc")


class TodoLayout(unittest.TestCase):
    def test_todo_items_use_label_above_command(self):
        text = (SK / "crav1-help/references/todo.md").read_text(encoding="utf-8")
        self.assertNotIn("Next: <skill>", text)
        self.assertIn("Answer the question:\n`/crav1-resolve-open-questions orders-api`", text)


class ReviewAndStatusReadFormatB(unittest.TestCase):
    def test_pr_status_takes_order_and_questions_from_the_kit(self):
        text = (SK / "crav1-pr-status/references/classify.md").read_text(encoding="utf-8")
        self.assertIn("format B", text)
        self.assertIn("`Merge these PRs, in this order:`", text)
        self.assertIn("`Order: not known from the kit's records.`", text)
        self.assertIn("Older descriptions (format A, 1.98.0)", text)
        self.assertNotIn("`/crav1-open-pr` writes these `###` sections", text)

    def test_review_pr_checks_the_short_body_task_by_task(self):
        first = (SK / "crav1-review-pr/references/first-section.md").read_text(encoding="utf-8")
        self.assertIn("A format B body (1.176.0) is compared task by task", first)
        self.assertIn("An older format A body (1.98.0) is compared bullet by bullet", first)
        checklist = (SK / "crav1-review-pr/references/checklist.md").read_text(encoding="utf-8")
        self.assertIn("the description is not the source", checklist)
        self.assertIn("`The kit has no recorded merge order for this pull request.`", checklist)
