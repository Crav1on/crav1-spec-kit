# Goal: orders-platform

- Ask: "split the orders platform so the target can grow on it"

## End goal

Orders run as their own platform that a later target can build on.

## Drivers

- One team runs orders. (from you, this session)

## Constraints

- none yet

## Criteria

- Checkout stays fast in prod
- Can be tried in test before prod
- Does not block the target

## Goal changes

- YYYY-MM-DD: the target owns how it reads orders
  - Dropped decision: How the target reads orders (the target topic decides it)
  - Input: inputs/goal-change-2.json
- YYYY-MM-DD: SQL is out of scope
  - Removed constraint: Orders stay in one SQL store. (docs/architecture/spec.md)
  - Added criterion: Does not block the target
  - Renamed decision: Who releases orders to Who ships orders
  - Added decision: How the target reads orders
  - Needs another look: Where orders live (names sql, store from a removed goal line)
  - Needs another look: Who ships orders (renamed from Who releases orders)
  - Input: inputs/goal-change-1.json

## Applied inputs

Saved goal files in inputs/ that are already in this goal.

- inputs/goal-change-1.json@9d83a6da17
- inputs/goal-change-2.json@6d088b8c47
