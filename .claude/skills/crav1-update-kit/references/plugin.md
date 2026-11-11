# Plugin and user scope

Read this only when `mode` is `plugin`. Do not run `apply`. Do not commit kit files. Do not show the branch card, because this path does not write the kit.

Say the installed version, where it was read (`plugin.json` or the `Kit version:` line), and the latest published tag. Then give the script's `advice` text:

- A team marketplace install updates by Auto Refresh or Dashboard Refresh, then update or reinstall if Cursor asks. Reload the window. A running Cloud Agent keeps the plugin it started with; start a new agent.
- A local plugin is a fresh copy of `plugins/crav1` from that release into `~/.cursor/plugins/local/crav1`, then a reload. This command does not copy it.
- User-scope Claude Code is a fresh copy of the release `.claude` tree into `~/.claude`. This command does not copy it and does not commit.

When the jump lists a migration id, read [migrations.md](migrations.md) and offer those steps. They can still change project files, and only after a yes. There is still no kit commit.
