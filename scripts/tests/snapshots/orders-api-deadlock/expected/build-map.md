# Build map

The plan has no steps, so this map uses one branch per task.

```mermaid
flowchart LR
  subgraph w2["Wave 2"]
    direction TB
    b1["feat/orders-cicd"]
  end
  subgraph blocked["Blocked"]
    direction TB
    b2["feat/orders-store"]
  end
  subgraph legend["Legend"]
    direction TB
    key1["Done"]
    key2["Waits on a PR or question"]
    key3["Blocked"]
    key4["Ready or not started"]
  end
  b2 ==> b1
  classDef blocked fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fef2f2
  classDef waiting fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fffbeb
  classDef todo fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#eff6ff
  classDef done fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#f0fdf4
  class b2,key3 blocked
  class key2 waiting
  class b1,key4 todo
  class key1 done
  style w2 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style blocked fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style legend fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  linkStyle default stroke:#60a5fa,stroke-width:2px
  linkStyle 0 stroke:#f87171,stroke-width:4px
```

An arrow means the later branch waits for the earlier one.

## Wave 2: 1 branch, 0 can start now

### feat/orders-cicd

- Tasks:
  - Add the build pipeline (T3)
- Waits for:
  - feat/orders-store
- Question: none
- Ready now: waits in order

## Blocked

### feat/orders-store

- Tasks:
  - Store a retried order once (T1)
  - Take in develop, resolve conflicts and merge PR 11 (T2)
- Waits for: none
- Question: none
- Ready now: blocked, merge deadlock: T2 waits on T1, which ticks only when PR 11 merges
