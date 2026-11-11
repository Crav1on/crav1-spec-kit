# Build map

One branch per plan step.

```mermaid
flowchart LR
  subgraph w1["Wave 1"]
    direction TB
    b1["feat/cancel-booking-record-refund-decision"]
  end
  subgraph w2["Wave 2"]
    direction TB
    b2["feat/cancel-booking-send-receipt"]
  end
  b1 --> b2
```

An arrow means the later branch waits for the earlier one.

## Wave 1: 1 branch, 1 can start now

### feat/cancel-booking-record-refund-decision

- Delivers: Record the refund decision.
- Tasks: T1 Persist the decision; T2 Reject an unknown booking
- Waits for: none
- Question: none
- Ready now: ready

## Wave 2: 1 branch, 1 can start now

### feat/cancel-booking-send-receipt

- Delivers: Send the receipt.
- Tasks: T3 Email the receipt
- Waits for: feat/cancel-booking-record-refund-decision
- Question: none
- Ready now: waits in order
