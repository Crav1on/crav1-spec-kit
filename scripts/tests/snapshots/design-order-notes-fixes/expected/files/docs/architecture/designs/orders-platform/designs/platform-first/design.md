# Design: platform first

- Topic: orders-platform
- Status: chosen
- Ask: "split the orders platform"

## End state

Not designed yet.

## Decisions

- Zone layout
  - State: leaning
  - Options shown: One zone, Two zones
  - Leaning: One zone
  - Drivers: Checkout does not wait; One team runs orders
- Resource group names
  - State: open
  - Detail: yes
- Access model
  - State: open
- Backup policy
  - State: open

## Drivers

- Checkout does not wait (docs/system/landscape.md)
- One team runs orders: fewer people on call

## Ideas

- none yet

## Small fixes

Accepted changes that need no design choice. Copied at go-ahead with no ADR.

- Rename the test queue to orders-test
