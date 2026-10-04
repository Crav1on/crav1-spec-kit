#!/usr/bin/env python3
"""Generate the Claude Code drop-in (.claude/) from the Cursor drop-in (.cursor/).

Source of the playbooks is .cursor/ (and the plugin mirror of that tree).
This script does not read plugins/crav1/. It rewrites paths and the three host
differences: agent frontmatter, the project instruction, and commit-style rules.

  scripts/sync-crav1-claude.py          write .claude/
  scripts/sync-crav1-claude.py --check  exit non-zero if .claude/ is stale

Claude Code paths (verified against current docs, not invented):
  https://code.claude.com/docs/en/skills          .claude/skills/<name>/SKILL.md
  https://code.claude.com/docs/en/sub-agents      .claude/agents/*.md
  https://code.claude.com/docs/en/memory          .claude/CLAUDE.md and .claude/rules/*.md
  https://code.claude.com/docs/en/claude-directory

.claude/agent-assets/ is not a directory Claude Code loads by itself. Subagent
prompts tell the model to read those template files. They stay out of
.claude/agents/ because Claude Code scans that tree recursively.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

READONLY_TOOLS = "tools: Read, Grep, Glob"

# Longer prefixes first. Do not rewrite "~/.cursor/" (finalize-commit cites
# ~/.cursor/cli-config.json, which is a Cursor setting, not a Claude path).
PATH_REWRITES = (
    (".cursor/skills/crav1/", ".claude/skills/"),
    (".cursor/agents/", ".claude/agents/"),
    (".cursor/agent-assets/", ".claude/agent-assets/"),
    (".cursor/rules/draft-commit-style.mdc", ".claude/rules/draft-commit-style.md"),
    (".cursor/rules/draft-commit-gitlog.mdc", ".claude/rules/draft-commit-gitlog.md"),
    (".cursor/rules/gitkraken-commit-style.mdc", ".claude/rules/gitkraken-commit-style.md"),
    (".cursor/rules/gitkraken-commit-gitlog.mdc", ".claude/rules/gitkraken-commit-gitlog.md"),
    (".cursor/rules/crav1.mdc", ".claude/CLAUDE.md"),
)

COMMIT_STYLE_ASSETS = {
    "draft-commit-style.mdc",
    "draft-commit-gitlog.mdc",
}

TEXT_SUFFIXES = {".md", ".mdc", ".txt", ".json", ".yml", ".yaml"}

CLAUDE_INSTRUCTION_NOTE = """
On Claude Code this file is the project instruction (`.claude/CLAUDE.md`). A user-scope install uses the same text in `~/.claude/CLAUDE.md` and does not commit the kit into a client repo. Playbook paths that start with `.claude/` are the project drop-in. If that file is not in the repo, read the same path under `~/.claude/`.
""".strip()


def rewrite_paths(text: str) -> str:
    for old, new in PATH_REWRITES:
        text = text.replace(old, new)
    return clarify_rewritten_commit_rules(text)


def clarify_rewritten_commit_rules(text: str) -> str:
    """Drop Cursor labels whose paths were rewritten onto the Claude project path.

    The source names both hosts. After `.cursor/rules/*.mdc` becomes
    `.claude/rules/*.md`, the Cursor clause duplicates the Claude Code project
    clause. The Claude copy should name the Claude file once and still skip
    the style question when that file exists.
    """
    text = text.replace(
        "Cursor and Claude Code both count. If the file for the host you are running exists, do not ask.",
        "If a file in the table exists, do not ask.",
    )
    text = text.replace(
        "If a persist rule already exists, **do not ask**. Use it. Cursor and Claude Code both count.",
        "If a persist rule already exists, **do not ask**. Use it.",
    )
    text = re.sub(
        r"Cursor: `(\.claude/rules/[^`]+)`\. Claude Code project: `\1`\. ",
        r"Claude Code project: `\1`. ",
        text,
    )
    text = re.sub(
        r"- Cursor: `(\.claude/rules/[^`]+)` or `(\.claude/rules/[^`]+)` "
        r"\(legacy `(\.claude/rules/[^`]+)` or `(\.claude/rules/[^`]+)`\)\n",
        "",
        text,
    )
    text = re.sub(
        r"\| `(\.claude/rules/[^`]+)` \| [^|\n]+ \(Cursor\) \| `assets/draft-commit-[^`]+` \|\n",
        "",
        text,
    )
    text = re.sub(
        r"- `\.claude/rules/gitkraken-commit-style\.md` → CRAV1 style onward\n"
        r"- `\.claude/rules/gitkraken-commit-gitlog\.md` → git log onward\n",
        "",
        text,
    )
    text = re.sub(
        r"Cursor git-log file: `(\.claude/rules/[^`]+)` \(legacy `(\.claude/rules/[^`]+)`\)\. "
        r"Claude Code project: `\1` \(legacy `\2`\)\. ",
        r"Claude Code project: `\1` (legacy `\2`). ",
        text,
    )
    text = re.sub(
        r"Cursor style file: `(\.claude/rules/[^`]+)` \(legacy `(\.claude/rules/[^`]+)`\)\. "
        r"Claude Code project: `\1` \(legacy `\2`\)\. ",
        r"Claude Code project: `\1` (legacy `\2`). ",
        text,
    )
    return text


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :]


def transform_agent(text: str) -> str:
    """Map Cursor agent frontmatter onto Claude Code subagent fields.

    model: inherit is Claude's default, so it is omitted.
    readonly: true becomes tools: Read, Grep, Glob (the documented read-only set).
    readonly: false is omitted so the writer inherits edit tools.
    """
    fm, body = split_frontmatter(text)
    if fm is None:
        raise SystemExit("agent file is missing YAML frontmatter")
    readonly: bool | None = None
    kept: list[str] = []
    for line in fm.splitlines():
        stripped = line.strip()
        if stripped == "model: inherit":
            continue
        if stripped == "readonly: true":
            readonly = True
            continue
        if stripped == "readonly: false":
            readonly = False
            continue
        kept.append(line)
    if readonly is True:
        kept.append(READONLY_TOOLS)
    elif readonly is None:
        raise SystemExit("agent frontmatter has no readonly: true|false")
    body = rewrite_paths(body)
    if not body.startswith("\n"):
        body = "\n" + body
    return "---\n" + "\n".join(kept) + "\n---\n" + body


def transform_commit_style_asset(text: str) -> str:
    """Cursor .mdc rule → Claude rule body.

    .claude/rules/*.md with no paths frontmatter loads at session start
    (https://code.claude.com/docs/en/memory). alwaysApply is Cursor-only.
    """
    text = rewrite_paths(text)
    _fm, body = split_frontmatter(text)
    return body.lstrip("\n")


def transform_project_instruction(text: str) -> str:
    _fm, body = split_frontmatter(text)
    body = rewrite_paths(body).strip() + "\n\n" + CLAUDE_INSTRUCTION_NOTE + "\n"
    return body


def is_text(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    data = path.read_bytes()
    return b"\0" not in data


def rewrite_tree_files(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or not is_text(path):
            continue
        text = path.read_text(encoding="utf-8")
        if path.name in COMMIT_STYLE_ASSETS:
            updated = transform_commit_style_asset(text)
        else:
            updated = rewrite_paths(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def generate(cursor: Path, dest: Path) -> None:
    skills_src = cursor / "skills" / "crav1"
    agents_src = cursor / "agents"
    assets_src = cursor / "agent-assets"
    rule_src = cursor / "rules" / "crav1.mdc"
    for required in (skills_src, agents_src, assets_src, rule_src):
        if not required.exists():
            raise SystemExit(f"missing Cursor source: {required}")

    if dest.exists():
        shutil.rmtree(dest)
    (dest / "skills").mkdir(parents=True)
    (dest / "agents").mkdir(parents=True)

    for skill_dir in sorted(p for p in skills_src.iterdir() if p.is_dir()):
        shutil.copytree(skill_dir, dest / "skills" / skill_dir.name)
    rewrite_tree_files(dest / "skills")

    agent_files = sorted(agents_src.glob("crav1-*.md"))
    if not agent_files:
        raise SystemExit(f"no crav1 agents under {agents_src}")
    for agent in agent_files:
        text = transform_agent(agent.read_text(encoding="utf-8"))
        (dest / "agents" / agent.name).write_text(text, encoding="utf-8")

    shutil.copytree(assets_src, dest / "agent-assets")
    rewrite_tree_files(dest / "agent-assets")

    instruction = transform_project_instruction(rule_src.read_text(encoding="utf-8"))
    (dest / "CLAUDE.md").write_text(instruction, encoding="utf-8")

    leaked = list(dest.rglob("kit-maintainer.mdc"))
    if leaked:
        raise SystemExit(f"refusing to write kit-maintainer.mdc: {leaked}")
    validate(dest)


def validate(dest: Path) -> None:
    """Fail the generate if a host difference was dropped."""
    instruction = (dest / "CLAUDE.md").read_text(encoding="utf-8")
    if "alwaysApply" in instruction or instruction.startswith("---"):
        raise SystemExit(".claude/CLAUDE.md still looks like a Cursor rule")
    if "docs/specs/" not in instruction:
        raise SystemExit(".claude/CLAUDE.md lost the kit instruction")

    for agent in sorted((dest / "agents").glob("crav1-*.md")):
        fm, _body = split_frontmatter(agent.read_text(encoding="utf-8"))
        if fm is None:
            raise SystemExit(f"{agent.name} lost frontmatter")
        if "readonly:" in fm or "model:" in fm:
            raise SystemExit(f"{agent.name} still has Cursor frontmatter")
        has_tools = "tools:" in fm
        if has_tools and READONLY_TOOLS not in fm:
            raise SystemExit(f"{agent.name} tools are not the documented read-only set")
        if has_tools and any(token in fm for token in ("Write", "Edit", "Bash")):
            raise SystemExit(f"{agent.name} read-only tools include a write tool")

    for asset_name in COMMIT_STYLE_ASSETS:
        matches = list((dest / "skills").rglob(asset_name))
        if len(matches) != 1:
            raise SystemExit(f"expected one {asset_name}, found {matches}")
        text = matches[0].read_text(encoding="utf-8")
        if "alwaysApply" in text or ".cursor/rules/" in text:
            raise SystemExit(f"{asset_name} was not rewritten for Claude Code")
        if ".claude/rules/" not in text:
            raise SystemExit(f"{asset_name} does not name the Claude rules path")


def check(cursor: Path, committed: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="crav1-claude-") as tmp:
        fresh = Path(tmp) / "claude"
        generate(cursor, fresh)
        if not committed.exists():
            print("Committed .claude/ is missing.", file=sys.stderr)
            print("Run scripts/sync-crav1-plugin.sh (it regenerates .claude/).", file=sys.stderr)
            return 1
        result = subprocess.run(
            ["diff", "-ru", str(fresh), str(committed)],
            check=False,
        )
        if result.returncode == 0:
            print("Claude drop-in matches a fresh generate (.claude/)")
            return 0
        print("Committed .claude/ does not match a fresh generate.", file=sys.stderr)
        print("Run scripts/sync-crav1-plugin.sh (it regenerates .claude/).", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed .claude/ tree is stale",
    )
    args = parser.parse_args()
    root = args.root or Path(__file__).resolve().parent.parent
    cursor = root / ".cursor"
    dest = root / ".claude"
    if args.check:
        return check(cursor, dest)
    generate(cursor, dest)
    print("Synced .cursor/ → .claude/ (generated Claude Code drop-in)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
