# Go-ahead

If the topic has more than one design, first pick the chosen one, with the `compare.md` scores and a recommendation.

## 0. A linked topic waits for its base

A topic created with `--builds-on` has its own go-ahead and design pull request. Its go-ahead waits until the base topic's design pull request is merged into the default branch. The script looks for the base design under `## Decided, not built yet` or `## Confirmed` in `docs/architecture/spec.md` on the repo's default branch (`origin/HEAD`, else `origin/main`, then `origin/master`; 1.191.0). Until then it refuses and prints a Run next with a Waiting line naming the base pull request; give that text as-is. Pass `--base-merged` only after the user confirms the base pull request is merged and main has not been fetched yet.

## 1. Review, automatically

Run the script move `review --topic <topic>`, then review in the spirit of `/crav1-review-architecture`: gaps against the goal (including environments, hosting, data flows, integrations and deployment), conflicts with what is already built or documented in environment and infrastructure docs, and decisions that are missing. Show the findings.

Card: What should happen with these findings?
- **Fix them first (Recommended)** (`fix`): go back to the open points in the design folder; nothing is copied yet. Why: the copy is what other skills read.
- **Accept and copy** (`accept`): keep the findings as they are and copy the chosen design now.

Ordinary sessions do not run this review.

## 2. Copy, clean

Only after the findings are fixed or accepted, run `go-ahead`, with `--slice <slug>` when the design affects one slice and `--accept-findings` when the user accepted findings. Without accepted findings the script writes nothing. It then:

- copies the chosen design's end state, and its stages if any, as one block under `## Decided, not built yet` in `docs/architecture/spec.md`, with a "Designed in" link and links to the accepted ADRs. It never writes under `## Confirmed`. `/crav1-existing-to-specs recheck` later moves parts up to `## Confirmed` once the code or the environment shows them;
- copies still-open questions into that spec's `## Open questions`, still naming who has the fact or decides;
- copies only the chosen design's draft ADRs, marked `accepted` and numbered, into `docs/system/adr/` or `docs/specs/<slug>/adr/`, each with a "Designed in" link;
- adds the design's draft diagrams to `docs/system/diagrams.md` or the slice's `diagrams.md` as a planned section, dashed parts labelled `planned`;
- copies the design's small fixes, if any, as a `Small fixes (no design choice)` list in the same block, with no ADR;
- marks the chosen design `chosen` and the others `rejected`. Rejected designs keep their draft ADRs in the sandbox.

## 3. Merge the design branch

The design branch is merged through a normal pull request with no tag. This skill does not push, open the pull request, merge, tag or release. The ending names pushing the branch first, then opening its pull request, and names no planning step. Planning starts only after that pull request is merged.
