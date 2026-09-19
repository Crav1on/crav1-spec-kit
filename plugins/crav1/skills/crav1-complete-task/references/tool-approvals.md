# Tool approvals (complete-task / complete-tasks)

Cursor **Allow / Stop** on a worker (podman, `dotnet`, env secrets, Browser click/fill) is the IDE’s **Approvals & Execution** gate. It is **not** `fix` / `stop` / `ready` from the kit. This skill cannot click Allow for you.

Workers (Aspire, SQL, live HTTP, UI) almost always hit **unsandboxed** shell and **Browser**. Those keep prompting unless the IDE is set to run them without asking.

## Upfront (once per command)

**Before the first worker**, if they have not already said how to handle approvals, ask (questions tool OK). This turn is approvals only — do not launch a worker yet.

| Id | Choice | Meaning |
| --- | --- | --- |
| `auto` | I will auto-run this batch | They set the IDE so workers are not blocked on Allow. You launch workers and **ignore** Allow/Stop as a kit gate. Do not pause the board for those buttons. |
| `click` | I will click Allow myself | Current IDE prompts stay. You still launch workers; they know they must Allow. Do not re-ask `auto`/`click` per `T#`. |

If they already wrote `auto` / `run everything` / `I'll approve in settings`, skip the menu.

Remind them (short, once) how to actually auto-run locally:

1. **Settings → Agents → Approvals & Execution**
2. For a hands-off `/crav1-complete-tasks` batch: **Run Everything** (every tool runs; no sandbox; they accept that risk).
3. Or **Auto-review** plus an allowlist / `allow_instructions` for their usual commands (`podman`, `dotnet`, `git`, test runners) **and** turn **off Browser Protection** if verify uses the Cursor browser (that protection blocks Browser tools even when the run mode would auto-run).
4. Allowlist with an empty list = ask every time (the Allow/Stop spam they are seeing).

Cloud Agents do not use Run Modes (their own VM). This note is for **local** Agent + subagents.

Do **not** invent a kit `permissions.json` unless they ask. Product-specific (SQL passwords, compose) belongs in **that** repo.

After `auto` or `click`, do not ask again for the rest of this `/crav1-complete-tasks` (or this `/crav1-complete-task`) invocation.
