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

Externally researched 2026-08-21 (owner-directed session; sources linked.
Monitoring/infra theme — the RF ideas from this session were moved to
Skipped when the owner paused the AIS project on 2026-08-23):

- **ntfy push notifications** — small self-hosted pub/sub server as the
  notification backbone: radar shipped/blocked pings, backup results. **S**
  <https://docs.ntfy.sh/install/>
- **Uptime Kuma service monitoring** — watch AdGuardHome, kiosk, portal
  and the other long-running services. **S**
  <https://github.com/louislam/uptime-kuma>
- **changedetection.io with LLM rules** — watch upstream releases of
  deployed software and status pages, digest changes via ntfy. **S**
  <https://github.com/dgtlmoon/changedetection.io>
- **Restic/borgmatic backups with healthchecks.io hooks** — deduplicated
  backups of portal, dashboards and configs; the heartbeat doubles as a
  backup-dead alert. **S**
  <https://torsion.org/borgmatic/reference/configuration/monitoring/healthchecks/>
- **Prometheus + Grafana + node_exporter** — real graphs for the devlog:
  CPU temp vs load, USB throughput, service health. **M**
  <https://artofinfra.com/monitor-raspberry-pi-and-linux-metrics-with-grafana-prometheus-on-docker/>

## In progress

- **Dead-man's switch on the loop itself** — *(external;
  <https://healthchecks.io/docs/>; picked 2026-08-23)*. On 2026-08-21 the
  implementer failed 3× silently; the loop needs silence to become a page.
  **Buildable version picked:** `loop-heartbeat` monitor in pi-cicd — a
  systemd-timer script that resolves the scheduled jobs (devlog,
  implementer, X writer, watchdog) via `hermes cron list`, inspects each
  one's real execution history via `hermes cron runs` for missed
  schedules and failure streaks, checks services and deploy timers, and
  alerts through `hermes send` with alert-state dedupe (state file under
  /var/lib or ~/.local/state). **Acceptance criterion:** watchdog-style
  script + unit/timer installed and active, pytest suite green in CI with
  fixtures generated from real `hermes cron` output, README documents the
  wiring, alerts deduped, and a live check within one timer period shows
  it evaluates all jobs and stays silent when all is green. Poll-based by
  design: the guardrail forbids editing the hermes cron jobs themselves,
  so nothing pings on the job's success path — the monitor polls durable
  state instead (works for jobs that die mid-run, not just ones that
  never fire).

## Done

_(nothing yet — first implementer run has not happened)_

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

## Notes

- **AIS/RF track paused by owner 2026-08-23** — do not re-add AIS ideas
  (including from older devlog posts' "On the radar" lists) unless the
  owner lifts the pause. ais-catcher itself keeps running as the X bot's
  data source; treat it as maintenance-only, not a development target.
- "Keep this devlog honest and boring: tests green, deploys dull,
  rollback never needed" — standing quality bar for everything above, not
  a build task. *(2026-08-21)*
