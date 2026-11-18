# Architecture

## Confirmed

- orders-api runs on the contoso cloud account. (`infra/main.bicep`)

## Decided, not built yet

### target first (topic orders-target)

Designed in: `docs/architecture/designs/orders-target/designs/target-first/`
Builds on: topic orders-platform

Not designed yet.

Approved designs that are not built yet. Recheck moves a part up to Confirmed once the code or the environment shows it.

### platform first (topic orders-platform)

Designed in: `docs/architecture/designs/orders-platform/designs/platform-first/`
Accepted ADRs: `docs/system/adr/0001-how-test-gets-data.md`, `docs/system/adr/0002-where-orders-live.md`, `docs/system/adr/0003-who-releases-orders.md`

Not designed yet.

## Open questions

- Who runs billing on call (person B knows)
