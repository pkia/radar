# radar — lessons

Append-only memory for the implementer loop, newest at the top. Read at
run start; prune entries that no longer apply (keep it lean — a bloated
lessons file gets ignored).

- 429/usage-limit hits are coordination, not bad luck: the 07:00 devlog
  and the 09:00 implementer share one API usage window. Checkpoint early,
  stop, resume next run — never retry-spin. *(2026-08-21)*
- The board is the state, not the context. Untracked scratch files are
  invisible to the next run — commit WIP on a `wip/` branch instead.
  *(2026-08-21)*
- "Done" needs environment evidence: a green CI run or passing test
  output. Agents confidently report finishing work the environment
  contradicts; only evidence prevents that here. *(2026-08-21)*
- The single RTL-SDR dongle belongs to ais-catcher — new RF ideas need a
  second dongle or SDR sharing before any of them can run. *(2026-08-21)*
