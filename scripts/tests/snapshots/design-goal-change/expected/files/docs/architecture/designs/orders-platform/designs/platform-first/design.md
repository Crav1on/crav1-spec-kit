# Design: platform first

- Topic: orders-platform
- Status: open
- Ask: "split the orders platform so the target can grow on it"

## End state

Not designed yet.

## Decisions

- How test gets data
  - State: to-question
  - Options shown: Copy of prod data, Made-up data
  - Leaning: Made-up data
  - Recommended: Made-up data
  - Open question in: questions.md
- Where orders live
  - State: reopened
  - Options shown: One SQL database for orders, Event log per service
  - Draft ADR: designs/platform-first/adr/where-orders-live.md
  - Reopened: goal changed YYYY-MM-DD: names sql, store from a removed goal line
- Who ships orders
  - State: reopened
  - Options shown: A pipeline releases orders, Releases by hand
  - Draft ADR: designs/platform-first/adr/who-releases-orders.md
  - Reopened: goal changed YYYY-MM-DD: renamed from Who releases orders
  - Renamed from: Who releases orders
- How the target reads orders
  - State: dropped
  - Dropped: YYYY-MM-DD: the target topic decides it

## Drivers

- One team runs orders. (from you, this session)

## Ideas

- none yet
