"""The path guard refuses anything outside the phase-1 list, and the 1.x line check."""

from __future__ import annotations

import unittest

import support  # noqa: F401  puts v2/ on sys.path before crav1_2 imports
from crav1_2.errors import PathGuardError
from crav1_2.lines import one_x_lines_unchanged, owned_mark_lines
from crav1_2.paths import GITATTRIBUTES, guarded_append, guarded_write
from crav1_2.repo import init_repo

from support import temp_dir


BEFORE = """## Constraints
- The feed to partner B runs over the existing secure channel.
- Security S2: inbound calls are accepted only from listed private networks.

## Open questions
- Who gets the certificate-expiry alert, and how early?
  Blocks: T9
"""

AFTER = """## Constraints
- The feed to partner B runs over the existing secure channel.
- The outbound messaging channel is not built in this slice. [src: F-0031 verbal] <!-- crav1-2:item I-0017 -->
  Full source: sot/facts.md#F-0031
- Security S2: inbound calls are accepted only from listed private networks.

## Open questions
- Who gets the certificate-expiry alert, and how early?
  Blocks: T9
  See also: sot/facts.md#F-0035 <!-- crav1-2:item I-0021 -->
"""


class Lines(unittest.TestCase):
    def test_owned_lines_do_not_count_as_a_1x_change(self):
        self.assertTrue(one_x_lines_unchanged(BEFORE, AFTER))
        changed = AFTER.replace("partner B", "partner C")
        self.assertFalse(one_x_lines_unchanged(BEFORE, changed))
        marked = AFTER.replace(
            "The outbound messaging channel is not built in this slice.",
            "**New:** The outbound messaging channel is not built in this slice.",
        )
        self.assertTrue(owned_mark_lines(marked))

    def test_crlf_only_is_not_a_change(self):
        self.assertTrue(one_x_lines_unchanged(BEFORE, BEFORE.replace("\n", "\r\n")))


class Guard(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.root, ignore_errors=True))
        init_repo(self.root)
        spec = self.root / "docs" / "specs" / "partner-b-feed" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(BEFORE, encoding="utf-8")

    def test_refuses_the_forbidden_list(self):
        for rel in (
            ".cursor/skills/crav1/crav1-help/SKILL.md",
            ".claude/CLAUDE.md",
            ".crav1/kit.json",
            "docs/notes/2026-11/note.md",
            "docs/sources/2026-11-25-outbound-channel/README.md",
            "docs/system/repos.md",
            ".gitattributes",
            "src/app.py",
            "README.md",
            "docs/specs/partner-b-feed/notes.md",
            "sot/not-a-date/note.md",
            ".crav1-2/secret.txt",
        ):
            with self.assertRaises(PathGuardError, msg=rel):
                guarded_write(self.root, rel, b"no\n")
            self.assertFalse((self.root / rel).exists(), rel)

    def test_spec_write_allows_only_2_0_lines(self):
        guarded_write(self.root, "docs/specs/partner-b-feed/spec.md", AFTER.encode("utf-8"))
        self.assertEqual((self.root / "docs/specs/partner-b-feed/spec.md").read_text(encoding="utf-8"), AFTER)
        with self.assertRaises(PathGuardError):
            guarded_write(self.root, "docs/specs/partner-b-feed/spec.md", AFTER.replace("partner B", "partner C").encode())
        with self.assertRaises(PathGuardError):
            guarded_write(
                self.root,
                "docs/specs/partner-b-feed/spec.md",
                AFTER.replace("The outbound", "**New:** The outbound").encode(),
            )
        missing = self.root / "docs" / "specs" / "other-feed"
        with self.assertRaises(PathGuardError):
            guarded_write(self.root, "docs/specs/other-feed/spec.md", AFTER.encode())
        self.assertFalse(missing.exists())

    def test_events_are_append_only_and_views_are_allowed(self):
        with self.assertRaises(PathGuardError):
            guarded_write(self.root, ".crav1-2/events.jsonl", b'{"v":1}\n')
        guarded_append(self.root, ".crav1-2/events.jsonl", '{"kept":true}\n'.encode())
        self.assertEqual((self.root / ".crav1-2" / "events.jsonl").read_bytes(), b'{"kept":true}\n')
        guarded_write(self.root, "sot/index.md", b"# SoT index\n")
        guarded_write(self.root, "sot/2026-11-25-outbound-channel/note.md", "# Note\n".encode())
        png = b"\x89PNG\r\n\x1a\n\x00\x00"
        guarded_write(self.root, "sot/2026-11-25-outbound-channel/screenshot-1.png", png)
        self.assertEqual((self.root / "sot/2026-11-25-outbound-channel/screenshot-1.png").read_bytes(), png)
        with self.assertRaises(PathGuardError):
            guarded_write(self.root, "sot/2026-11-25-outbound-channel/note.md", b"**New:** no\n")
        self.assertEqual((self.root / ".crav1-2" / ".gitattributes").read_bytes(), GITATTRIBUTES)

    def test_symlink_escape_is_refused(self):
        outside = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(outside, ignore_errors=True))
        link = self.root / ".crav1-2" / "sessions"
        link.rmdir()
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(PathGuardError):
            guarded_write(self.root, ".crav1-2/sessions/s-0001.json", b"{}\n")
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
