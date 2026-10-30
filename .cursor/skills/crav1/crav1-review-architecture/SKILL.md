---
name: crav1-review-architecture
description: >-
  Use when the user wants an architecture critique of the current spec. Starts
  the crav1-review-architecture-agent subagent for hunches vs decisions, ADR
  and diagram gaps, and numbered issues for /crav1-tighten-spec. Does not
  write application code.
disable-model-invocation: true
icon: shield
color: purple
---

# Start review-architecture

This skill is the **command**. You are the parent agent. Immediately delegate to the **crav1-review-architecture-agent** subagent. Load `.cursor/agents/crav1-review-architecture-agent.md` (drop-in) or this plugin’s `agents/crav1-review-architecture-agent.md`. Do not review in your own voice as a substitute. Do not edit files. Do not write application code.

## Find the spec

Use the spec folder the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug, then delegate.

Pass the subagent these paths (read-only): the user’s `spec.md`, `diagrams.md`, `adr/`, and `export/` if present. Also point it at this skill’s `assets/` (drop-in also has `.cursor/agent-assets/crav1-review-architecture-agent/`; plugin also has `agent-assets/crav1-review-architecture-agent/`) for **expected artifact shape**, not as the spec under review.

## What to tell the subagent

Instruct it to follow its own prompt and to finish with numbered **Issues for `/crav1-tighten-spec`** (`I1`, `I2`, …), one finding each. No single global patch recommendation.

## After it returns

Show the subagent’s review to the user. Then tell them the next command is `/crav1-tighten-spec` to walk those issues one by one. Do not start tightening in this turn unless they already asked.

Also name `/crav1-review-security` when they want a security pass on the design that now exists. That command is optional. Do not run it from this skill. Architecture review stays a critique of design hunches. It does not ask whether the thing is secure.
