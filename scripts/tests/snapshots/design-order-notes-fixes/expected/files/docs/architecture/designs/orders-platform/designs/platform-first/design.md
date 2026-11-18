# Design: platform first

- Topic: orders-platform
- Status: chosen
- Ask: "split the orders platform"

## End state

Not designed yet.

## Decisions

- Access model
  - State: open
  - Order: 3
- Backup policy
  - State: open
  - Order: 4
- Resource group names
  - State: open
  - Order: 2
  - Detail: yes
- Zone layout
  - State: leaning
  - Order: 1
  - Options shown: One zone, Two zones
  - Leaning: One zone
  - Drivers: Checkout does not wait; One team runs orders

## Drivers

- Checkout does not wait (docs/system/landscape.md)
- One team runs orders: fewer people on call

## Ideas

- none yet

## Small fixes

Accepted changes that need no design choice. Copied at go-ahead with no ADR.

- Rename the test queue to orders-test
