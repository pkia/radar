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

Ledger **pointers** are checked, though (added 2026-11-12):

- a ``**SHIPPED`` stamp must land on a real Done row carrying the same
  title (the board's convention is that a Done row repeats its row's
  title verbatim; punctuation, bold and backticks are ignored in the
  comparison) — a stamp pointing at a row that is not there is a fault;
- a backticked commit reference (``abc1234``) must resolve in the
  history of the repo its row names. A row is bound to a repo by its
  title's project prefix (``radar — …``, ``personal-website — …``,
  ``cluster — …``, …) — the board's established spelling. Only repos
  supplied with ``--repo NAME=PATH`` are checked (the checker's own
  radar repo by default, which is all a CI checkout has); a ref bound
  to any other repo is reported as unverified, never faulted, because
  the checker cannot see a repository it was not handed.

Read-only by construction: the board is opened for reading only and git
is only ever asked ``cat-file`` (asserted by tests/test_check_board.py).

Exit codes: 0 clean, 1 faults (each fault names file, line, the row and
the broken part), 2 structural (unreadable file, no Proposed section).

Usage: check_board.py [BOARD] [--repo NAME=PATH ...]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOARD = REPO_ROOT / "IDEAS.md"

# Ledger stamps: **SHIPPED …**, **SKIPPED …**, **RECORDED DONE …**, or a
# plain-prose pointer at the outcome ("shipped 2026-09-11, see Done",
# "shipped same day, see Done."). The pointer tolerates the board's
# wrapped lines — "see\n  Done." is the same phrase (bit the first run).
LEDGER_STAMP = re.compile(r"\*\*(?:SHIPPED|SKIPPED|RECORDED DONE)\b")
LEDGER_SEE = re.compile(r"\bsee\s+(?:Done|run\s+log|Notes)\b")

# Only an explicit SHIPPED stamp is held to the Done-pointer rule. Plain
# prose ("→ concretised … and shipped same day, see Done") names an
# outcome without promising a same-title row, and the board predates the
# stamp convention — faulting those would red the board for history.
SHIPPED_STAMP = re.compile(r"\*\*SHIPPED\b")

# Effort tag, two established spellings: **S** / **M** / **L** and the
# italic-meta form *(S; on-box; …)* — i.e. the letter in bold, or right
# after an opening paren.
EFFORT_TAG = re.compile(r"\*\*(?:S|M|L)\*\*|\((?:S|M|L)\s*[;)]")

ACCEPTANCE = re.compile(r"\*\*Acceptance:")

ROW_START = re.compile(r"^- ")
ROW_TITLE = re.compile(r"^- \*\*(.+?)\*\*")

# A backticked 7–40 char lowercase-hex token with at least one digit is
# a commit reference (a run id is 11 digits and is never backticked; a
# word like `__pycache__` is not hex).
COMMIT_REF = re.compile(r"`([0-9a-f]{7,40})`")

# Row title prefix → the repo whose history its commit refs live in.
# The board names a project before the dash/colon, and this map is that
# convention made explicit. An unknown prefix means "cannot bind": its
# refs stay unverified rather than guessed at.
PROJECT_REPOS = {
    "radar": "radar",
    "personal-website": "pkia.github.io",
    "pkia.github.io": "pkia.github.io",
    "cluster": "cluster-prototype",
    "cluster-prototype": "cluster-prototype",
    "pi-cicd": "pi-cicd",
    "pi-backup": "pi-cicd",
    "pi-doctor": "pi-cicd",
    "switch-l4t-gpu": "switch-l4t-gpu",
    "twitter-launch": "twitter-launch",
    "forex-copybot": "forex-copybot",
    "copybot": "forex-copybot",
    "train": "cs2-train",
    "cs2-train": "cs2-train",
}


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


def normalise_title(text):
    """Compare titles as the board means them, not as they are spelled."""
    text = text.replace("*", "").replace("`", "")
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def project_repo(label):
    """The repo a row's commit refs belong to, from its title prefix."""
    head = re.split(r"\s+(?:—|–|-)\s+|:\s+", label.strip())[0]
    head = head.replace("*", "").replace("`", "").strip().lower()
    return PROJECT_REPOS.get(head)


def resolve_commit(repo_path, sha):
    """True/False as git answers; None when git itself is unavailable.

    ``cat-file -e`` is the read-only question "does this object exist" —
    it fetches nothing, writes nothing, and touches no ref.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "cat-file", "-e", sha + "^{commit}"],
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    return proc.returncode == 0


def commit_refs(text):
    return [sha for sha in COMMIT_REF.findall(text) if any(c.isdigit() for c in sha)]


def lint_board(text, repos=None):
    """Return (faults, counts).

    faults: (line_no, label, problem) — ``problem`` completes the
    sentence ``row "<label>" <problem>``.
    """
    repos = repos or {}
    sections = split_sections(text)
    done_titles = {
        normalise_title(row_label(lines))
        for name, rows in sections
        if name.strip().lower() == "done"
        for lines in rows
    }
    faults = []
    counts = {
        "actionable": 0,
        "ledger": 0,
        "shipped": 0,
        "refs_checked": 0,
        "refs_unverified": 0,
    }
    lines_all = text.splitlines()
    for name, rows in sections:
        section = name.strip().lower()
        if section not in ("proposed", "done"):
            continue
        search_from = 0
        for lines in rows:
            # locate this row's first line in the file (rows are unique
            # enough at their bullet; fall back to a scan counter)
            start_line = None
            first = lines[0]
            for idx in range(search_from, len(lines_all)):
                if lines_all[idx] == first:
                    start_line = idx + 1
                    search_from = idx + 1
                    break
            joined = row_text(lines)
            label = row_label(lines)

            is_ledger = bool(LEDGER_STAMP.search(joined) or LEDGER_SEE.search(joined))
            if is_ledger:
                counts["ledger"] += 1
            if section == "proposed" and not is_ledger:
                counts["actionable"] += 1
                if not EFFORT_TAG.search(joined):
                    faults.append(
                        (start_line, label, "missing effort tag (**S**/**M**/**L**)")
                    )
                if not ACCEPTANCE.search(joined):
                    faults.append(
                        (start_line, label, "missing acceptance clause (**Acceptance:**)")
                    )

            # ledger pointer: a SHIPPED stamp must land on a Done row
            if SHIPPED_STAMP.search(joined):
                counts["shipped"] += 1
                if normalise_title(label) not in done_titles:
                    faults.append(
                        (
                            start_line,
                            label,
                            "stamped SHIPPED but no Done row carries that title",
                        )
                    )

            # ledger pointer: commit refs resolve in the repo the row names
            refs = commit_refs(joined)
            if not refs:
                continue
            repo_name = project_repo(label)
            repo_path = repos.get(repo_name) if repo_name else None
            for sha in refs:
                if repo_path is None:
                    counts["refs_unverified"] += 1
                    continue
                verdict = resolve_commit(repo_path, sha)
                if verdict is None:
                    counts["refs_unverified"] += 1
                    continue
                counts["refs_checked"] += 1
                if not verdict:
                    faults.append(
                        (
                            start_line,
                            label,
                            f"cites `{sha}`, which is not in {repo_name} history",
                        )
                    )
    return faults, counts


def parse_args(argv):
    """(board path, {repo name: checkout}) — or SystemExit on bad flags."""
    parser = argparse.ArgumentParser(
        description="Lint IDEAS.md: row shape and ledger cross-references.",
    )
    parser.add_argument("board", nargs="?", default=str(DEFAULT_BOARD))
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="a checked-out repo whose commit refs can be resolved "
        "(repeatable; 'radar' defaults to this checkout)",
    )
    args = parser.parse_args(argv[1:])
    repos = {"radar": REPO_ROOT}
    for item in args.repo:
        name, _, path = item.partition("=")
        if not name.strip() or not path.strip():
            parser.error(f"--repo wants NAME=PATH, got {item!r}")
        repos[name.strip()] = Path(path.strip()).expanduser()
    return Path(args.board), repos


def main(argv):
    try:
        path, repos = parse_args(argv)
    except SystemExit as exc:  # argparse already printed the reason
        return 2 if exc.code else 0
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"board-lint: cannot read {path}: {exc}")
        return 2
    sections = [name for name, _ in split_sections(text)]
    if not any(name.strip().lower() == "proposed" for name in sections):
        print(f"board-lint: no '## Proposed' section in {path}")
        return 2
    faults, counts = lint_board(text, repos)
    for line_no, label, problem in faults:
        print(f'FAIL {path}:{line_no} — row "{label}" {problem}')
    if faults:
        print(
            f"board-lint: {len(faults)} fault(s) in {counts['actionable']} "
            f"actionable Proposed row(s)"
        )
        return 1
    checked_repos = ", ".join(sorted(repos)) or "none"
    print(
        f"OK — board lint: {counts['actionable']} actionable Proposed row(s) "
        f"checked, {counts['ledger']} ledger row(s) exempt, "
        f"{counts['shipped']} SHIPPED marker(s) matched to Done, "
        f"{counts['refs_checked']} commit ref(s) resolved in {checked_repos}, "
        f"{counts['refs_unverified']} unverified (repo not supplied)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
