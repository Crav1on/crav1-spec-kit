# Build map

To zoom the diagram, run `/crav1-tasks-ready-to-build cancel-booking open-map`. To share the map as one file, run `/crav1-tasks-ready-to-build cancel-booking export-map`.

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
  subgraph legend["Legend"]
    direction TB
    key1["Done"]
    key2["Waits on a PR or question"]
    key3["Blocked"]
    key4["Ready or not started"]
  end
  b1 --> b2
  classDef blocked fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fef2f2
  classDef waiting fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fffbeb
  classDef todo fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#eff6ff
  classDef done fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#f0fdf4
  class key3 blocked
  class key2 waiting
  class b1,b2,key4 todo
  class key1 done
  style w1 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style w2 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style legend fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  linkStyle default stroke:#60a5fa,stroke-width:2px
  linkStyle 0 stroke:#60a5fa,stroke-width:2px
```

An arrow means the later branch waits for the earlier one.

## Wave 1: 1 branch, 1 can start now

### feat/cancel-booking-record-refund-decision

- Delivers: Record the refund decision.
- Tasks: T1 Persist the decision; T2 Reject an unknown booking
- Waits for: none
- Question: none
- Ready now: ready

## Wave 2: 1 branch, 0 can start now

### feat/cancel-booking-send-receipt

- Delivers: Send the receipt.
- Tasks: T3 Email the receipt
- Waits for: feat/cancel-booking-record-refund-decision
- Question: none
- Ready now: waits in order
