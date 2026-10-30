# Local test dependencies (preflight)

Run this before any test command in implement, verify, or fix. A test that skips because a local dependency is down is not a pass.

## Detect

Read what the tests need from the repo, not from memory:

- Test setup, fixtures, and skip conditions (for example `skipif`, `[Ignore]`, `Assume`, `test.skip`) that name a service.
- Test config and connection strings: `appsettings*.json`, `local.settings.json`, `.env*`, `pytest.ini`, `jest.config.*`, `testcontainers` usage.
- `docker-compose*.yml`, `.devcontainer/`, Aspire app hosts, and the test or setup section of `AGENTS.md` or the README.

Typical local dependencies:

| Dependency | Signal | Running check |
| --- | --- | --- |
| Azurite (Azure Storage emulator) | `UseDevelopmentStorage=true`, `127.0.0.1:10000`, `azurite` in scripts | ports 10000–10002 answer |
| Cosmos DB emulator | `localhost:8081`, emulator key | port 8081 answers |
| A database container (SQL Server, Postgres, MySQL, Redis, …) | a local connection string, a compose service | the port answers, or `docker ps` shows the service up |
| Service Bus / Event Hubs emulator, LocalStack, other emulators | a local endpoint in config | its port answers |

Check that each one is running. Do not start anything yet. List only what the repo references. Do not guess one the repo does not name.

## Ask

When one is not running, ask once per dependency. Use the questions tool when it is available:

1. **Start it.** The kit starts it with the repo's documented command (README, `AGENTS.md`, compose, a script). When none is documented, use a sensible default, for example `azurite --silent --location <system temp>` or `docker compose up -d <service>`, and name that command in the question. Then check again that it answers.
2. **Skip the tests that need it.** Run the rest. Name the skipped tests in `verify.md`.
3. **Stop.** Run no tests. Nothing is marked verified.

When the start fails, say why and ask again with skip or stop.

## Headless runs (two-pass)

A run with no window cannot stop to ask. Use the two-pass questions file from the imported-sources convention (skill `crav1-add-to-spec`, `references/sources-rare.md` → **Headless runs (two-pass)**): pass 1 writes the question to a file in the system temp folder, names it, and stops before marking anything verified. Pass 2 reads the answer.

Put the missing dependency at the **top** of the summary, before the TL;DR, as a marked blocker:

```text
BLOCKER: Azurite (Azure Storage) is not running. 5 tests need it. Not verified. Answer in <questions file>: start, skip, or stop.
```

Never as a footnote.

## Verified

- A task is **Implemented, verified** only when its evidence ran and passed with no test skipped for a missing dependency, or when the user explicitly chose **skip** for that dependency.
- Without that choice, the task is **Claimed done, unverified** and the box in `tasks.md` stays as `crav1-build-tasks` says: not ticked on this evidence.
- After a **skip**, `verify.md` → **Skipped tests** lists each skipped test, the dependency, and `skipped by user choice, <date>`.

## Missed by the preflight

When the test output still shows tests skipped for a dependency reason (for example "skipped because Azurite wasn't running", a connection refused in a skip message, an emulator not found), treat it as above: put it at the top as a blocker, ask start, skip, or stop, and do not mark verified without that choice. Name the missed dependency in `verify.md` so the next preflight checks it. Do not edit the repo's config.
