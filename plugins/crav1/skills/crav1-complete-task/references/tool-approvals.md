# Tool approvals (complete-task / complete-tasks)

Cursor **Allow / Stop** on a worker (podman, `dotnet`, env secrets, Browser) is the IDE’s **Approvals & Execution** gate. It is **not** kit `fix` / `stop` / `ready`. This skill cannot change Settings or click Allow.

## Who pauses

| Who is running | Pause with directions? |
| --- | --- |
| `/crav1-complete-tasks` (orchestrator) | **Yes**, once, before the first worker |
| `/crav1-complete-features` (orchestrator) | **Yes**, once, before the first worker (same as complete-tasks) |
| `/crav1-complete-task` **standalone** (user typed that command) | **Yes**, once, before launching the worker |
| `crav1-complete-task` **worker** (subagent) | **Never** |
| Worker launched by complete-tasks or complete-features | **Never** — parent already paused. Pass `approvals: already-done` |

If the parent said `approvals: already-done`, skip this file’s wait entirely.

Cloud Agents: skip (no Run Modes). Say so and continue.

## Pause (directions, then wait)

Do **not** launch a worker on this turn.

1. Ask them to **write down** the current values (they look in Settings; you cannot read them):
   - Approvals & Execution mode: Auto-review / Allowlist / Run Everything
   - Browser Protection: on / off
2. Show the two paths below (which to choose, how to set).
3. Wait. Questions tool OK. Do not start implement.

| Id | They do | Then you do |
| --- | --- | --- |
| `continue` | They changed Settings as they chose | Launch workers. Remember their **before** values for the undo at the end. Do not treat IDE Allow/Stop as a kit gate. |
| `click` | They leave Settings as-is | Launch workers; they will click Allow. Still remember **before** (same as current) so undo is “nothing to reset.” |
| `stop` | Abort | No worker. |

If they already named `continue` / `click` / `stop` and (for `continue`) said they changed Settings, skip waiting.

Remember for the **end of this command only**: `approvals-before-mode`, `approvals-before-browser`, and whether they picked `continue` or `click`.

## Which path to choose

**Path 1 — Run Everything**  
Use for an unattended batch (several `T#`s, Aspire/podman/SQL, Cursor browser verify) when you accept that this chat can run those tools with **no** Allow prompt and **no** sandbox.

**Path 2 — Auto-review + allowlist + Browser Protection off**  
Use when you want fewer prompts but not “run anything.” Safer default if the batch is smaller or the repo is less trusted. Podman, Docker, env secrets, and Browser often **still** ask unless you allowlist those commands **and** turn Browser Protection **off**.

Empty Allowlist = ask almost every time (the Allow/Stop spam).

## How to set (local desktop)

**Settings → Agents → Approvals & Execution** (sometimes labeled Run Mode).

**Path 1**

1. Set the mode to **Run Everything**.
2. If verify uses the Cursor browser: **Browser Protection** → **off** (same security / protections area; it can still prompt on Browser even when the mode would auto-run).
3. New Agent chat or reload the window if an old chat still prompts.
4. Reply `continue`. Include the **before** mode and Browser on/off if you have not yet.

**Path 2**

1. Set the mode to **Auto-review** (or Allowlist **with** entries — not empty).
2. Allowlist or Auto-review `allow_instructions` for commands this repo actually runs (`podman`, `dotnet`, `git`, test runner).
3. Browser Protection → **off** if workers click/fill the Cursor browser.
4. New chat or reload if needed.
5. Reply `continue` and the **before** values.

Do not create a kit `permissions.json` unless they ask. Product-specific commands stay in that repo.

## Undo when this flow is over

After the standalone worker finishes (any STATUS) or the **complete-tasks batch ends** (done, blocked, or they `stop`):

If they picked `click` or never changed Settings: say **no reset needed**.

If they picked `continue`:

1. **Settings → Agents → Approvals & Execution**
2. Set the mode back to **`approvals-before-mode`** (what they wrote at the pause). If they never wrote it: “put back the mode you use day to day (usually Auto-review).”
3. Set Browser Protection back to **`approvals-before-browser`**.
4. Reload or new chat if the old mode sticks.

Do **not** leave them on Run Everything without this reminder. You cannot flip Settings for them.

Undo is **once at the end** of the command that paused. Do not undo after every `T#` inside complete-tasks.
