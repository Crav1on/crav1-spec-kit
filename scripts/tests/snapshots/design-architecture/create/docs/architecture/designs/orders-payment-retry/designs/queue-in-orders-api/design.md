# Design: queue in orders-api

- Topic: orders-payment-retry
- Status: open
- Ask: "orders should retry failed payments without blocking checkout"

## End state

Not designed yet.

## Decisions

- Where a failed payment waits before retry
  - State: open
- Who owns the retry policy
  - State: open

## Drivers

- Checkout does not wait. (from you, this session)
- One team runs it. (docs/system/landscape.md)

## Ideas

- none yet
