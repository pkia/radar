# Radar — idea board

Single source of truth for the self-improvement loop. Ideas arrive from the
"On the radar" section of daily devlog posts; the radar implementer picks one
per run, builds it, and records the outcome here. Oldest entries at the bottom
of each section; keep Done and Skipped as an append-only ledger.

## Proposed

- **Grow pi-cicd into the single architecture reference** for how everything
  on this Pi builds, tests, deploys and rolls back.
  *(first seen 2026-08-21, posts/2026-08-21.html)*

## In progress

- **Make sense of the AIS data pile in ais_analysis** — first proper look at
  what the station has been collecting.
  *(first seen 2026-08-21, posts/2026-08-21.html; started 2026-08-21)*
  Concrete scope for this run: turn the scratch IQ scripts into a real,
  tested CU8→AIS-decode toolchain (burst detect → GMSK demod → HDLC/CRC →
  MMSI/message type) with synthetic round-trip pytest tests, run it on the
  2-min 162 MHz capture, and commit an honest findings report.

## Done

_(nothing yet — first implementer run has not happened)_

## Skipped

_(nothing yet)_

## Notes

- "Keep this devlog honest and boring: tests green, deploys dull, rollback
  never needed" — standing quality bar for everything above, not a build task.
  *(2026-08-21)*
