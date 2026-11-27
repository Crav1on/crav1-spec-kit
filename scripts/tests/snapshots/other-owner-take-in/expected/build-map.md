# Build map

The plan has no steps, so this map uses one branch per task.

```mermaid
flowchart LR
  subgraph w1["Wave 1"]
    direction TB
    b1["feat/orders-table"]
  end
  subgraph w2["Wave 2"]
    direction TB
    b2["feat/orders-fixes"]
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
  class b2,key4 todo
  class b1,key1 done
  style w1 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style w2 fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  style legend fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1
  linkStyle default stroke:#60a5fa,stroke-width:2px
  linkStyle 0 stroke:#4ade80,stroke-width:2px
```

An arrow means the later branch waits for the earlier one.

<details>
<summary>Wave 1 done (1 task)</summary>

## Wave 1: 1 branch, 0 can start now, 1 done

### feat/orders-table

- Tasks:
  - ~~Add the orders table (T1)~~ ✓ done (feat/orders-table)
- Waited for: none
- Question: none
- Ready now: done

</details>

## Wave 2: 1 branch, 0 can start now

### feat/orders-fixes

- Tasks:
  - A test of the 404 for an unknown order (T2)
  - A test of the order id guard (T3)
  - PR 7 takes in develop, conflicts resolved, whole suite green (T4)
- Waits for:
  - feat/orders-table
- Question: none
- Ready now: in progress
