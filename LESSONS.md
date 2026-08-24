# radar — lessons

Append-only memory for the implementer loop, newest at the top. Read at
run start; prune entries that no longer apply (keep it lean — a bloated
lessons file gets ignored).

- ntfy 2.11 (Debian): `listen-http` accepts exactly ONE address string
  (comma list and YAML list both fatal) — bind the tailnet IP, not
  0.0.0.0. `ntfy user/access/token` commands need no `--config` (they
  default to /etc/ntfy/server.yml) but must run as root. And `sudo -u ev
  <tool>` loses ~/.local/bin from PATH — scripts invoking user tools must
  use absolute paths. *(2026-08-24)*
- `getattr(obj, "attr", default)` evaluates the default EAGERLY — as a
  response-code fallback it crashed on objects without the method.
  Also: any test that lets `main()` use the wall clock rots at the next
  schedule boundary — always inject `now=`. *(2026-08-24)*
- `hermes cron list` / `hermes cron runs <id>` expose the loop's durable
  state (statuses incl. failed/unknown/zombie-running) — monitoring
  should POLL that instead of instrumenting jobs (which the guardrail
  forbids anyway). Note: `hermes send` to the SAME target a cron job
  delivers to is skipped by the harness ("will already auto-deliver");
  loop-heartbeat runs via systemd, so its alerts go through fine.
  *(2026-08-23)*
- Test fixtures captured from CLI output must be wall-clock-naive (strip
  `+01:00` offsets) or tests flip outcome between the Pi (IST) and CI
  (UTC). *(2026-08-23)*
- 429/usage-limit hits are coordination, not bad luck: devlog and
  implementer share one provider quota (schedules now staggered 01:00 /
  04:00, overnight). Checkpoint early, stop, resume next run — never
  retry-spin. *(2026-08-21)*
- The board is the state, not the context. Untracked scratch files are
  invisible to the next run — commit WIP on a `wip/` branch instead.
  *(2026-08-21)*
- "Done" needs environment evidence: a green CI run or passing test
  output. Agents confidently report finishing work the environment
  contradicts; only evidence prevents that here. *(2026-08-21)*
- The single RTL-SDR dongle belongs to ais-catcher — new RF ideas need a
  second dongle or SDR sharing before any of them can run. *(2026-08-21)*
