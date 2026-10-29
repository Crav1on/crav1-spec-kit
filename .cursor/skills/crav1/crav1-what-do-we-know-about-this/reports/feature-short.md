# report-feature-short

One screen: what the feature is and how it works. Rules: `reports/common.md`.

Diagrams: one `flowchart` of the main flow. Add one `sequenceDiagram` only when the flow is a back-and-forth between parts. No C4.

```markdown
# <Feature>: what it is and how it works

## Verdict
<one line: what is true, what is blocked, what is next>

## What it is
<short paragraph in the docs' words>

## At a glance
| | |
| --- | --- |
| Status | <from spec or tasks> |
| Main parts | <names> |
| Inputs / outputs | <names> |

## How it works
<flowchart, then 3–6 numbered steps>

## Source
<slice path, files, live reads>
```
