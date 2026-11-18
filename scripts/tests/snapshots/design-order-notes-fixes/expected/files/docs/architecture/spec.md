# Architecture

## Confirmed

- orders-api runs on the contoso cloud account. (`infra/main.bicep`)

## Decided, not built yet

Approved designs that are not built yet. Recheck moves a part up to Confirmed once the code or the environment shows it.

### platform first (topic orders-platform)

Designed in: `docs/architecture/designs/orders-platform/designs/platform-first/`

Not designed yet.

Small fixes (no design choice):
- Rename the test queue to orders-test

## Open questions

- Who pays for the zone (person B decides)
- Are backups needed in test (person A knows)
