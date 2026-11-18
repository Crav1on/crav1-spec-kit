# Design: platform first

- Topic: orders-platform
- Status: chosen
- Ask: "split the orders platform so the target can grow on it"

## End state

Not designed yet.

## Decisions

- How test gets data
  - State: settled
  - Options shown: Made-up data, Copy of prod data
  - Draft ADR: designs/platform-first/adr/how-test-gets-data.md
- Where orders live
  - State: reopened
  - Options shown: One SQL database for orders, Event log per service
  - Draft ADR: designs/platform-first/adr/where-orders-live.md
  - Reopened: revisit from topic orders-target YYYY-MM-DD: the target needs its own read copy
- Who releases orders
  - State: settled
  - Options shown: A pipeline releases orders, Releases by hand
  - Draft ADR: designs/platform-first/adr/who-releases-orders.md

## Drivers

- One team runs orders. (from you, this session)

## Ideas

- none yet
