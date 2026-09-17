---
name: architecture-reviewer
description: Start the architecture-reviewer subagent on the current spec. Use when the user wants an architecture critique, hunches vs decisions, ADR/diagram gaps, and a numbered issue list for /tighten-spec. Do not write application code.
disable-model-invocation: true
icon: shield
color: purple
---

# Start architecture-reviewer

This skill is the **command**. You are the parent agent. Immediately delegate to the **architecture-reviewer** subagent (`.cursor/agents/architecture-reviewer.md`). Do not review in your own voice as a substitute. Do not edit files. Do not write application code.

## Find the spec

Use the spec folder the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug, then delegate.

Pass the subagent these paths (read-only): `spec.md`, `diagrams.md`, `adr/`, and `export/` if present.

## What to tell the subagent

Instruct it to follow its own prompt and to finish with numbered **Issues for `/tighten-spec`** (`I1`, `I2`, …), one finding each. No single global patch recommendation.

## After it returns

Show the subagent’s review to the user. Then tell them the next command is `/tighten-spec` to walk those issues one by one. Do not start tightening in this turn unless they already asked.
