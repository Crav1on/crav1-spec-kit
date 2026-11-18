# Design: platform first

- Topic: orders-platform
- Status: open
- Ask: "split the orders platform so the target can grow on it"

## End state

Not designed yet.

## Decisions

- How test gets data
  - State: open
- Where orders live
  - State: settled
  - Options shown: One SQL database for orders, Event log per service
  - Draft ADR: designs/platform-first/adr/where-orders-live.md
- Who releases orders
  - State: settled
  - Options shown: A pipeline releases orders, Releases by hand
  - Draft ADR: designs/platform-first/adr/who-releases-orders.md

## Drivers

- One team runs orders. (from you, this session)

## Ideas

- none yet
