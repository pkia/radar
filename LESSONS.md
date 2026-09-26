# radar — lessons

Append-only memory for the implementer loop, newest at the top. Read at
run start; prune entries that no longer apply (keep it lean — a bloated
lessons file gets ignored).

- 2026-09-26 — **a system unit resolves `%h` from the manager, not from `User=`.** A unit
  with `User=ev` and `WorkingDirectory=%h/cs2-train` expands `%h` to `/root`, so the service
  died at CHDIR (`status=200/CHDIR`) and then at spawn (`Errno 13`) — the journal naming
  `/root/cs2-train` is what gave it away. In a system unit spell absolute paths (`%h` is fine
  in a user unit). Found by the unit's own first live run, not by review, which is the point:
  install the timer and start it once, or nobody learns it is broken until the week it matters.

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

- 2026-09-08 — Empty subprocess stdout on a CI runner usually means the target file is not there, not that it crashed: python's "can't open file" goes to stderr while stdout stays empty. Read stderr into the failure message and check the path exists before theorising about import-time crashes (the 09-07 "engine crash under HOME" theory was wrong — ~/.hermes/cloud/hetzner_cloud.py simply does not exist on GitHub runners). Corollary: tests must never read machine-private state (~/.hermes) — drive it from tmp_path, skipif the artifact is dev-box-only, and assert the stdout JSON contract, not the exit code (the no-token CLI legitimately exits 1 with error JSON on stdout).

- 2026-09-10 — a root-created config file is a silent failure mode. The first /etc/metric-alert.conf was written by root with umask 077 (mode 600, root-owned); the timer runs as ev, so load_config read nothing, reported "no rules configured" and exited 1 — the tool was right and the box looked broken. Any tool whose config is written by an installer must be created ev-owned, and any parser must check readability and say so loudly. Same class as the 2026-08-29 mute-dir ownership bug: root writes, ev reads.

- 2026-09-20 — **Recount the test total; never carry a memory of it.** The T-075 record claimed `19 passed (6 new + 13 existing)` from the earlier two-failure output's `13 passed` line, but that 13 already *included* four of the new tests — the real split was 6 new + **9** existing = 15. The number was written into two ledgers (a commit message and docs/WORKLOG.md) before anyone re-ran with `-q` on a clean tree. `pytest --collect-only -q | tail -1` (or one green run) is the only source for a count; a count copied from a *failing* run is a count of a tree that no longer exists.

- 2026-09-21 — **A lint invocation is not the repo's lint gate.** Committing T-075 aborted because I ran `venv/bin/ruff check <changed files>`: with explicit paths ruff applied a far broader rule set than the repo's gate (119 findings, nearly all pre-existing style in `api/control.py`) and the `&&` chain stopped *before* the commit — a working tree with green tests and no commit, the exact state the checkpoint rule exists to prevent. In cs2-train the gate is the narrow selection CI runs (E9/F63/F7/F82 class) and `scripts/release_check.sh` is its owner. Read the gate's own command out of the repo before linting a change, and when ruff is "red", check whether the *changed* lines are the cause before believing the run.

- 2026-09-21 — **A CSP nonce beats moving files when the files are what the locks reach into.** The clean-sounding fix for `'unsafe-inline'` (externalise the shells' inline JS) would have blinded six revert harnesses, the `esc()` locks and the token-marker locks in cs2-train — they all target the inline block inside `dashboard/*.html`. Minting a per-response nonce (`secrets`, never reused) retired the directive with every lock intact. Related: a nonce in `style-src` makes `'unsafe-inline'` inert per CSP3, so inline `style="…"` attributes and nonced styles cannot coexist — with 256 attributes in the tree, `style-src` had to keep the carve-out, and the residual got filed with per-file counts instead of adjectives.

- 2026-09-22 — **A claim you cannot measure gets a pin, not a hope.** cs2-train reported the 55 upstream practice profiles as unmeasured because their tree lives off-box, so upstream deleting one would have looked exactly like a healthy corpus. Pinning the *listing* (upstream commit sha + per-file blob shas + a sha256 over the whole thing) turned an unverifiable claim into a re-derivable one, and pinning a **commit**, never a branch, is what stops the pin itself moving. Shape the gate offline (`--check` reads only the pin) and make the network re-measure opt-in (`--fetch`) with a replay mode (`--listing FILE`) — then CI can never flake on a third party API while the tests still drive the real CLI. *(2026-09-22)*

## 2026-09-23 — a shared file's diff is not all yours

`api/control.py` in cs2-train is worked by two agents, and this run needed to
commit one hunk of it (the CSP change) while another agent's uncommitted T-040
hunk sat in the same file — an untracked module plus its import. Reverting the
file, re-applying my edits, committing and copying their work back would have
worked but touched their WIP; the technique that did not is **staging a
filtered patch**:

```
git diff <file> > /tmp/all.patch          # every hunk, mine and theirs
python /tmp/stage_mine.py /tmp/all.patch /tmp/mine.patch <their-marker>
git apply --cached /tmp/mine.patch        # index only — the working tree is untouched
git add <my other files> && git commit
```

The marker is any string in their *added* lines (here `auth_backstop`); hunks
without it are staged, hunks with it are dropped. The working tree keeps their
WIP, the commit never carries it, and `git status` afterwards shows their hunk
as the only unstaged change — which is the correct handoff state.

**Corollary, learned the hard way in the same run:** to prove a commit green
when someone else's uncommitted code breaks a test, set that code aside briefly
(`git stash push -u <paths>`), run the suite, then `git stash pop` it back. The
first `pop` can fail on a stale `.git/index.lock` while the other agent's git
process is still running — retry in a loop before assuming the lock is garbage.

## 2026-09-23 — generated class names break tests that pin literal markup

T-075's style tokenisation renames every converted tag's styling into
sha-derived classes (`.u-1a2b3c4d`), so a test that anchored on a literal
`style="…"` slice of a shell either broke or silently matched the wrong
element. The fix is not to pin the hash: read the anchor out of the file at
test time (`src.rindex(row_open, 0, src.index(unique_cell))`), so the test
still means "this row" after the next conversion. A scan/gate that pins a
*count* (`--check` reads zero) is stable; a pin on generated *spelling* is not.

- **2026-09-24 — a pin with one reader is still prose.** The upstream pin shipped
  gated on 09-22 while the *report* every other check reads kept calling the same
  55-profile claim `unmeasured`: one file measured it, another shrugged at it.
  When a measurement lands, find every reader of that claim and route them through
  the measurement in the same change — a gate that exists beside a shrug is a gate
  nobody depends on. Corollary from T-077: import the writer's own helpers
  (`validate_pin`, `count`, `listing_sha`) instead of re-implementing its rules, or
  the reader quietly defines "valid pin" differently from the writer.
