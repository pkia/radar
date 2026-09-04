# radar — lessons

Append-only memory for the implementer loop, newest at the top. Read at
run start; prune entries that no longer apply (keep it lean — a bloated
lessons file gets ignored).

- Docs that claim to map the running system rot within days — bind them
  to a test. units.md/layers.md carry `tests/test_units_doc.py` (expected
  units present with full rows, every unit in systemd/ indexed, every
  layer section present) so the index can't silently drift from the repo.
  Also: a markdown-table parser must not skip the header row — the
  separator `|---|` line is what follows it, not precedes it. *(2026-08-31)*
- Chaos-drill patterns that cost a test cycle: (1) service-probe's
  stdout carries only alert COUNTS — the digest text goes to the ntfy
  payload — so verify detection via the state-file flip
  (`probes["http:name"].status`), not stdout grepping; (2) its
  PROBE_HTTP entries REQUIRE the `http://` scheme (RE_HTTP gate) —
  `Name=127.0.0.1:port/` is silently skipped; (3) repeated config keys
  accumulate, and LAST occurrence wins — so appending both
  `PROBE_HTTP=drill=...` and `NTFY_TOPIC=chaos` lines to a copy of the
  live config is the safe way to run shadow drills without touching
  production state or topics. *(2026-08-30)*
- Config files created via `sudo bash -c "cat > /etc/x.conf"` end up
  root-owned 600 — but the systemd unit runs the tool as `ev`, so the
  tool silently sees "no probes configured". After provisioning:
  `sudo chown ev:ev /etc/x.conf`. And ntfy's `<topic>/json?poll=1`
  returns one JSON object per line (JSONL stream), not an array —
  `json.load()` chokes; parse line by line. *(2026-08-27)*
- Root-run tools that mkdir a state dir make it root-owned, locking
  `ev` out of it (bit the ntfy mute kill switch: root-run e2e drill
  created `~ev/.local/state/ntfy` root-owned; ev's `--mute` then
  died). Rule: shared state dirs under ~ev must be created by ev
  (install.sh pre-creates; root drills chown back). Related: a kill
  switch must FAIL OPEN (unreadable state = alerts flow) and a standing
  mute needs its own watchdog finding, or it silences the box forever.
  *(2026-08-29)*
- ntfy 2.11 CLI shape: `ntfy access <user> <topic> <perm>` — no `add`
  verb, no `--config` on `user list` (defaults to server.yml), and
  permissions are `read-only`/`write-only`/`read-write`. Also: ntfy's
  JSON subscribe stream is `<topic>/json?poll=1` — bare `/<topic>` is
  the web app (returns 200 for anonymous, so a wrong ACL test passes
  for the wrong reason). *(2026-08-26)*
- e2e drills that run a user-stateful tool as root: `~` resolves to
  `/root`, silently writing a parallel state file instead of diffing
  the seeded one — always `sudo -u ev <tool> --state <abs path>` and
  chown the restored file back. And match assertion strings to the
  actual output mode: release-watch's `-v` prints ASCII `->` while the
  digest uses `→`. *(2026-08-26)*
- borg 1.4 quirks that cost a test cycle: `borg info --json` nests
  per-archive stats under `archives[0]` (not `archive`); archives of
  absolute paths are stored WITHOUT the leading `/`, so restores land
  under `dest/tmp/.../src/...` — map restored rel paths back to
  `/`+rel when byte-comparing against sources. Also: borg on GitHub CI
  is just `apt-get install borgbackup`. *(2026-08-25)*
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

- 2026-09-04 — systemd-only repo evidence is incomplete: hermes cron is a first-class scheduler on this box (docs/units.md in pi-cicd documents which units run where). Check `hermes cron list` AND the unit index before declaring a tool "never deployed" — the 09-03 run burned a session on a systemd-only misdiagnosis.
