# radar — self-improvement loop

Control plane for an autonomous improvement loop running on my Raspberry Pi:

- **07:00** — the [devlog job](https://pkia.github.io/blog/) reviews the last
  day's commits across my repos, publishes a daily post, and proposes next
  steps in its "On the radar" section.
- **09:00** — the **radar implementer** (this repo is its workdir) picks one
  radar idea and implements it for real: code, tests, docs — in an existing
  repo or a brand-new one.
- **Next morning** — the devlog reports what shipped, straight from git
  history. The loop closes.

The idea board lives in [IDEAS.md](IDEAS.md) — the single source of truth for
what is Proposed, In progress, Done, or Skipped. The implementer's protocol is
in [AGENTS.md](AGENTS.md).

Owned repos it may work across (any repo under `/home/ev` whose origin remote
points at `pkia` on GitHub):

- [maritime-dashboard](https://github.com/pkia/maritime-dashboard) — AIS ship tracker + NOAA weather-satellite kiosk
- [project-hub](https://github.com/pkia/project-hub) — home-server ops portal
- [pi-cicd](https://github.com/pkia/pi-cicd) — CI/CD architecture reference
- [ais_analysis](https://github.com/pkia/ais_analysis) — AIS data exploration
- [camoufox-setup](https://github.com/pkia/camoufox-setup) — browser automation setup
- [pkia.github.io](https://github.com/pkia/pkia.github.io) — portfolio + devlog
