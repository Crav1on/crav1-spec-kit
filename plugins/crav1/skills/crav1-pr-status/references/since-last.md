# crav1-pr-status: since last

Read only on `since last`, from **Since last** in `SKILL.md`.

## Your Read line

Every run writes `- Read: <your name> | <head short sha>, push <n>, newest comment <YYYY-MM-DDTHH:MMZ> | <date>` in the record, replacing your own earlier line. `<n>` is the Azure DevOps iteration id, or the GitHub commit count on the source branch. The newest comment is the latest `publishedDate` or `lastUpdatedDate` (GitHub `created_at` or `updated_at`) of a non-system comment.

## What changed

Compare the host now with your `Read` line and the record:

- New pushes: `Sam pushed 2 commits (push 7, 7b41a0c).`
- New or edited comments since the newest comment time, by thread.
- New threads, as new points.
- Each Point whose status or flags changed: `4. src/orders/handler.py:238-244: agreed -> done 3c9d2e1.`
- `Order` and `Ready` changes, and a host state change.

Print the heading, then `Since your last run on <date> (<sha>, push <n>):`, then those lines, then the verdict line and the `Ready` line as the full view gives them, and the offers. Nothing changed: `Nothing new since your last run on <date>.` and the verdict line.

The record is still written in full, so the next run compares with this one. Someone else's `Read` line is never used or changed.
