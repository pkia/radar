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

- **Grow pi-cicd into the single architecture reference** for how
  everything on this Pi builds, tests, deploys and rolls back.
  *(M; first seen 2026-08-21, posts/2026-08-21.html)*

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
- **Prometheus + Grafana + node_exporter** — real graphs for the devlog:
  CPU temp vs load, USB throughput, service health. **M**
  <https://artofinfra.com/monitor-raspberry-pi-and-linux-metrics-with-grafana-prometheus-on-docker/>

## In progress

_(nothing — pick from Proposed)_

## Done

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

## Notes

- **AIS/RF track paused by owner 2026-08-23** — do not re-add AIS ideas
  (including from older devlog posts' "On the radar" lists) unless the
  owner lifts the pause. ais-catcher itself keeps running as the X bot's
  data source; treat it as maintenance-only, not a development target.
- "Keep this devlog honest and boring: tests green, deploys dull,
  rollback never needed" — standing quality bar for everything above, not
  a build task. *(2026-08-21)*
