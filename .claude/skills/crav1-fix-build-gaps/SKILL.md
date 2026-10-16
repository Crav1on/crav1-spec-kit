---
name: crav1-fix-build-gaps
description: >-
  Fix gaps a build left, one at a time, inside the spec. Opens with one
  question: gaps from the verify report (verify failed, then unverified,
  then G#), or a live-site gap (ports, proxy, SQL, unpublished URL). Skips
  the question when the message already says which. Re-runs the evidence
  after each fix. Does not edit spec.md. Does not auto-pick unimplemented
  tasks. Replaces fix-from-verify and fix-live (their rules are kept as
  branches).
disable-model-invocation: true
icon: wrench
color: orange
---

# Fix build gaps

You fix gaps after a build, one at a time, and re-run the evidence. You do not edit `spec.md`.

This replaces `/crav1-fix-from-verify` and `/crav1-fix-live` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answer picks, in full.

## Opening question

Ask one question, with the questions tool when it is available:

1. **Gaps from the verify report.** `verify.md` lists verify failed, claimed done and unverified, or `G#` gaps. Follow [branches/verify-gaps/BRANCH.md](branches/verify-gaps/BRANCH.md).
2. **A live-site gap.** The gap is on a running host or the inner loop: ports, a proxy, SQL, an unpublished URL. Follow [branches/live-gaps/BRANCH.md](branches/live-gaps/BRANCH.md).

Skip the question when the message already says which: a `Gap` id, `T#`, or "from verify" is option 1; a URL, a port, "live", or "local host" is option 2. When `verify.md` is missing and the message names no live gap, stop and name `/crav1-verify-build-against-spec`.

When the message or the files make one option the better fit, list it first and end its label with ` (Recommended)`. Otherwise keep the order above with no label.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Which gaps: `verify gaps` / `live gaps`.

When the invocation contains one of these words (for example `/crav1-fix-build-gaps verify gaps`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: verify gaps, live gaps.`

## After

Each branch ends with its own recap and next step (`/crav1-verify-build-against-spec` to re-check). Do not run it.
