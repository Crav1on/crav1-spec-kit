# report-change-full

Everything about one change: the change, what it runs on, its pipelines, and the discussion. Rules: `reports/common.md`.

Diagrams: a `gitGraph` for branches and merges; a `flowchart` per pipeline (trigger → stages → target); a `sequenceDiagram` for the discussion timeline when there are several turns. C4 only when the change alters architecture or pipelines: then C4 level 1 and 2 of the parts it touches. Otherwise leave **Architecture** to one plain flowchart.

```markdown
# <Change> explained

## Verdict
## The 30-second version
## Architecture: what runs where
## Branches
## Pipelines today          (what each pipeline does, one row each)
## What the change does     (files, size, before → after)
## The discussion           (who said what, dated, from what is written)
### Point by point          (agreed | open | dropped)
## Where it's heading
### The order of work       (dependency order)
## Watch-outs
## Decisions still open     (options as written, for and against)
## Either way
## Do not touch
## Seen only live
## Research marked stale
## Tracked elsewhere
## Source
```

People come only from what is written. The sections from **Either way** on follow `references/answer.md` ("Answer sections").
