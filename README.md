# radar — self-improvement loop

Control plane for an autonomous improvement loop running on my Raspberry
Pi:

- **07:00** — the [devlog job](https://pkia.github.io/blog/) reviews the
  last day's commits across my repos, publishes a daily post, and proposes
  next steps in its "On the radar" section.
- **14:00** — the **radar implementer** (this repo is its workdir) picks
  one radar idea and implements it for real: code, tests, docs — in an
  existing repo or a brand-new one. If an idea is already In progress it
  resumes that first; it checkpoints with local commits as it goes, so a
  run that dies mid-way (rate limit, timeout) loses nothing and the next
  run picks up from the board.
- **Next morning** — the devlog reports what shipped, straight from git
  history. The loop closes.

The idea board lives in [IDEAS.md](IDEAS.md) — the single source of truth
for what is Proposed, In progress, Done, or Skipped, plus an append-only
Run log (failures and no-ops included) so the loop's health is visible on
the board itself. Ideas come from the devlog, from repo evidence (failing
tests, TODOs, CI flakes), and from periodic external research tagged
*(external)*. [LESSONS.md](LESSONS.md) is the implementer's carry-over
memory. The implementer's protocol is in [AGENTS.md](AGENTS.md).

In-scope repos — the **current Pi 5 deployment only** (owner directive
2026-11-02; pkia-owned and checked out on this box):

- [cluster-prototype](https://github.com/pkia/cluster-prototype) — Pi 5 + Switch distributed-computing coordinator
- [switch-l4t-gpu](https://github.com/pkia/switch-l4t-gpu) — NVIDIA GPU workload harness for the Switch worker
- [pi-cicd](https://github.com/pkia/pi-cicd) — CI/CD architecture reference
- [pkia.github.io](https://github.com/pkia/pkia.github.io) — portfolio + devlog
- [radar](https://github.com/pkia/radar) — this loop

Plus any new repo the loop itself creates on this box. Projects from
the **old Pi deployment** — twitter-launch, forex-copybot,
maritime-dashboard, project-hub, ais_analysis, camoufox-setup — and
**Train / cs2-train** (train VM/cloud) are out of scope: the radar does
not sync, pick, or implement ideas for them (see AGENTS.md "Deployment
scope" and the IDEAS.md Notes).

## Known constraints

- **Shared API quota.** The devlog and implementer jobs draw from the
  same provider quota; on 2026-08-21 the 07:00 devlog (plus retries)
  exhausted the 5-hour usage window and all three same-day implementer
  attempts failed with HTTP 429. Fixed structurally the same day, by the
  owner's direction, via `hermes cron edit`: the implementer now runs at
  **14:00** — clear of any usage window containing the morning devlog —
  and run-to-run continuity was disabled so each run starts with a fresh
  context (the board is the state). The protocol additionally treats
  budget errors as normal: checkpoint, stop, resume next run.
