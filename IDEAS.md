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

- **pi-cicd: one retired list, three readers** *(S; new in
  posts/2026-09-17.html)* — pi-doctor, service-probe and the unit index
  each learned about this month's retirements separately, which is three
  places to forget. Next step: a single `retired-units` config file that
  all three read, with a test that fails when a unit appears in the live
  set and the retired list at once. Acceptance: retiring one unit means
  editing one file, and a unit named in both lists reddens CI.

- **Train: measure the upstream half** *(S; new in posts/2026-09-17.html;
  repo private)* — the corpus mapper cannot re-measure the 55 upstream
  OpenPrefirePrac practice profiles on this box, so it reports them
  `unmeasured`; a profile vanishing upstream stays invisible. Next step:
  cache the upstream profile listing (or pin the release by hash) and let
  the report diff flag a vanished profile. Needs the upstream tree or a
  network fetch of the release listing.

- **Train: stage the proof run** *(S; new in posts/2026-09-03.html)* —
  cs2-train's fresh-install validation is one pod away from done: turn
  validate_chain.sh into the automated boot test that runs the moment a
  server is up — fresh install, bundle pull, plugin load, one scored
  scenario, receipts — so the final link is a single command. Costs
  nothing until cloud budget says go; repo lives on the train VM, not
  this box.
  *(09-04 devlog refinement: the server-side chain is proven with bots;
  the open link is the human test — `!train start` with a real player in
  the seat.)*

- **Train: give the box room to hold a bot** *(S; code lives on this box;
  repo private)* — new in posts/2026-09-12.html and named there as the new
  P0: set `sv_hibernate_when_empty 0` in the launcher and assert it in the
  seed guard with a test that fails when the line is missing — **shipped
  2026-09-12, see Done**. The rest of that item (chase the kick itself — a
  `bot_quota` / team-limit / `bot_join_after_player` interaction — until a
  log line says `placed 5/5` and holds for a minute) needs the live box and
  stays open below.

- **Train: the box must hold a bot (placed 5/5)** *(S; needs the train
  VM)* — the second half of the 09-12 P0, unsplit from it by this run so
  the shipped half is not mistaken for the whole: with hibernation off,
  find why a spawned bot is kicked (`bot_quota` / team-limit /
  `bot_join_after_player` on the shipped build) and keep going until a log
  line says `placed 5/5` and holds there for a minute. Acceptance:
  `placed 5/5` observed in the live log, bot still standing one minute
  later. Until then no headless end-to-end drill claim is real.

- **Train: fix the attribution before anything else** *(M; needs a cloud
  box; repo private)* — new in posts/2026-09-11.html, and named the new
  P0: the plugin must send the Steam identity it already has in the game
  session, scope the session-linking call to that identity instead of the
  placeholder, and prove it by starting one drill as a real account and
  watching history fill in. Every other customer-facing feature is
  decorative until this lands. Blocked on cloud budget.
- **Train: retry the live spatial pass** *(S; repo private)* — new in
  posts/2026-09-11.html: the real-geometry drift check is shipped and
  unit-tested; its live run was blocked by the box's bot-spawn quirk.
  Next: run it against the live server now that map prep handles bot
  quotas and team limits, and record the observed layer. Needs the train
  VM.

- **project-guard: adopt with a filter** *(S; pi-cicd)* — new in
  posts/2026-09-11.html; **shipped 2026-09-11, see Done** (deny-list read
  at adopt time + one-line skip report).

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
- **Train's first post-release feature: moving practice bots** *(L; new
  in posts/2026-09-08.html)* — FEATURE_PARITY marks bot behaviour the
  biggest gap vs SCL/Refrag; owner wants xfire-style bots (peeks,
  counter-strafes, swings) instead of standing targets. First concrete
  step: map what CounterStrikeSharp exposes for bot control, then
  prototype one moving behaviour. Post-release — Train's proof-run +
  human gate land first.
  *(09-09 devlog refinement — "moving bots, round two": reaction and aim
  control have since landed; the xfire-style behaviour itself — swings,
  counter-strafes, wide peeks — is the next increment, building on the
  peek amplitude/period hooks. First step: get the authored plugin code
  its first compile on the live box and verify the peek loop against a
  real player.)*

## In progress

*(none — the 09-14 pick shipped 2026-09-16; next run picks from Proposed)*

## Done

- **service-probe: drop the two dead funnel probes — and make the tool
  name the next leftover itself** — done 2026-09-18 (the only on-box **S**
  at the top of Proposed; its *decide drop-vs-repoint* instruction is what
  this run settled). Measured first, then chosen: `tailscale funnel
  status` shows :8443 now proxies **only** `/xmedia`, so `/` and `/mark/`
  are 404 **by design** (mark-site, retired 2026-09-15, took `/mark/`
  with it) — nothing is meant to serve them, so the answer was *drop*, not
  repoint. Both rows were at **4379 consecutive failed sweeps** with
  `HTTP 404`.
  - **Live** (`/etc/service-probe.conf`, ev:ev 600, comment block dated):
    `funnel-mark` and `funnel-root` removed from `PROBE_HTTP`; next sweep
    pruned their state rows. Verified in the environment:
    `journalctl -u service-probe` → `✓ 4 up, 0 down`, `service-probe
    --list` shows **4 rows, none stale** (adguard, kiosk-home, ntfy,
    portal), and `status.json` — what the portal renders — carries no
    funnel row.
  - **Why it took a devlog to find them:** DOWN alerts are
    edge-triggered, so a hopelessly dead endpoint fires once and then goes
    silent forever, looking exactly like a healthy quiet one. The tool now
    closes that blind spot: a probe past `DEFAULT_STALE_FAILS` (1000)
    consecutive failures is named in every sweep (`! N probe(s) long-dead
    … drop from PROBE_HTTP/PROBE_DNS`) and marked in `--list`
    (`stale — probe looks retired`). It publishes nothing — a config fact
    is not a new outage.
  - **Evidence:** pi-cicd commit `0c29fc2`; `tests/test_service_probe.py`
    +2 (the real script, seeded 4379-fail rows: a long-dead probe is
    flagged in `--list`, and named in the sweep with `published == []`) —
    **28 passed** in the file, full suite **262 passed**; **CI green (run
    35307438413)** on `0c29fc2`. Negative-controlled by
    execution: both new tests fail against the pre-change script read out
    of git (`/tmp/nc`). Repo: <https://github.com/pkia/pi-cicd>.

- **pi-cicd: sync the unit and layer docs with the retirements** — done
  2026-09-17 (new in posts/2026-09-16.html; picked as the only Proposed **S**
  that lives on this box). What was actually stale, measured rather than
  assumed: `docs/layers.md` still advertised "the seven local services
  (including cs2-tracker's JSON `healthy` gate) … 12 probes total" for a
  probe set that no longer contains cs2-tracker, cs2-dashboard or
  mark-site; `templates/service-probe.conf.example` still carried
  `cs2-dash`, `cs2-tracker` and `mark-site` probes (the live
  `/etc/service-probe.conf` was already clean, so the example was the only
  copy still seeding dead endpoints); and **mission-control** (:8788, the
  Hermes Kanban board, host-local unit in `/etc/systemd/system`) was running
  but absent from the index. Also fixed in the portal: project-hub's
  registry still listed a CS2 Dashboard card + status row for the retired
  unit.
  - **pi-cicd** `93faaca`: mission-control row in `docs/units.md` + a note
    naming it as host-local (sibling of the portal registry); the
    service-probing layer rewritten to point at the live config instead of
    a rotting count, with the retired endpoints named as not-probed;
    probe example rewritten (retired local dashboards and funnel-mark gone,
    `cs2-dash`/`cs2trk` spellings called out as dead).
  - **Tests (the acceptance, not prose):** `tests/test_units_doc.py` +2 —
    no retired unit may appear as a live index row, and the shipped probe
    example must target no retired endpoint, matched on every spelling ever
    used (`cs2-dash`, `cs2trk`, unit names). **Negative-controlled by
    execution:** `scripts/negative_control_docs_sync.py` applies the exact
    predicates to the pre-change files read out of git — the old probe
    example fails them (`cs2-tracker=…8092/healthz`, `mark-site=…8089/`),
    the old layers prose carried the dead healthz claim; the index-row
    assertion is a forward guard (no retired unit was ever a *row*, the
    staleness sat in prose).
    **261 passed** in pi-cicd (48 in the three touched files).
  - **project-hub** `df68069`: CS2 Dashboard project entry and its
    `SERVICES` row removed; `tests/test_app.py` +1 pinning
    `PROJECTS`/`SERVICES` against all three retired unit names —
    **10 passed**.
  - **Stale-probe count is zero, checked live:** `service-probe --list`
    lists 6 rows, none retired (the state pruned them on the config drop).
  - **Found while verifying, recorded not silently fixed:** two *live*
    probes are red with 4092 consecutive failures (`funnel-mark`,
    `funnel-root`, HTTP 404) — filed as its own Proposed S so the fix is a
    decision, not a drive-by edit.
  - Budget honesty: the run's discovery cost made ≈38 tool calls, over the
    20-call contract — recorded in the Run log rather than hidden. No ruff
    binary on this box, so the fast lint gate was skipped; CI runs ruff.
  Evidence: CI run 35182347278 (pi-cicd) / 35182353690 (project-hub) on
  these SHAs. Repos: <https://github.com/pkia/pi-cicd>,
  <https://github.com/pkia/project-hub>.
- **Train: map the routes before the corpus shrinks** — done 2026-09-16
  (resumed from the 09-14 pick; the 09-16 devlog named the concrete next
  step: *"reconcile scenario slugs against the prefire profiles … run the
  mapper across the scenario files and commit the reconciliation report,
  unmatched slugs included"*). Shipped in cs2-train:
  `scripts/reconcile_corpus_routes.py`, `docs/route_reconciliation.json`,
  7 tests in `tests/test_corpus_route_map.py`. The mapper re-derives the
  corpus map from `engine/scenarios/*.json` and re-measures the claims in
  `docs/ROUTE_MAPPING.md` — until now prose measured once on 09-11 with
  nothing checking it:
  - **587 scenarios** = 497 map drills over 9 maps (nuke 81, anubis 63,
    mirage 63, overpass 63, dust2 54, ancient 45, inferno 45, vertigo 45,
    train 36) + 90 arena; **495** carry the OpenPrefirePrac attribution
    (165 prefire + 165 aim + 165 recoil). Every doc number agrees.
  - every conversion-derived slug decomposes to (map, route, difficulty,
    mode) and re-composes byte-identically, and every route carries the full
    3×3 difficulty×mode grid (`incomplete_routes` empty) — a renamed route
    or a dropped mode reddens CI instead of surfacing as a live 404.
  - **the unmatched slugs, named:** `dust2-b_long-peek-d1` and
    `mirage-a_ramp-peek-d1` are hand-authored peek-behaviour scenarios
    (`attribution.source: dunbar-engineered`) that never came from the
    converter — right shape, no mode suffix. The report declares them as
    `known_exceptions` with the reason, so a *new* odd slug shows up in the
    report diff rather than hiding behind an allowlist.
  - **honest gap, recorded not guessed:** the upstream side — the **55**
    OpenPrefirePrac practice profiles — cannot be re-measured on this box
    (`/tmp/opp` absent), so it is reported as `unmeasured` with a resume
    pointer. The item's acceptance is met for the public surface, not for
    the upstream release.
  Evidence: cs2-train commit `09f3924` (pushed, CI on push); `--check` green
  (`ROUTE-MAP: OK`), 7/7 new tests, ruff clean on the changed files.
  `release_check.sh` was cut off by the run's tool timeout, not by a failure
  — CI runs the full gate. Repo:
  <https://github.com/pkia/cs2-train>.

- **Train: give the box room to hold a bot — `sv_hibernate_when_empty 0`
  in the launcher** — done 2026-09-12 (the 09-12 devlog's *new P0*, tagged
  S and living on this box; picked ahead of the 422 item, which turned out
  to be already shipped — see the Run log). The root cause on the board was
  real and quiet: the seed writes the box's `server.cfg` and never disabled
  hibernation, so an empty server hibernated, its world-update callbacks
  stopped, and a drill's deferred bot placement never ran — the bots
  "vanish" with no error line (docs/WORKLOG.md, from the live bot-spawn
  chase: *"the launcher does not set `sv_hibernate_when_empty 0` … set at
  runtime for this test only"*). Shipped in `deploy/box_seed.sh`:
  `sv_hibernate_when_empty 0` is appended to the cfg the seed itself writes,
  **after** the `rcon_password` line, which truncates with `>` — the order
  is now pinned by a test, because a later re-seed reorder would silently
  erase it. The embedded cloud-init boxes actually execute was **stale**
  (its base64 copy predated several seed edits, not just this one) and was
  regenerated with `scripts/gen_seed.py`; that script keeps timestamped
  `.bak` copies. Evidence: cs2-train commit `f06116d`, 3 new tests in
  `tests/test_hibernate_cvar.py` — the source of truth carries the line in
  the cfg it writes, the script still passes `bash -n`, and (Pi-only drift
  guard) the embedded copy carries it too; **negative-controlled by
  execution**: a stripped seed and a stale embedded copy were both fed to
  the real assertions and both failed. Suite: **860 collected**, 858 passed
  / 1 skipped; the one failure was the docs-count drift test and it drove a
  measured correction (README + docs/FIRST_HUMAN_E2E 857 → 860), 20/20 on
  the targeted re-run, CI cited in the Run log. Repo:
  <https://github.com/pkia/cs2-train>.
  *Not done, and not claimed: the item's second half — chase the kick until
  a log line says `placed 5/5` and holds a minute. That needs the live box
  and is left as its own Proposed entry.*

- **project-guard: adopt with a filter** — done 2026-09-11 (new in the
  09-11 devlog radar list, tagged S in pi-cicd: "an explicit deny-list
  file, read at adopt time, plus a one-line report when a directory is
  skipped"). Shipped in `project-guard`: adoption is now filtered by
  `~/.config/project-guard/deny-list` (override `$GUARD_DENY_LIST`) — one
  glob pattern per line, `#` comments, matched against both the
  directory's basename and its full path, read at adopt time so editing
  it needs no restart. A denied directory is left byte-identical (no
  `git init`, no `.gitignore`, no commit) and reported in one log line,
  deduplicated through `~/.local/state/project-guard-denied.state` so a
  standing exclusion costs one line rather than one every 10 minutes —
  the guard's log stays event-only. Deliberate scope boundary, stated in
  the code and docs: the filter is **adoption-only**; directories that
  are already git repos keep going through push + autosave, and the
  built-in `EXCLUDE` names still apply. Evidence: **254/254 pytest** (5
  new, hermetic — the REAL script against a throwaway `GUARD_HOME` with
  no gh config and no network: skip + one-line report, report-once
  across three sweeps, no-list-is-no-change, path patterns / nested
  `apps/`, and an existing deny-listed repo still backed up), CI run
  **34563342137**, README row + `docs/layers.md` refreshed, and the live
  config file created on the Pi (comment-only, so behaviour is unchanged
  until the owner adds a pattern). Repo:
  <https://github.com/pkia/pi-cicd> commit `b9fe069`.

- **Prom stack step 3b: `metric-alert` (stdlib rule-check alerting)** —
  done 2026-09-10. The item's two open questions, both decided: the
  consumer is a **stdlib rule-check**, not Alertmanager (a second daemon
  with its own config language for five rules, when Prometheus is already
  scraped and the query API is free); and the **mute gap is closed**,
  because alerts publish through `ntfy_lib` exactly like every other
  pi-cicd publisher — `ntfy-notify --mute` silences metric alerts too,
  which an Alertmanager webhook receiver (outside ntfy_lib) never could.
  Topic is the already-provisioned `services` topic: no new ACL grant and
  no ntfy restart; docs/prometheus.md notes the one-line split to a
  dedicated `alerts` topic if volume ever justifies it. Behaviour:
  `RULE=Name op threshold = promql` lines are instant-queried against the
  loopback Prometheus; a breach must hold CONFIRM_FAILS sweeps (default
  2) before it alerts; alerting is edge-triggered (one message on breach,
  one on recovery, silence while standing). Shipped rules: disk used %,
  SoC temp, memory used %, failed systemd units, any scrape target down.
  systemd service + 5 min timer offset 4 min from service-probe so the
  two sweeps never stack — probe answers "is it up", metric-alert "is it
  healthy". Evidence: **249/249 pytest** (27 new hermetic — fake
  Prometheus JSON through an injected `_urlopen`, stubbed query, captured
  publish), CI green **(run 34437718662)**, and a live sweep against the
  real Prometheus: DiskRootPct 14.88 / CpuTempC 50.7 / MemUsedPct 46.06 /
  FailedUnits **1** (firing, 1st of 2 confirm sweeps) / ScrapeTargetDown
  1; timer active with the next run 4 min out. En-route live find: the
  first root-created `/etc/metric-alert.conf` was mode 600 root, so the
  timer's `ev` user saw an empty rule set with no complaint — the config
  is now ev-owned 600 and load_config says so loudly when it is missing
  or unreadable (see LESSONS). Repo: <https://github.com/pkia/pi-cicd>
  commit `e1b72da`.

- **Prom stack step 3a: the ntfy `/metrics` scrape** — done 2026-09-09
  (picked from the 09-09 devlog radar list — "still the queued half of
  the stack"; the other three radar items need a human in the seat, the
  train VM, or cloud budget, so the S on this box was the pick). The
  scrape half of step 3: `metrics-listen-http: "127.0.0.1:9091"` added
  to the live ntfy server config (/etc/ntfy/server.yml, root-owned,
  backup kept as server.yml.bak-promstep3, pi-backup-covered) with the
  item's ONE planned ntfy restart done at the quiet 05:32 hour; an
  `ntfy` job (loopback :9091) added to the source-of-truth
  prometheus/prometheus.yml, copied to /etc/prometheus and Prometheus
  reloaded (live file differed only by the missing job — clean
  overwrite). Evidence: **220/220 pytest locally** (test pin extended to
  three jobs); live `up{job="ntfy", instance="127.0.0.1:9091"} = 1` via
  the query API, ntfy active post-restart, `/metrics` answering. Repo:
  <https://github.com/pkia/pi-cicd> commit `a270a93` (CI triggered on
  push). Remaining step-3b (metric alerting) is a decision item — see
  Proposed. docs/prometheus.md refreshed to match (step-3a shipped,
  step-3b remaining).

- **Mine the heal ledger — cs2-train CI storm retired, heal has no job
  left** — done 2026-09-08 (09-07 shipped the ruff root-cause fix
  `9e78d03`; this run fixed the remaining two CI-only hermeticity
  failures in tests/test_hetzner.py). Mechanism correction: the 09-07
  "CLI crash under the runner's HOME" suspect was wrong — the deployed
  `~/.hermes/cloud/hetzner_cloud.py` is hermes cloud tooling that CI
  runners simply don't have, so the subprocess never found the file
  (python's error goes to stderr, stdout stays empty). Hermeticised in
  cs2-train `aa54bd4`: (1) routing test no longer opens the real
  ~/.hermes/.env — a tmp .env via monkeypatched expanduser now asserts
  BOTH branches deterministically (token → HETZNER_CLOUD, none →
  GPU_CLOUD); (2) CLI contract test skipif-absent (dev-box artifact)
  with HOME isolated via tmp_path and stderr surfaced in failure
  messages. En-route finding: the no-token CLI contract is exit 1 +
  JSON `{"ok": false, "error": "no HETZNER_API_TOKEN"}` on stdout — the
  gate is stdout JSON, not the return code. Evidence: **CI green (run
  34187336138, 35 s) — first green cs2-train push since 09-05**;
  281/281 pytest locally (3/3 hetzner). Owner's unrelated dirty work
  (map_sessions/customer demo) left untouched. Repo:
  <https://github.com/pkia/cs2-train> commit `aa54bd4`. The
  `ci-rerun-queued` heal should retire on the next pipeline-check
  sweeps — confirm via the ledger next run.

- **Prom stack step 2: the pinned dashboard (`prom-dash`, pi-cicd
  native)** — code done 2026-09-05, board recorded 2026-09-06 (the 09-05
  run shipped and died before its ledger commit; the 09-06 devlog said
  it plainly: "the implementer owes the board a paragraph" — this run
  verified the ship green and closed the loop). Concretisation: the
  board's "Grafana from apt" premise was false — grafana is NOT in
  Debian trixie (no apt candidate) and this box runs Debian packages
  only (no third-party repos, no containers) — so the graphs got a
  native answer: `prom-dash` range-queries the loopback Prometheus for
  the four panels the devlogs quote — CPU temperature vs load,
  active/failed systemd units — and renders ONE self-contained HTML
  page with inline SVG sparklines. On demand, ~0 MB resident (the ~102
  MB scrape layer stays the stack's whole footprint). A real bug died
  en route: node_systemd_unit_state is a 0/1 gauge per (unit, candidate
  state), so count() overcounted — 197 "active" vs 99 real — and sum()
  is the truth. PANELS is the pin: hermetic tests bind a fake
  Prometheus to exactly those queries. Evidence: 220/220 pytest locally
  (4 new); live render 2026-09-06 exit 0 — 24 h temp 45.9–50.7 °C,
  load 0.0–1.4, 99 active / 0 failed units. Repo:
  <https://github.com/pkia/pi-cicd> commits `a48fafb`, `9c02da7`;
  install.sh links it (no timer — on demand by design);
  docs/prometheus.md step-2 section refreshed to match (2026-09-06,
  board run). Remaining step-3 scope is a Proposed item (ntfy
  `/metrics` + metric-alerting consumer decision).

- **Mine-the-heal-ledger blocker re-verified — the 09-03 "never
  deployable" verdict was wrong; the healers were live all along** — done
  2026-09-04 (resumed the 09-03 thread; repo + live evidence, no code gap
  found). The 09-03 finding checked systemd only and missed the
  architecture its own units.md documents: pipeline-check and pi-doctor
  are **Hermes cron jobs**, not systemd units. Verified live via
  `hermes cron list`: "Pipeline compliance check" runs 01:00 & 13:00 via
  `pipeline-check-wrapper.sh`, which `exec`s `/home/ev/pi-cicd/
  pipeline-check` **by absolute path** (PATH never mattered) — last run
  2026-09-04 01:01 **ok**; "pi-doctor daily audit" runs 06:30 daily —
  last run 09-03 06:31 **ok**. The heal ledger
  (`~/.local/state/pipeline-check/status.json`) is empty because **no
  heal has fired** since the 09-01 ship (~6 pipeline-check runs + 2
  audits, zero fixes on a healthy box — pi-doctor's own audit agrees: no
  issues), not because the healers were missing. Ships: units.md rows
  corrected to reality (pipeline-check cron `0 1,13 * * *` + wrapper,
  pi-doctor cron `30 6 * * *`), test_install_sh.py docstring corrected so
  it no longer fossilises the wrong "ledger could never be written"
  causal claim; install.sh re-run live so the 09-03 e4c1293 links
  finally exist for interactive use (pipeline-check + pi-doctor now on
  PATH). 216/216 pytest locally. Repo: <https://github.com/pkia/pi-cicd>
  commit `f925967` (CI pending at write time). The mining item stays
  Proposed — it becomes actionable once heals accrue.

- **Mine-the-heal-ledger blocker: self-healer was never deployable** —
  done 2026-09-03 (pick was mine the heal ledger, Proposed S; repo
  evidence stopped it cold and the real root cause got fixed instead).
  Live-box check: `which pipeline-check` → missing, no pipeline-check or
  pi-doctor unit in systemd/, no timer, and project-guard (the only
  installed driver, symlinked to repo HEAD) invokes neither — so the
  09-01 heal-ledger ship was repo-only and
  `~/.local/state/pipeline-check/status.json` has never been created.
  install.sh linked 8 of the 10 repo tools and omitted pipeline-check and
  pi-doctor since their ships. Fix: both added to install.sh's ln -sf +
  chmod blocks; new tests/test_install_sh.py binds the installer to every
  repo tool (and rejects stray links). 216/216 pytest locally (2 new);
  Repo: <https://github.com/pkia/pi-cicd> commit `e4c1293` (CI pending at
  write time). *09-04: this verdict was partially wrong — see the
  correction entry above; the systemd-only check missed the Hermes-cron
  scheduling units.md documents.*

- **Prometheus + node_exporter scrape (Prom stack, step 1)** — done
  2026-09-02 (the 09-02 devlog named the stack "the next pick" and asked
  whether the graphs earn their RAM — answered live: ~102 MB RSS total,
  a rounding error on an 8 GB box; Grafana is the real cost to watch).
  Installed prometheus 2.53.3 + prometheus-node-exporter from Debian (no
  containers, this box's way), both pinned to loopback via committed
  systemd drop-ins (the tailnet must not see an unauthenticated
  Prometheus), minimal `prometheus/prometheus.yml` as source of truth
  copied to /etc/prometheus/ by install.sh, systemd collector on (990
  node_systemd_unit_state series — per-service health over time, raw
  material for the dashboard graph). Live evidence: both services active,
  `up` = 1 for the `prometheus` and `node` jobs via the query API, pi-cicd
  units visible as unit-state series. 214/214 pytest (4 new —
  tests/test_prometheus_config.py binds the config: jobs present,
  loopback-only targets, 15 s interval, docs naming). Repo:
  <https://github.com/pkia/pi-cicd> commit `bd7d54f` (CI run pending at
  write time). Docs: docs/prometheus.md (layer map + step-2 scope).

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
  32689099974); committed live check
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

- 2026-09-18 — implementer run: synced the 09-17 devlog radar list (its
  two new items added to Proposed: *one retired list, three readers*,
  *measure the upstream half*) and picked the older top item, **service-probe:
  two dead funnel probes**. Decided drop-not-repoint on measured evidence
  (`tailscale funnel status`: :8443 serves only `/xmedia`, so `/` and
  `/mark/` 404 by design) and dropped both rows from the live
  `/etc/service-probe.conf`; next sweep pruned them — journal `✓ 4 up, 0
  down`, `--list` 4 rows and no stale streak, `status.json` clean. Because
  edge-triggered DOWN alerts made a 4379-sweep-dead probe invisible after
  its first alert, service-probe now names any probe past 1000 consecutive
  failures in the sweep and in `--list` (publishes nothing); pi-cicd
  `0c29fc2`, +2 tests (28 passed in the file, 262 in the suite, CI run
  35307438413 green), negative-controlled against the pre-change script
  from git. Repo: <https://github.com/pkia/pi-cicd>. Budget honesty: ≈24
  tool calls, over the 20-call contract — the run measured the live funnel
  config before deciding drop-vs-repoint rather than guessing.

- 2026-09-17 — implementer run: picked the 09-16 devlog's only on-box **S**
  (*pi-cicd: sync the unit and layer docs with the retirements*). Shipped the
  sync in two repos: pi-cicd `93faaca` (mission-control indexed in
  docs/units.md, layers.md's "seven local services / 12 probes / cs2-tracker
  healthy gate" claim replaced by a pointer to the live config, the shipped
  probe example stripped of the retired cs2-dash / cs2-tracker / mark-site
  rows, +2 tests) and project-hub `df68069` (retired CS2 Dashboard dropped
  from the portal registry, +1 test pinning PROJECTS/SERVICES against every
  retired name). Negative-controlled by execution against the pre-change
  files read out of git: the old probe example fails the new predicate.
  261 passed in pi-cicd, 10 in project-hub; live `service-probe --list` shows
  6 rows and zero retired ones. En-route finding filed as a new Proposed S:
  `funnel-mark` and `funnel-root` are **live probes down 4092 sweeps with
  HTTP 404** — a drop-or-repoint decision left to the owner rather than
  fixed in this run's scope. Budget honesty: ≈38 tool calls, over the
  20-call contract (doc-sync items touch two repos and needed the pre/post
  measurement to avoid guessing); no ruff binary on this box, so the local
  lint gate was skipped and CI carries it. Repos:
  <https://github.com/pkia/pi-cicd>,
  <https://github.com/pkia/project-hub>.

- 2026-09-16 — implementer run: **resume-first pick, finished** — the In
  progress item (*Train: map the routes before the corpus shrinks*) was the
  pick; the 09-16 devlog named its next step and it was on-box. Shipped the
  corpus route reconciliation mapper in cs2-train
  (`scripts/reconcile_corpus_routes.py` + `docs/route_reconciliation.json` +
  7 tests, commit `09f3924`): 587 scenarios decomposed, 497 map drills over
  9 maps, 90 arena, 495 upstream-attributed, full 3×3 grid present, doc
  claims in ROUTE_MAPPING.md now re-measured by CI. Found and named the two
  real odd ones (`dust2-b_long-peek-d1`, `mirage-a_ramp-peek-d1` —
  hand-authored, no mode suffix), declared as `known_exceptions`; the
  upstream 55-profile count is recorded `unmeasured` with a resume pointer
  (`/tmp/opp` absent) rather than guessed. Board: item moved to Done, the
  09-16 devlog's pi-cicd docs item added to Proposed. Budget honesty: the
  run's own gate — `bash scripts/release_check.sh` — was killed by the tool
  timeout while it ran the pytest stage, so the push carries the fast gates
  (ruff on changed files, `--check`, 7/7 new tests) and CI runs the full
  one; discovery in an unfamiliar repo also pushed this run past the 20-call
  efficiency cap (≈33), which is recorded here rather than hidden. Repo:
  <https://github.com/pkia/cs2-train>.

- 2026-09-14 — implementer run: moved 'Train: map the routes before the corpus shrinks' to In progress; added board-invariants test asserting at most one In progress item; tests: 2 passed. Commit: 28a0164. Repo: https://github.com/pkia/radar

- 2026-09-12 — implementer run: synced the 09-12 devlog radar list (new P0
  "give the box room to hold a bot", "map the routes", the attribution item
  restated, and the still-open 422 item). **En-route correction to the
  board:** the 422 item — "the cheapest real bug on the board" for two
  devlogs running — is *already shipped*: cs2-train has
  `tests/test_t047_broken_controls.py`, which executes both call-site
  expressions under Node and asserts `api()` received a JSON string, plus a
  class-level guard against any bare `body: {`. A repo-wide scan for a raw
  `body:` found only one, and it is the intentional binary upload
  (`application/octet-stream`, ArrayBuffer). So the item was dropped from
  Proposed rather than re-fixed; the devlog's radar list is generated from
  the board's own prose, so a stale entry self-perpetuates — worth watching.
  The pick was the new P0's on-box half: `sv_hibernate_when_empty 0` seeded
  into the box's `server.cfg`, 3 new tests (negative-controlled), the stale
  embedded cloud-init regenerated, README/docs counters corrected to the
  measured 860. The live half (`placed 5/5` holding for a minute) needs the
  train VM and is its own Proposed entry, explicitly unsplit so the shipped
  half is not mistaken for the whole. Splitting the 09-12 P0 into
  "seeded" + "verified live" is the honest shape. Repo:
  <https://github.com/pkia/cs2-train> commit `f06116d`.

- 2026-09-11 — implementer run: synced the 09-11 devlog radar list — it
  introduced three new train items (attribution P0, the two HTTP-422
  controls, the live spatial pass) plus the pi-cicd one; the two train
  blockers were added to Proposed, and the pick was the item that lives
  on this box: **project-guard: adopt with a filter**. Shipped the adopt
  deny-list (glob file read at adopt time, one-line deduplicated skip
  report, adoption-only so autosave is untouched), 5 hermetic tests
  driving the real script against a throwaway HOME, 254/254 pytest, CI
  run 34563342137, README + docs/layers.md refreshed, live config file
  created comment-only on the Pi. Remaining Proposed now needs a cloud
  box, the train VM, or the human seat — the only other on-box S was the
  changedetection.io leftover (browser-based arbitrary-page diffing).
  See Done. Repo: <https://github.com/pkia/pi-cicd> commit `b9fe069`.

- 2026-09-10 — implementer run: synced the radar lists (the 09-10 devlog
  added nothing beyond items already on the board; the three Proposed
  entries before this run all need a human in the seat, the train VM, or
  cloud budget — this run picked the one that lives on this box). Shipped
  **Prom stack step 3b `metric-alert`** in pi-cicd: stdlib rule-check
  alerting off the loopback Prometheus, edge-triggered with 2-sweep
  confirmation, publishing through ntfy_lib (which is the answer to the
  item's mute gap), topic `services` so no new ACL or ntfy restart; 27
  hermetic tests, 249/249 green, live sweep on the real Prometheus, timer
  active. En route: root-owned 600 config silently emptied the rule set —
  fixed + made loud + test pinned. See Done. Remaining Proposed: the two
  train items (train VM / cloud budget) and the L-sized moving-bots
  increment.

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
  drills **PASS live** with the chain read back off the `chaos` topic;
  portal Chaos Drills panel live via pull-CD; 203/203 + 9/9 tests, CI
  green (see Done). Remaining Proposed: Prom stack, architecture doc.
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
- 2026-09-02 — implementer run: synced the 09-02 devlog radar list (Prom
  stack named the next pick, its RAM question open; new idea — **mine the
  heal ledger** — added to Proposed). Picked **Prom stack step 1** (split
  the M item): Debian prometheus + node_exporter, loopback-bound via
  committed drop-ins, scrape config + install.sh wiring +
  docs/prometheus.md in pi-cicd; live targets UP, RAM measured (~102 MB
  RSS), 214/214 pytest, pushed `bd7d54f` (see Done). Remaining Proposed:
  Prom step 2 (Grafana + alerting), mine the heal ledger.
- 2026-09-03 — implementer run: synced the 09-03 devlog radar list (Prom
  step 2 + mine the heal ledger carried over; new — **Train: stage the
  proof run** — added to Proposed). Picked **mine the heal ledger**; the
  ledger turned out unmineable — repo evidence: pipeline-check not on
  PATH, no unit/timer anywhere, project-guard (autosave driver) never
  calls it; the 09-01 ledger ship was repo-only (install.sh linked 8/10
  tools). Fixed the deployability gap instead: install.sh links
  pipeline-check + pi-doctor (ln -sf + chmod), regression test
  tests/test_install_sh.py; 216/216 pytest, pushed `e4c1293`. Board:
  Done entry, blocker note on the mining idea, stale 08-31 self-healer
  dup cleaned out of Proposed.
- 2026-09-04 — implementer run: synced the 09-04 devlog radar list (item
  1 — "run install.sh, then mine for real" — repeats the 09-03 premise
  this run disproved; item 2 refines Train's last link to the human test;
  nothing genuinely new added). Picked **mine-the-heal-ledger blocker
  re-verification**: `hermes cron list` proves pipeline-check ("Pipeline
  compliance check", wrapper `exec`s the repo tool by absolute path,
  01:00 & 13:00) and pi-doctor ("pi-doctor daily audit", 06:30) were
  deployed and green all along — the 09-03 "never deployable" verdict
  looked at systemd only and missed the Hermes-cron scheduling units.md
  documents. Ledger empty = zero heals fired on a healthy box, not a
  deployment gap. Shipped: units.md reality fix + test_install_sh.py
  docstring correction in pi-cicd (`f925967`, 216/216 pytest), install.sh
  re-run live (pipeline-check/pi-doctor now on PATH for interactive use).
  Mining remains Proposed — re-check the ledger once heals accrue.
- 2026-09-06 — implementer run: synced the 09-06 devlog radar list
  (item 1, "Prom step-2 bookkeeping, then the other half" — adopted;
  item 2, heal-ledger re-check — came back actionable, not empty).
  Prom step 2: the 09-05 run had shipped `prom-dash` in pi-cicd
  (`a48fafb` + `9c02da7`) and died before its ledger commit; this run
  verified the ship (220/220 pytest; live render exit 0 — temp
  45.9–50.7 °C, load 0.0–1.4, 99 active / 0 failed units over 24 h),
  moved the item to Done and refreshed docs/prometheus.md (the stale
  "Grafana from apt" step-2 plan now records prom-dash + the remaining
  step-3 scope). Heal-ledger re-check: NOT empty — three
  `ci-rerun-queued` heals since 09-05, all cs2-train CI failures
  (`b4785f58`, `4b800525`, `dc27bbb7`); gh evidence: cs2-train CI red
  on EVERY push since 09-05 ~13:50 (12/12 runs failed, 11–27 s each,
  exit 1 with pytest "Found 1 error." — a collection/import error the
  re-run heal can never green). Mine-the-heal-ledger is now the next
  pick, resume pointer on the Proposed item. No code shipped this run —
  board + docs, the bookkeeping the 09-06 devlog explicitly owed.
  Budget honesty: discovering the unrecorded 09-05 ship + the surprise
  ledger finding pushed past the 20-call efficiency cap; closed the
  record anyway because the board is the state and stranding it would
  cost the next run the same discovery.
- 2026-09-07 — implementer run: picked **mine the heal ledger** (Proposed,
  actionable per 09-06). Root-caused the cs2-train rerun storm: CI's ruff
  gate (E9/F63/F7/F82) failed F821 on every commit since 09-05 —
  `skill_model` used unimported in session_end's §16 self-evaluation
  (api/control.py:306), hidden from pytest by the broad except. One-line
  fix pushed to pkia/cs2-train `9e78d03`; ruff + byte-compile + 250/250
  pytest green locally. CI now runs pytest for the first time since
  09-05: 248/250 — two pre-existing CI-only hermeticity failures in
  tests/test_hetzner.py (raw ~/.hermes/.env read; CLI empty-stdout on
  runner python 3.13.15) recorded on the Proposed item as the next step.
  Unrelated dirty work (customer_demo wiring) stashed/restored untouched
  around the fix. Heal not yet retired — cs2-train CI still red on the
  2 hetzner tests; board carries the resume pointer.
- 2026-09-08 — implementer run: picked the mine-the-heal-ledger resume
  pointer (09-07's recorded next step; nothing In progress). Fixed the
  two CI-only hetzner hermeticity failures in cs2-train
  tests/test_hetzner.py (`aa54bd4`): routing test driven by a tmp .env
  (both branches asserted), deployed-CLI contract test skipif-absent +
  isolated HOME via tmp_path + stderr in messages; found the real
  empty-stdout mechanism (deployed ~/.hermes CLI absent on the runner,
  not the suspected engine crash) and the no-token stdout-JSON contract
  (exit 1 is legal). 281/281 pytest locally; **CI green (run
  34187336138)** — first green cs2-train push since 09-05, heal should
  retire. Board: item to Done; devlog 09-08 radar list synced (heal
  item = this ship, human test + Prom step 3 already on board, moving
  practice bots added to Proposed as post-release L); owner's dirty
  tree untouched.
- 2026-09-09 — implementer run: synced the 09-09 devlog radar list (4
  items: human test + proof run already on board — both need the train
  VM/human; moving bots round-two refinement folded into the Proposed L
  item; Prom step 3 adopted as the pick — the only S actionable on this
  box). Picked **Prom step 3a: ntfy `/metrics` scrape**: repo side —
  `ntfy` job (loopback :9091) in prometheus/prometheus.yml, test pin
  extended to 3 jobs, docs/prometheus.md step-3a entry; live side —
  metrics-listen-http added to /etc/ntfy/server.yml (backup kept), the
  item's planned ntfy restart done 05:32, live prometheus.yml updated +
  reload. 220/220 pytest; live `up{job="ntfy"} = 1` via query API;
  pi-cicd pushed `a270a93` (see Done). Remaining Proposed: alerting
  half (step 3b, decision item), Train proof run, moving bots (L),
  heal-ledger mining (re-check once heals accrue).

- 2026-09-13 — implementer run: synced the board; no Proposed items actionable on this box (top items require train VM or cloud budget); board unchanged.

## Notes

- **AIS/RF track paused by owner 2026-08-23** — do not re-add AIS ideas
  (including from older devlog posts' "On the radar" lists) unless the
  owner lifts the pause. ais-catcher itself keeps running as the X bot's
  data source; treat it as maintenance-only, not a development target.
- "Keep this devlog honest and boring: tests green, deploys dull,
  rollback never needed" — standing quality bar for everything above, not
  a build task. *(2026-08-21)*
- **09-04 lesson (from the re-verification above):** repo evidence that
  checks systemd only is incomplete — hermes cron is a first-class
  scheduler on this box and units.md documents which units run where.
  Before declaring a tool "never deployed", check `hermes cron list` AND
  read the unit's own index row. The 09-03 run burned a session on this.
