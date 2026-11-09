#!/usr/bin/env python3
"""Board lint — IDEAS.md's house rules, executable.

The idea board is the loop's single source of truth. A malformed row —
a missing effort tag, a missing acceptance clause — used to fail only
when a human noticed. This checker parses IDEAS.md's sections and
requires every **actionable** row under ``## Proposed`` to carry:

- an effort tag: ``**S**``/``**M**``/``**L**`` or ``(S;``/``(M)``/``(L;``
  (the board's two established spellings), and
- an acceptance clause: ``**Acceptance:``.

A row is **ledger** (historical, exempt) when it carries a
``**SHIPPED``/``**SKIPPED``/``**RECORDED DONE`` stamp or points at its
outcome with ``see Done``/``see run log``/``see Notes``. Ledger rows are
reported in the OK line but never faulted — the checker reads Done and
Skipped history, it does not judge it.

Read-only by construction: the board is opened for reading only; the
checker never writes, renames or removes anything (asserted by
tests/test_check_board.py).

Exit codes: 0 clean, 1 faults (each fault names file, line, the row and
the missing part), 2 structural (unreadable file, no Proposed section).

Usage: check_board.py [BOARD]   (default: the repo's IDEAS.md)
"""

import re
import sys
from pathlib import Path

DEFAULT_BOARD = Path(__file__).resolve().parents[1] / "IDEAS.md"

# Ledger stamps: **SHIPPED …**, **SKIPPED …**, **RECORDED DONE …**, or a
# plain-prose pointer at the outcome ("shipped 2026-09-11, see Done",
# "shipped same day, see Done."). The pointer tolerates the board's
# wrapped lines — "see\n  Done." is the same phrase (bit the first run).
LEDGER_STAMP = re.compile(r"\*\*(?:SHIPPED|SKIPPED|RECORDED DONE)\b")
LEDGER_SEE = re.compile(r"\bsee\s+(?:Done|run\s+log|Notes)\b")

# Effort tag, two established spellings: **S** / **M** / **L** and the
# italic-meta form *(S; on-box; …)* — i.e. the letter in bold, or right
# after an opening paren.
EFFORT_TAG = re.compile(r"\*\*(?:S|M|L)\*\*|\((?:S|M|L)\s*[;)]")

ACCEPTANCE = re.compile(r"\*\*Acceptance:")

ROW_START = re.compile(r"^- ")
ROW_TITLE = re.compile(r"^- \*\*(.+?)\*\*")


def split_sections(text):
    """Yield (name, [row strings]) for every ``## `` section.

    A row is a top-level bullet (``^- ``) plus its continuation lines,
    up to the next top-level bullet or the next section header.
    """
    sections = []
    current = None
    for line in text.splitlines():
        header = re.match(r"^## (.+?)\s*$", line)
        if header:
            current = (header.group(1), [])
            sections.append(current)
            continue
        if current is not None:
            if ROW_START.match(line):
                current[1].append([line])
            elif current[1] and line.startswith((" ", "\t")):
                current[1][-1].append(line)
    return sections


def row_text(lines):
    return "\n".join(lines)


def row_label(lines):
    m = ROW_TITLE.match(lines[0])
    if m:
        return m.group(1)
    return lines[0][2:].strip()[:60]


def lint_board(text):
    """Return (faults, counts). faults: (line_no, label, missing)."""
    faults = []
    counts = {"actionable": 0, "ledger": 0}
    for name, rows in split_sections(text):
        if name.strip().lower() != "proposed":
            continue
        # Recompute line numbers: rows were collected as lists of lines,
        # so find each row's start offset in the original text.
        lines_all = text.splitlines()
        search_from = 0
        for lines in rows:
            start_line = None
            joined = row_text(lines)
            # locate this row's first line in the file (rows are unique
            # enough at their bullet; fall back to a scan counter)
            first = lines[0]
            for idx in range(search_from, len(lines_all)):
                if lines_all[idx] == first:
                    start_line = idx + 1
                    search_from = idx + 1
                    break
            if LEDGER_STAMP.search(joined) or LEDGER_SEE.search(joined):
                counts["ledger"] += 1
                continue
            counts["actionable"] += 1
            label = row_label(lines)
            if not EFFORT_TAG.search(joined):
                faults.append((start_line, label, "effort tag (**S**/**M**/**L**)"))
            if not ACCEPTANCE.search(joined):
                faults.append((start_line, label, "acceptance clause (**Acceptance:**)"))
    return faults, counts


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_BOARD
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"board-lint: cannot read {path}: {exc}")
        return 2
    sections = [name for name, _ in split_sections(text)]
    if not any(name.strip().lower() == "proposed" for name in sections):
        print(f"board-lint: no '## Proposed' section in {path}")
        return 2
    faults, counts = lint_board(text)
    for line_no, label, missing in faults:
        print(f"FAIL {path}:{line_no} — row \"{label}\" missing {missing}")
    if faults:
        print(
            f"board-lint: {len(faults)} fault(s) in {counts['actionable']} "
            f"actionable Proposed row(s)"
        )
        return 1
    print(
        f"OK — board lint: {counts['actionable']} actionable Proposed row(s) "
        f"checked, {counts['ledger']} ledger row(s) exempt"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
