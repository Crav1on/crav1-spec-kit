# Diagrams (landscape)

Write `docs/system/diagrams.md` from the repos you read. Each diagram: one heading, one sentence of what it is for, then one fenced block.

## Prefer Mermaid

One system-context diagram of what is actually there. Use `flowchart LR`. Keep node labels short. Do not invent services, queues, or a future product.

```mermaid
flowchart LR
  user[User] --> web[web repo]
  web --> api[api repo]
```

Slice sequences do not belong here. This command does not write `docs/specs/<slug>/diagrams.md`.

## Prefer ASCII

Use a `text` fence for a repo or module tree, or a one-line pipeline. Do not draw the same view as both mermaid and ascii unless the ascii is a one-line summary.

If a diagram encodes a choice that had real alternatives, that choice is a landscape ADR or the caption stays a description of what the code does. Do not invent the alternatives.
