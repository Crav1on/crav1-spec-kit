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

Skip the question when the message already says which: a `Gap` id, `T#`, or "from verify" is option 1; a URL, a port, "live", or "local host" is option 2. When `verify.md` is missing and the message names no live gap, stop and name `/crav1-verify-spec`. An alias (`/crav1-fix-from-verify`, `/crav1-fix-live`) arrives with its choice already made.

## After

Each branch ends with its own recap and next step (`/crav1-verify-spec` to re-check). Do not run it.
