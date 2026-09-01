# Radar — idea board

Single source of truth for the self-improvement loop. Ideas arrive from
the "On the radar" section of daily devlog posts, from repo evidence, and
from occasional external research; the radar implementer picks one per
run, builds it, and records the outcome here. Oldest entries at the
bottom of each section; keep Done, Skipped and the Run log as append-only
ledgers.

Proposed entries carry an effort tag — **S** (one session), **M** (a few
sessions), **L** (multi-week) — and a source. *(external)* items were
found by web research and keep their source URL.

## Proposed

- **Make the self-healer show its work** *(S; new in posts/2026-08-31.html —
  "the pick I'd make next")* — pipeline-check now fixes things silently;
  give it the chaos-drill treatment: a `status.json` recording every
  self-heal (what, when, before → after), a Self-healing panel in the
  portal (project-hub) like the Chaos Drills one, and a "healed N things
  since yesterday" line in pi-doctor's morning audit. Acceptance:
  pipeline-check appends heals with before→after detail to
  `~/.local/state/pipeline-check/status.json`, project-hub renders a
  Self-healing panel via `/api/heals`, pi-doctor reports the daily heal
  count in its audit, pytest + CI green in both repos.

Externally researched 2026-08-21 (owner-directed session; sources linked;
monitoring/infra theme). ntfy left this list 2026-08-24 (see Done) — the
rest now build on it:

- **Uptime Kuma service monitoring** → concretised 2026-08-27 as
  **service uptime scoreboard (pi-cicd native)** and shipped same day,
  see Done (Uptime Kuma itself needs containers, which this box
  forbids; the stdlib `service-probe` covers the HTTP/DNS probes, the
  ntfy alert wiring and the portal scoreboard the idea asked for).
- **changedetection.io with LLM rules** → concretised 2026-08-26 as
  **upstream release watcher (pi-cicd native)** — shipped same day, see
  Done. The changedetection.io app itself is not in Debian and
  conflicts with the no-container rule; the underlying need (watch
  upstream releases of the deployed software, digest changes to the
  notifications topic) shipped as a stdlib `release-watch` tool
  instead. Remaining from the original item, if ever wanted:
  browser-based arbitrary-page diffing with visual selector support.
  **S** <https://github.com/dgtlmoon/changedetection.io>
- **Prometheus + Grafana + node_exporter from Debian packages** —
  concretised 2026-08-31: install all three from apt with plain systemd
  units (the no-container way this box does things), point Prometheus at
  node_exporter and the long-running services, pin ONE dashboard with the
  graphs these posts actually quote — CPU temperature against load, probe
  health over time. Alerting routes through ntfy_lib. **M**
  <https://artofinfra.com/monitor-raspberry-pi-and-linux-metrics-with-grafana-prometheus-on-docker/>

## In progress

_(nothing — pick from Proposed)_

## Done

- **Make the self-healer show its work** — done 2026-09-01 (first seen in
  the 08-31 devlog radar list, its explicit "pick I'd make next"). 
  pipeline-check now records every self-heal to
  `~/.local/state/pipeline-check/status.json` — event-driven (only fires
  when a fix actually happened), bounded 50-entry ledger, each entry
  ts/what/detail with before→after in the detail (e.g. deploy caught up
  `m8 -> head`), atomic write via temp file; project-hub renders a
  **Self-healing panel** (last 8 heals, newest first) fed by the new
  `/api/heals` endpoint, hiding itself when absent exactly like the
  Chaos Drills panel; pi-doctor's audit appends "Self-healed in the last
  24h: N thing(s)". 210/210 pytest in pi-cicd (2 new — hermetic
  end-to-end: a real stranded-commit push heal driven through the REAL
  script against a local bare remote, plus a no-heal → no-ledger case),
  9/9 in project-hub; CI triggered on push (runs pending at write time).
  Repos: <https://github.com/pkia/pi-cicd> commit `48dc032`;
  <https://github.com/pkia/project-hub> commit `54012c2`.

- **Grow pi-cicd into the single architecture reference** — done
  2026-08-31 (first seen 08-21; the 08-31 post named the concrete next
  step: "the index comes next"). Completed the reference in pi-cicd:
  `docs/units.md` — the **unit index**, one row per running unit mapping
  it to schedule, config file, state and ntfy topic (12 units:
  project-guard, per-service deploy, pipeline-check, pi-doctor,
  loop-heartbeat, ntfy-notify, ntfy server, pi-backup, pi-backup-drill,
  release-watch, service-probe, chaos-drill; portal panels and the mute
  noted) — and `docs/layers.md`, one page per operational layer (deploy,
  guard, compliance, doctor, heartbeat, notifications+mute, backup,
  release-watch, service-probe, chaos drills), cross-linked from
  architecture.md and README. The index is bound to reality by
  `tests/test_units_doc.py`: expected units present with full rows,
  every unit file in `systemd/` indexed, every layer section present.
  208/208 pytest locally (3 new); **CI green (run 33357644280)**. Repo:
  <https://github.com/pkia/pi-cicd> commit `cedfd67`. The index was
  verified against the live box (systemctl timers/units, /etc configs,
  ~/.local/state, README + Done ledger) before writing.

- **Chaos drills on a timer** — done 2026-08-30 (new in the 08-30
  devlog's radar list, its explicit "pick I'd make next"). Built
  `chaos-drill` in pi-cicd: a stdlib runner with a manifest of three
  drills, one per night on date-hashed rotation (systemd timer 04:45,
  after the 03:30 backup, clear of the 04:00 implementer):
  (1) **service-probe-dead-port** — seeds a dead-port probe through a
  *shadow copy* of the live probe config (alerts re-targeted to the
  drill's `chaos` topic, its own state dir, live scoreboard and
  `services` topic untouched) and drives the REAL service-probe
  pipeline until the probe flips DOWN in its own state file, the DOWN
  digest publishes, then heals and expects the recovery flip + digest;
  (2) **ntfy-auth** — the backbone must be fail-closed: anonymous
  publish DENIED (401/403), publisher token accepted, marker receipt
  read back off the topic via the subscriber token (root-owned token
  read via `sudo -n cat`, skip-not-weaken if unavailable);
  (3) **probe-timer-alive** — timer active AND last sweep recent
  (timezone-proof: `ExecMainExitTimestampMonotonic` vs /proc/uptime).
  PASS/FAIL receipt to the new ntfy `chaos` topic through ntfy_lib
  (mute + timeouts inherited), receipts in
  `~/.local/state/chaos-drill/status.json`. Live evidence: all three
  drills **PASS on the Pi**, and the full chain was read back off the
  topic via the subscriber token — the real "service-probe: 1 service
  DOWN / chaos-dead-port back UP" digests AND both drill receipts.
  Portal (project-hub) shows the Chaos Drills panel via `/api/chaos`
  (deployed by pull-CD at commit `4a64e9e`). 203/203 pytest in
  pi-cicd (36 new), 9/9 in project-hub; **CI green (runs 33290179800,
  33290180409)**. Repos:
  <https://github.com/pkia/pi-cicd> commits `3114406`, `af19f59`;
  <https://github.com/pkia/project-hub> commit `4a64e9e`.

- **Alert-storm kill switch and notifier timeouts** — done 2026-08-29
  (picked from the 08-28/29 devlog radar lists, which called it "the
  pick I'd make tomorrow"). Built `ntfy_lib.py` in pi-cicd — the one
  shared publish layer every ntfy publisher now routes through — with
  (a) a **global mute file** (`ntfy-notify --mute REASON /
  --unmute / --mute-status`): one variable suppresses every publisher
  on the box without touching the network, counts as delivered so jobs
  keep flowing, fails open (unreadable mute ≠ silent box), and
  pi-doctor's daily audit reports a standing mute so it can't silence
  the box forever; (b) **finite timeouts sanitised centrally** (None/0/
  negative → 15 s), so a dead ntfy server delays a job by seconds,
  never hangs it. Consumers loop-heartbeat, pi-backup, release-watch,
  service-probe, ntfy-notify (and pi-doctor's check) inherit both for
  free; each kept its `ntfy_post` signature so existing patch points
  survived. Live evidence: committed drill `docs/e2e-mute-check.py`
  passes **8/8 as root** — real mute file, real publish suppressed
  (subscriber token read-back confirms nothing arrived), doctor finding
  fires, unmute restores delivery (message read back off the topic) —
  and the live service-probe sweep ran the new code green (12 up).
  En route: fixed a pre-existing same-second archive-name CI flake in
  the pi-backup roundtrip test, and hardened the mute state dir to
  ev-owned (root-run drill had created it root-owned, locking the
  owner out of their own kill switch — drill now chowns, install.sh
  pre-creates). 167/167 pytest locally; **CI green (run 33232164062,
  head 1aaa074)**. Repo: <https://github.com/pkia/pi-cicd> commits
  `e098236`, `83805bc`, `0ccefa6`, `c0fb4c2`, `b1f80ad`, `1aaa074`.

- **Service uptime scoreboard (service-probe, pi-cicd native)** — done
  2026-08-27 (concretised from the Uptime Kuma idea: Uptime Kuma needs
  containers, forbidden on this box; the 08-27 devlog asked for the
  release-watch treatment instead). Built `service-probe` in pi-cicd:
  stdlib prober every 5 min — HTTP checks for the seven local services
  (incl. cs2-tracker's JSON `healthy` gate) + three public funnel
  endpoints + ntfy self-check, and a hand-built-UDP DNS query for
  AdGuardHome (12 probes total). DOWN confirmed only after 2
  consecutive failures (anti-flap), recovery notices with downtime
  duration, alerts to the new ntfy `services` topic (ACLs provisioned:
  publisher write-only, subscriber read-only), atomic state +
  `status.json` at `~/.local/state/service-probe/`. Live evidence:
  first sweep 12/12 up; seeded dead-port drill produced the DOWN alert
  AND the recovery notice, both **read back via the subscriber token**;
  portal (project-hub) shows the new Uptime Scoreboard panel via
  `/api/probes` (deployed by pull-CD at commit `1c2b9f3`). En route,
  fixed two pre-existing hermeticity bugs that had pi-cicd CI red
  since 08-26 (live `:8092` and live-`:53` tests now hermetic/skip on
  runners). 139/139 pytest locally; **CI green (run 33036791781)**.
  Repos: <https://github.com/pkia/pi-cicd> commits `3f37190`,
  `41fb1e2`, `9671a87`; <https://github.com/pkia/project-hub> commit
  `1c2b9f3` (CI run 33036338724).
- **Upstream release watcher (pi-cicd native)** — done 2026-08-26
  (concretised from the changedetection.io idea: that app isn't in
  Debian and conflicts with the no-container rule, and its LLM-rule
  variant would need an owner-provided API key). Built `release-watch`
  in pi-cicd: stdlib watcher over the GitHub releases API (plus
  optional sha256 page watches for sources without an API),
  first-observation-is-baseline, ONE digest per sweep on a new ntfy
  `releases` topic (ACLs provisioned: publisher write-only, subscriber
  read-only), error-streak escalation for failing sources, `--list`,
  atomic state at `~/.local/state/release-watch/state.json`, systemd
  timer 10:12/22:12. Live evidence: first run baselined ntfy v2.27.0,
  AdGuardHome v0.107.79, AIS-catcher v0.70 and published the digest;
  committed drill `docs/e2e-release-watch-check.py --drill` passes 8/8
  live (anonymous denied / publisher writes / seeded change → digest →
  **read back via the subscriber token** → restore → silent sweep);
  101/101 pytest locally and CI green (run 32926074782). Repo:
  <https://github.com/pkia/pi-cicd> commits `6d5d8fc`, `25f9a58`.
- **Deduplicated backups with restore drill** — done 2026-08-25. Built
  `pi-backup` in pi-cicd: a stdlib-Python wrapper around borg 1.4
  (Debian package — no containers on this Pi) covering the /etc state
  git cannot hold (ntfy server config + user db, loop configs, units).
  Daily 03:30 create+prune timer (7 daily / 4 weekly / 6 monthly) and a
  weekly Sunday 05:30 **restore drill** that extracts a fresh archive
  and byte-compares it (sha256, sampled) against the live sources —
  PASS/FAIL published to the ntfy `backups` topic. Config at
  `/etc/pi-backup.conf` (600, root-only; passphrase + ntfy keys, never
  committed — verified no secret values in the pushed tree). Live
  evidence: first `run` archived 6 files; **live drill PASS (6/6
  byte-compared)**; both notifications read back off the `backups`
  topic via the subscriber token; 71/71 pytest green locally and CI
  green (run 32804861591). Repo:
  <https://github.com/pkia/pi-cicd> commit `559e517`. No USB storage
  attached yet — repo on SD at `/var/backups/pi-borg`, one config line
  to move it (docs/backups.md has the runbook).
- **ntfy push notifications** — done 2026-08-24. The notification
  backbone is live: ntfy 2.11 (Debian package, no third-party repo)
  on the Pi, bound to the tailscale IP only (`:6839`, NTFY on a phone
  keypad), `auth-default-access: deny-all` with a write-only
  `publisher` user (scripts) and a read-only `subscriber` user (phone),
  tokens in `/etc/loop-heartbeat.conf` and `/etc/ntfy-notify.conf`.
  Topic-per-job convention (`radar`, `loop-heartbeat`, `backups` —
  ACLs provisioned) documented in pi-cicd `docs/notifications.md` with
  a runbook. loop-heartbeat now fans alerts out to both WhatsApp and
  the `loop-heartbeat` topic (delivered if either channel accepts);
  new `ntfy-notify` helper publishes job outcomes; install.sh links it.
  50 tests pass locally and on CI (runs 32688026871, 32688874150,
  32689099970); committed live check
  `docs/e2e-ntfy-check.py` passes 7/7 (deny-all, write-only publisher,
  read-only subscriber, publish + read-back); production
  loop-heartbeat run green over both channels. Owner's one manual
  step: subscribe the phone — server
  ` token in
  `/etc/ntfy/tokens/subscriber.txt`. Repo:
  <https://github.com/pkia/pi-cicd> commits `f4b656b`, `43d2005`,
  `fcab234`.
- **Dead-man's switch on the loop itself** — done 2026-08-23. Built
  `loop-heartbeat` in pi-cicd: a poll-based systemd-timer monitor (30 min)
  that reads the hermes cron jobs' durable execution history
  (`hermes cron list`/`runs`) and alerts via `hermes send` on missed
  schedules, failure streaks, zombie "running" entries, vanished jobs,
  plus systemd service/timer staleness; deduped with recovery notices,
  silent when green. Config at `/etc/loop-heartbeat.conf` keeps the alert
  target out of the public repo. First live sweep immediately caught the
  real 2026-08-21 implementer outage (4 failed/unknown runs) and paged
  WhatsApp. Repo: <https://github.com/pkia/pi-cicd> commits `59597ba`
  + `3c006c0`; CI green (runs 32615681707, 32615767382 — 27 tests);
  timer active on the Pi
  (first run 04:33 IST, exit 0, alert delivered — state file proves the
  send). Poll-based by design because the protocol forbids editing the
  hermes cron jobs themselves.

## Skipped

- **ACARS/VDL2 decoding (acarsdec)**, **ADS-B tracking (readsb +
  tar1090)**, **OpenWebRX+ browser SDR** — the RF-extension ideas from the
  2026-08-21 research session. Skipped 2026-08-23: owner paused the
  AIS/RF track for now; all three also need a second RF front end.
  Sources: <https://github.com/TLeconte/acarsdec>
  <https://github.com/wiedehopf/tar1090> <https://www.openwebrx.de/>
- **Make sense of the AIS data pile in ais_analysis** — paused (not
  abandoned) 2026-08-23: owner is done with the AIS project for now.
  **Resume pointer if ever un-paused:** the `aisdecode` package (dsp +
  hdlc modules) and `tests/` exist in `/home/ev/ais_analysis`; the
  scratch probes are preserved on the `wip/aisdecode` branch (start with
  `_probe_chain.py`); the capture is `cap_2min.raw`. Next: fold the
  useful probes into the package, land the AWGN round-trip test, decode
  the capture, write the findings report.

## Run log

Append-only, one line per run — including failures and no-ops.

- 2026-08-21 — 3 scheduled implementer attempts failed on API errors
  (2× 90 s timeouts, then HTTP 429 usage-limit; the 07:00 devlog job
  consumed the shared 5-hour window). No idea work done; AIS idea left In
  progress with a resume pointer.
- 2026-08-21 — owner-directed session: researched external sources,
  rewrote the protocol (resume-first, checkpointing, run log, external
  idea sourcing) and seeded this board. Loop machinery untouched.
- 2026-08-21 — owner-directed follow-up: via `hermes cron edit`, the
  implementer moved 09:00 → 14:00 (out of the devlog's usage window) and
  run-to-run continuity was disabled (fresh context; board is the state);
  the devlog prompt's "09:00 implementer" reference corrected.
- 2026-08-23 — owner-directed: AIS project paused for now. The In-progress
  AIS item and the three RF-hardware ideas moved to Skipped (resume
  pointer preserved); monitoring ideas kept, descriptions generalised.
  No code work in this change. Overnight schedule (devlog 01:00, X writer
  02:30, implementer 04:00) starts tonight.
- 2026-08-23 — implementer run: synced devlog radar lists (no new ideas —
  all already on the board), picked the dead-man's switch, shipped
  `loop-heartbeat` in pi-cicd (see Done). First sweep caught the real
  2026-08-21 implementer outage and paged; CI green.
- 2026-08-24 — implementer run: devlog radar lists synced — the 08-24
  post refined the ntfy idea with concrete steps, nothing genuinely
  new otherwise; no external research needed (four Proposed items
  remained). Picked **ntfy notification backbone**, shipped it in
  pi-cicd with a live server on the Pi (see Done). 50 tests + CI green
  ×3, 7/7 live checks, production heartbeat green on both channels.
  Fixed en route: two latent wall-clock-dependent e2e tests that
  flipped at midnight.
- 2026-08-25 — implementer run: synced the 08-25 devlog radar list (it
  refined the three monitoring ideas with concrete next steps — folded
  the restore-drill requirement into the backups item; nothing
  genuinely new). Picked **deduplicated backups + restore drill**,
  shipped `pi-backup` in pi-cicd: borg wrapper, daily + drill timers,
  first live drill PASS, ntfy `backups` topic live, CI green (see
  Done). Remaining Proposed: Uptime Kuma, changedetection.io, Prom
  stack, pi-cicd architecture doc.
- 2026-08-26 — implementer run: synced the 08-26 devlog radar list
  (same three monitoring ideas, further refined; nothing new to add).
  Concretised the changedetection.io item into an **upstream release
  watcher** and shipped it as `release-watch` in pi-cicd: baselined
  ntfy/AdGuardHome/AIS-catcher, live seeded-change drill 8/8, `releases`
  `releases` ntfy topic live, 101/101 tests + CI green (see Done).
  Remaining Proposed: Uptime Kuma, Prom stack, pi-cicd architecture doc.
- 2026-08-27 — implementer run: synced the 08-27 devlog radar list (it
  concretised Uptime Kuma into a stdlib prober — adopted as the pick).
  Shipped **service uptime scoreboard** as `service-probe` in pi-cicd:
  12 live probes green, dead-port drill round-tripped through the ntfy
  `services` topic, portal scoreboard panel live via pull-CD, 139/139
  tests + CI green after fixing two pre-existing red-CI test bugs (see
  Done). Remaining Proposed: Prom stack, pi-cicd architecture doc.
- 2026-08-29 — implementer run: synced the 08-28 + 08-29 devlog radar
  lists — the 08-28 post introduced the **alert-storm kill switch +
  notifier timeouts** idea (adopted as the pick; the 08-29 post called
  it "the pick I'd make tomorrow"); Prom stack and architecture doc
  carried over, nothing else new. Shipped `ntfy_lib.py` in pi-cicd
  (global mute + centrally-sanitised timeouts) inherited by all five
  publishers; live drill 8/8, 167/167 tests, CI green (see Done).
  En-route fixes: pre-existing pi-backup CI flake (same-second archive
  names), mute state dir ownership (root-run tools must not create it
  root-owned). Remaining Proposed: Prom stack, pi-cicd architecture
  doc.
- 2026-08-30 — implementer run: synced the 08-30 devlog radar list (one
  new idea — chaos drills; Prom stack and architecture doc carried
  over). Picked **chaos drills on a timer** and shipped `chaos-drill`
  in pi-cicd: 3-drill manifest, nightly date-hashed rotation, shadow
  dead-port drill through the real service-probe pipeline, ntfy
  fail-closed drill with read-back, probe-timer liveness; all three
  PASS live with the chain read back off the `chaos` topic; portal
  Chaos Drills panel live via pull-CD; 203/203 + 9/9 tests, CI green
  (see Done). Remaining Proposed: Prom stack, architecture doc.
- 2026-08-31 — implementer run: synced the 08-31 devlog radar list (one
  new idea — **make the self-healer show its work**, the post's explicit
  "pick I'd make next", added to Proposed with acceptance criteria; Prom
  stack carried over and concretised as Debian packages). Picked the
  **pi-cicd architecture reference** (carried over; 08-31 named the
  index as the next step — smaller and zero-risk vs. touching the live
  self-healer): shipped `docs/units.md` (unit index — 12 units →
  schedule/config/state/topic), `docs/layers.md` (one page per layer),
  links from architecture.md + README, and `tests/test_units_doc.py`
  binding the index to `systemd/`. Stale chaos-drill entry cleaned out
  of Proposed (already Done). 208/208 pytest; **CI green (run
  33357644280)**. Remaining Proposed: self-healer visibility, Prom
  stack.
- 2026-09-01 — implementer run: picked **make the self-healer show its
  work** (already on the board from the 08-31 devlog, its explicit "pick
  I'd make next"; devlog re-sync skipped this run — pick was settled).
  Shipped the heal ledger in pipeline-check, the Self-healing portal
  panel via /api/heals, and pi-doctor's 24h heal-count line; 210/210 +
  9/9 tests green, both repos pushed (see Done). En route: test
  fixture's bare remote tripped a pre-existing slug-extraction `p` flag
  (local path got printed as a slug → spurious "no CI workflow" alert)
  — renamed the fixture remote so it can't match. Remaining Proposed:
  Prom stack (M).

## Notes

- **AIS/RF track paused by owner 2026-08-23** — do not re-add AIS ideas
  (including from older devlog posts' "On the radar" lists) unless the
  owner lifts the pause. ais-catcher itself keeps running as the X bot's
  data source; treat it as maintenance-only, not a development target.
- "Keep this devlog honest and boring: tests green, deploys dull,
  rollback never needed" — standing quality bar for everything above, not
  a build task. *(2026-08-21)*
