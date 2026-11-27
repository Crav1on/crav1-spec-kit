# Build map

The plan has no steps, so this map uses one branch per task.

```mermaid
flowchart LR
  subgraph w1["Wave 1"]
    direction TB
    b1["feat/orders-store"]
  end
  subgraph w2["Wave 2"]
    direction TB
    b2["feat/orders-cicd"]
  end
  subgraph w3["Wave 3"]
    direction TB
    b3["feat/orders-deploy"]
  end
  subgraph legend["Legend"]
    direction TB
    key1["Done"]
    key2["Waits on a PR or question"]
    key3["Blocked"]
    key4["Ready or not started"]
  end
  b1 -.-> b2
  b2 -.-> b3
  classDef blocked fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fef2f2
  classDef waiting fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fffbeb
  classDef todo fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#eff6ff
  classDef done fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#f0fdf4
  class key3 blocked
  class b1,b2,b3,key2 waiting
  class key4 todo
  class key1 done
  style w1 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style w2 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style w3 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style legend fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  linkStyle default stroke:#60a5fa,stroke-width:2px
  linkStyle 0 stroke:#fbbf24,stroke-width:2px
  linkStyle 1 stroke:#fbbf24,stroke-width:2px
```

An arrow means the later branch waits for the earlier one.

## Wave 1: 1 branch, 0 can start now, 1 done

### feat/orders-store

- Tasks:
  - ~~Add the idempotency key column (T1)~~ ✓ done (feat/orders-store)
  - Store a retried order once (T2)
- Waits for: none
- Question: none
- Ready now: built, waits for PR 11 to merge

## Wave 2: 1 branch, 0 can start now

### feat/orders-cicd

- Tasks:
  - Add the build pipeline (T3)
  - Take in develop after PR 11 merges (T4)
- Waits for:
  - feat/orders-store
- Question: none
- Ready now: held, waits on feat/orders-store

## Wave 3: 1 branch, 0 can start now

### feat/orders-deploy

- Tasks:
  - Add the deploy stage (T5)
- Waits for:
  - feat/orders-cicd
- Question: none
- Ready now: held, waits on feat/orders-cicd
