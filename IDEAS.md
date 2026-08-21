# Radar — idea board

Single source of truth for the self-improvement loop. Ideas arrive from
the "On the radar" section of daily devlog posts, from repo evidence, and
from occasional external research; the radar implementer picks one per
run, builds it, and records the outcome here. Oldest entries at the bottom
of each section; keep Done, Skipped and the Run log as append-only
ledgers.

Proposed entries carry an effort tag — **S** (one session), **M** (a few
sessions), **L** (multi-week) — and a source. *(external)* items were
found by web research and keep their source URL.

## Proposed

- **Grow pi-cicd into the single architecture reference** for how
  everything on this Pi builds, tests, deploys and rolls back.
  *(M; first seen 2026-08-21, posts/2026-08-21.html)*

Externally researched 2026-08-21 (owner-directed session; sources linked.
RF ideas note: the single RTL-SDR dongle is occupied by ais-catcher, so
anything receiving RF needs a second dongle (~USD 30) or an SDR-sharing
scheme like rtl_tcp/SpyServer):

- **Dead-man's switch on the loop itself (healthchecks.io)** — every
  scheduled job (devlog, implementer, watchdog) pings healthchecks.io on
  completion; silence pages the owner. On 2026-08-21 the implementer
  failed 3× silently — this would have caught it. **S**
  <https://healthchecks.io/docs/>
- **ntfy push notifications** — small self-hosted pub/sub server as the
  notification backbone: radar shipped/blocked pings, AIS anomalies,
  backup results. **S** <https://docs.ntfy.sh/install/>
- **Uptime Kuma service monitoring** — watch ais-catcher, AdGuardHome,
  kiosk, maritime-dashboard, portal; pairs with project-hub. **S**
  <https://github.com/louislam/uptime-kuma>
- **changedetection.io with LLM rules** — watch AIS-catcher releases,
  satellite status pages and marine notices, digest changes via ntfy.
  **S** <https://github.com/dgtlmoon/changedetection.io>
- **ACARS/VDL2 decoding (acarsdec)** — plain-text airline operational
  messages on VHF; decoded text is ideal input for an LLM "today's air
  traffic" digest next to the ship log. **S** + second RF front end
  <https://github.com/TLeconte/acarsdec>
- **ADS-B aircraft tracking (readsb + tar1090)** — the air-traffic sibling
  of the AIS map, on the same dashboard. **M** + second dongle
  <https://github.com/wiedehopf/tar1090>
- **Automated NOAA/Meteor imagery (SatDump or raspberry-noaa-v2)** —
  extend the existing NOAA audio tap and METEOR demod work into fully
  unattended pass scheduling, image enhancement and a web gallery. **M**
  <https://github.com/jekhokie/raspberry-noaa-v2>
- **OpenWebRX+ browser SDR** — KiwiSDR-style web receiver to expose spare
  SDR bandwidth remotely (works over Tailscale). **S–M** + RF front end
  <https://www.openwebrx.de/>
- **Restic/borgmatic backups with healthchecks.io hooks** — deduplicated
  backups of portal, dashboards and SDR configs; the heartbeat doubles as
  a backup-dead alert. **S**
  <https://torsion.org/borgmatic/reference/configuration/monitoring/healthchecks/>
- **Prometheus + Grafana + node_exporter** — real graphs for the devlog:
  CPU temp vs satellite-pass load, SDR USB throughput, service health.
  **M**
  <https://artofinfra.com/monitor-raspberry-pi-and-linux-metrics-with-grafana-prometheus-on-docker/>

## In progress

- **Make sense of the AIS data pile in ais_analysis** — first proper look
  at what the station has been collecting.
  *(first seen 2026-08-21, posts/2026-08-21.html; started 2026-08-21)*
  Concrete scope for this run: turn the scratch IQ scripts into a real,
  tested CU8→AIS-decode toolchain (burst detect → GMSK demod → HDLC/CRC →
  MMSI/message type) with synthetic round-trip pytest tests, run it on the
  2-min 162 MHz capture, and commit an honest findings report.
  **Resume pointer (2026-08-21, after 3 API-failed runs):** the
  `aisdecode` package (dsp + hdlc modules) and `tests/` exist in
  `/home/ev/ais_analysis`; ~15 untracked `_probe_*.py` scratch scripts and
  `_refdecode.py` debug the AWGN round-trip alignment (start with
  `_probe_chain.py`); the capture is `cap_2min.raw`. Next step: fold the
  useful probes into the package, land the round-trip test, decode the
  capture. First run after this note: finish this before picking anything
  new.

## Done

_(nothing yet — first implementer run has not happened)_

## Skipped

_(nothing yet)_

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

## Notes

- "Keep this devlog honest and boring: tests green, deploys dull,
  rollback never needed" — standing quality bar for everything above, not
  a build task. *(2026-08-21)*
