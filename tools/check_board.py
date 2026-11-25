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
  history of the repo its row names. The repo is the project name
  written beside the ref — ``pi-cicd `38c65ce```, ``**project-hub**
  `df68069``` inside a pi-cicd row — falling back to the row title's
  project prefix (``radar — …``, ``cluster — …``) when no name sits
  next to it. Only repos supplied with ``--repo NAME=PATH`` are checked
  (the checker's own radar repo by default, which is all a CI checkout
  has). A ref the checker cannot answer for is *unverified* with its
  reason named — repo not supplied, the checkout is shallow (a shallow
  clone cannot prove a commit absent), or the path is not a usable
  repository — never faulted: a gate that faults on what it cannot see
  would be red forever, and a false fault costs a run to disprove.

Deployment scope is checked too (added 2026-11-15): the owner's directive
of 2026-11-02 limits the loop to the current Pi 5 deployment. An
**actionable** Proposed row naming a retired project — the old Pi
deployment's repos or Train/cs2-train — can never ship, so it is a fault:
without the rule such a row lints green, the run reads it, and then skips
it. Ledger rows are exempt (the Skipped history names those projects
legitimately), and only the title's project prefix is judged, never the
prose.

Read-only by construction: the board is opened for reading only and git
is only ever asked ``cat-file`` (asserted by tests/test_check_board.py).

Exit codes: 0 clean, 1 faults (each fault names file, line, the row and
the broken part), 2 structural (unreadable file, no Proposed section).

Usage: check_board.py [BOARD] [--repo NAME=PATH ...] [--explain]
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

# Row title prefix → the repo whose history its commit refs belong in.
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
    # Ledger history cites a retired project's commits inside an in-scope
    # row ("**project-hub** `df68069`"); the ref still has a repo, even
    # though the project can never be picked again.
    "project-hub": "project-hub",
    "maritime-dashboard": "maritime-dashboard",
}

# Names a ref can be bound to *beside itself* in a row: every prefix above
# plus every repo name those prefixes map to (a row writes the repo, not
# the prefix, next to its sha).
BIND_REPOS = dict(PROJECT_REPOS)
BIND_REPOS.update({repo: repo for repo in PROJECT_REPOS.values()})
BIND_NAME = re.compile(
    r"(?<![a-z0-9._-])(?:"
    + "|".join(re.escape(n) for n in sorted(BIND_REPOS, key=len, reverse=True))
    + r")(?![a-z0-9._-])"
)
# Only markup may sit between the repo name and the ref it binds: the
# board's spellings are `pi-cicd `abc1234``, `**project-hub** `abc`` and
# `cluster-prototype `abc`, pi-cicd `def``.
BIND_GAP = re.compile(r"^[\s`*_:+,]*$")
BIND_GAP_MAX = 8

# Owner deployment scope (AGENTS.md "Deployment scope", directive
# 2026-11-02): the loop serves the current Pi 5 deployment only. A row
# naming one of these prefixes can never ship, so an **actionable** row
# carrying one is refused at lint time rather than discovered at pick time.
# Values are the project name the fault reports. Ledger rows are exempt.
OUT_OF_SCOPE = {
    "twitter-launch": "twitter-launch",
    "forex-copybot": "forex-copybot",
    "copybot": "forex-copybot",
    "maritime-dashboard": "maritime-dashboard",
    "project-hub": "project-hub",
    "ais_analysis": "ais_analysis",
    "ais-analysis": "ais_analysis",
    "camoufox-setup": "camoufox-setup",
    "train": "Train (cs2-train)",
    "cs2-train": "Train (cs2-train)",
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


def title_prefix(label):
    """The project name a row's title starts with (lowercased)."""
    head = re.split(r"\s+(?:—|–|-)\s+|:\s+", label.strip())[0]
    return head.replace("*", "").replace("`", "").strip().lower()


def project_repo(label):
    """The repo a row's commit refs belong to, from its title prefix."""
    return PROJECT_REPOS.get(title_prefix(label))


def bind_repo(line, ref_start, fallback):
    """The repo named beside the ref, else the row's title prefix.

    The board puts a ref's repo next to it — ``pi-cicd `38c65ce```,
    ``**project-hub** `df68069``` inside a pi-cicd row — and a row can
    legitimately cite two repos. The nearest preceding project name
    separated from the ref by markup alone is the binding. Anything
    looser (any mention anywhere in the row) would let a passing mention
    steal a ref from the repo that really holds it.
    """
    bound = None
    for match in BIND_NAME.finditer(line, 0, ref_start):
        gap = line[match.end():ref_start]
        if len(gap) <= BIND_GAP_MAX and BIND_GAP.match(gap):
            bound = BIND_REPOS[match.group(0).lower()]
    return bound or fallback


def bind_refs(text, fallback):
    """[(sha, repo_name)] for every commit ref in one row's text.

    A ref binds to the repo named beside it; a sha *repeated* in the same
    row (the board names a commit once and then cites it again in prose,
    often on a line with no repo name) binds to the repo it was already
    bound to in that row. Everything else falls back to the title prefix.
    """
    bound = {}
    out = []
    for match in COMMIT_REF.finditer(text):
        sha = match.group(1)
        if not any(c.isdigit() for c in sha):
            continue
        repo = bind_repo(text, match.start(), None)
        if repo is None:
            repo = bound.get(sha, fallback)
        else:
            bound[sha] = repo
        out.append((sha, repo))
    return out


# The only git questions this tool may ask: both read-only, both answer a
# fact about objects already on disk.
GIT_READ_VERBS = ("cat-file", "rev-parse")


def git_read(repo_path, *args):
    """Run one read-only git question; None when git itself is unavailable.

    The verb is asserted here, at the single call site, so a future
    addition cannot quietly turn the checker into something that writes.
    """
    assert args and args[0] in GIT_READ_VERBS, f"not a read-only verb: {args[:1]}"
    try:
        return subprocess.run(
            ["git", "-C", str(repo_path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None


def repo_state(repo_path):
    """'ok' | 'shallow' | 'unusable' — what this checkout can answer.

    ``cat-file -e`` answers "absent" for a commit older than a shallow
    clone's cut, which is indistinguishable from a bogus sha — so the
    checker asks the checkout what it is before believing its silence.
    """
    probe = git_read(repo_path, "rev-parse", "--git-dir")
    if probe is None or probe.returncode != 0:
        return "unusable"
    shallow = git_read(repo_path, "rev-parse", "--is-shallow-repository")
    if shallow is None or shallow.returncode != 0:
        return "unusable"
    return "shallow" if shallow.stdout.strip() == "true" else "ok"


def resolve_commit(repo_path, sha):
    """True/False as git answers; None when git itself is unavailable.

    ``cat-file -e`` is the read-only question "does this object exist" —
    it fetches nothing, writes nothing, and touches no ref.
    """
    proc = git_read(repo_path, "cat-file", "-e", sha + "^{commit}")
    if proc is None:
        return None
    return proc.returncode == 0


def commit_refs(text):
    return [sha for sha, _repo in bind_refs(text, None)]


def lint_board(text, repos=None):
    """Return (faults, counts, unverified).

    faults: (line_no, label, problem) — ``problem`` completes the
    sentence ``row "<label>" <problem>``. unverified: (line_no, sha,
    repo_name, reason) for every ref the supplied checkouts could not
    answer for.
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
    unverified = []
    counts = {
        "actionable": 0,
        "ledger": 0,
        "shipped": 0,
        "refs_checked": 0,
        "refs_unverified": 0,
        "unverified": {},
        "out_of_scope": 0,
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
                retired = OUT_OF_SCOPE.get(title_prefix(label))
                if retired:
                    counts["out_of_scope"] += 1
                    faults.append(
                        (
                            start_line,
                            label,
                            f"names out-of-scope project {retired} "
                            "(owner deployment scope, 2026-11-02)",
                        )
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
            bound_refs = bind_refs(joined, project_repo(label))
            if not bound_refs:
                continue
            states = {}
            for sha, repo_name in bound_refs:
                repo_path = repos.get(repo_name) if repo_name else None
                if repo_path is None:
                    reason = (
                        "row names no repo" if repo_name is None
                        else "repo not supplied"
                    )
                    counts["refs_unverified"] += 1
                    counts["unverified"][reason] = (
                        counts["unverified"].get(reason, 0) + 1
                    )
                    unverified.append((start_line, sha, repo_name, reason))
                    continue
                if repo_name not in states:
                    states[repo_name] = repo_state(repo_path)
                state = states[repo_name]
                if state != "ok":
                    reason = (
                        "repo is shallow" if state == "shallow"
                        else "repo path is not a usable checkout"
                    )
                    counts["refs_unverified"] += 1
                    counts["unverified"][reason] = (
                        counts["unverified"].get(reason, 0) + 1
                    )
                    unverified.append((start_line, sha, repo_name, reason))
                    continue
                verdict = resolve_commit(repo_path, sha)
                if verdict is None:
                    counts["refs_unverified"] += 1
                    counts["unverified"]["git unavailable"] = (
                        counts["unverified"].get("git unavailable", 0) + 1
                    )
                    unverified.append(
                        (start_line, sha, repo_name, "git unavailable")
                    )
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
    return faults, counts, unverified


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
    parser.add_argument(
        "--explain",
        action="store_true",
        help="print one line per commit ref the supplied checkouts could "
        "not answer for, naming the ref, its repo and the reason",
    )
    args = parser.parse_args(argv[1:])
    repos = {"radar": REPO_ROOT}
    for item in args.repo:
        name, _, path = item.partition("=")
        if not name.strip() or not path.strip():
            parser.error(f"--repo wants NAME=PATH, got {item!r}")
        repos[name.strip()] = Path(path.strip()).expanduser()
    return Path(args.board), repos, args.explain


def main(argv):
    try:
        path, repos, explain = parse_args(argv)
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
    faults, counts, unverified = lint_board(text, repos)
    if explain:
        for line_no, sha, repo_name, reason in unverified:
            where = f"bound to {repo_name}" if repo_name else "no repo named"
            print(f"UNVERIFIED {path}:{line_no} — ref `{sha}` ({where}): {reason}")
    for line_no, label, problem in faults:
        print(f'FAIL {path}:{line_no} — row "{label}" {problem}')
    if faults:
        print(
            f"board-lint: {len(faults)} fault(s) in {counts['actionable']} "
            f"actionable Proposed row(s)"
        )
        return 1
    checked_repos = ", ".join(sorted(repos)) or "none"
    if counts["refs_unverified"]:
        parts = [
            f"{n} {reason}" if len(counts["unverified"]) > 1 else reason
            for reason, n in sorted(counts["unverified"].items())
        ]
        unverified_text = f"{counts['refs_unverified']} unverified ({', '.join(parts)})"
    else:
        unverified_text = "0 unverified"
    print(
        f"OK — board lint: {counts['actionable']} actionable Proposed row(s) "
        f"checked, {counts['ledger']} ledger row(s) exempt, "
        f"{counts['shipped']} SHIPPED marker(s) matched to Done, "
        f"{counts['refs_checked']} commit ref(s) resolved in {checked_repos}, "
        f"{unverified_text}, "
        f"{counts['out_of_scope']} out-of-scope Proposed row(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
