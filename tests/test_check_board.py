"""Tests for tools/check_board.py — the IDEAS.md board lint.

Acceptance (board row, radar — lint the board in CI):
- a planted malformed row fails naming the row and the missing part;
- the current board passes clean;
- the checker never edits the board (read-only, asserted on source and
  by bytes-identical runs);
- the board-lint step is wired into this repo's CI — including the
  branch filter fix (the workflow triggered on main only while the
  default branch is master, so radar CI had never run).
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "tools" / "check_board.py"
BOARD = REPO / "IDEAS.md"
CI = REPO / ".github" / "workflows" / "ci.yml"

MINIMAL_BOARD = """# Radar — idea board

## Proposed

- **good row** *(S; on-box)* — does a thing. **Acceptance: it works.**
- **ledger row** — **SHIPPED 2026-01-01, see Done** (`abc1234`).
- **skipped row** — **SKIPPED 2026-01-02: no longer wanted.**

## In progress

*(none)*

## Done

*(none)*

## Skipped

*(none)*

## Run log

*(empty)*
"""


def run_checker(board_path):
    return subprocess.run(
        [sys.executable, str(CHECKER), str(board_path)],
        capture_output=True,
        text=True,
    )


def write_board(tmp_path, text):
    board = tmp_path / "IDEAS.md"
    board.write_text(text, encoding="utf-8")
    return board


def test_real_board_passes_clean():
    """The current board passes: measured counts, exit 0."""
    proc = run_checker(BOARD)
    assert proc.returncode == 0, proc.stdout
    assert "OK — board lint:" in proc.stdout
    assert "actionable Proposed row(s) checked" in proc.stdout
    # the two genuinely open rows are the ones counted actionable
    n_actionable = int(proc.stdout.split("board lint: ")[1].split(" actionable")[0])
    assert n_actionable >= 1


def test_planted_row_missing_both_fails_naming_row_and_parts(tmp_path):
    board = write_board(
        tmp_path, MINIMAL_BOARD.replace(
            "## Proposed\n",
            "## Proposed\n\n- **planted bad row** — does a thing with no meta.\n", 1))
    proc = run_checker(board)
    assert proc.returncode == 1
    assert 'row "planted bad row"' in proc.stdout
    assert "effort tag" in proc.stdout
    assert "acceptance clause" in proc.stdout


def test_planted_row_missing_effort_tag_only(tmp_path):
    board = write_board(
        tmp_path, MINIMAL_BOARD.replace(
            "## Proposed\n",
            "## Proposed\n\n- **tagless row** — has an acceptance, no tag. "
            "**Acceptance: fine.**\n", 1))
    proc = run_checker(board)
    assert proc.returncode == 1
    assert 'row "tagless row" missing effort tag' in proc.stdout
    assert "acceptance clause" not in proc.stdout


def test_planted_row_missing_acceptance_only(tmp_path):
    board = write_board(
        tmp_path, MINIMAL_BOARD.replace(
            "## Proposed\n",
            "## Proposed\n\n- **unaccepted row** *(S; on-box)* — tag but "
            "no acceptance clause anywhere.\n", 1))
    proc = run_checker(board)
    assert proc.returncode == 1
    assert 'row "unaccepted row" missing acceptance clause' in proc.stdout
    assert "effort tag" not in proc.stdout


def test_fault_names_file_and_row_line(tmp_path):
    board = write_board(
        tmp_path, MINIMAL_BOARD.replace(
            "## Proposed\n",
            "## Proposed\n\n- **located row** — no meta at all.\n", 1))
    proc = run_checker(board)
    assert proc.returncode == 1
    # the fault names the fixture file and the planted row's own line (5:
    # header, blank, ## Proposed, blank, planted row)
    assert f"{board}:5" in proc.stdout


def test_ledger_rows_exempt(tmp_path):
    """SHIPPED/SKIPPED-stamped rows are history: never faulted."""
    board = write_board(tmp_path, MINIMAL_BOARD)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    assert "ledger row(s) exempt" in proc.stdout
    assert "2 ledger" in proc.stdout  # the shipped + skipped fixture rows


def test_wrapped_ledger_pointer_exempt(tmp_path):
    """The real board wraps 'see Done' across lines — same phrase.

    (This exact spelling in the changedetection.io row faulted the
    first live run; the board's line wrapping is part of its schema.)
    """
    text = MINIMAL_BOARD.replace(
        "- **skipped row** — **SKIPPED 2026-01-02: no longer wanted.**",
        "- **wrapped row** — shipped same day, see\n"
        "  Done. **S** <https://example.invalid>").replace(
        "- **ledger row** — **SHIPPED 2026-01-01, see Done** (`abc1234`).",
        "- **wrapped log row** — reported, see run\n  log for details.")
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    # wrapped row + wrapped log row are ledger history; the good row
    # stays actionable (the shipped fixture row was replaced above)
    assert "2 ledger" in proc.stdout
    assert "1 actionable" in proc.stdout


def test_effort_tag_spellings_accepted(tmp_path):
    """Both established spellings: **S** and *(M; …)*."""
    text = MINIMAL_BOARD.replace(
        "- **good row** *(S; on-box)*",
        "- **bold tag row** **M** — tagged in bold. "
        "**Acceptance: works.**\n- **paren tag row** *(L; needs hardware)* "
        "— tagged in the meta parens. **Acceptance: works.**")
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    # the good row was replaced by the two spellings under test
    assert "2 actionable" in proc.stdout


def test_checker_is_readonly_source():
    """The checker never writes: no write-mode opens, no removing calls."""
    src = CHECKER.read_text(encoding="utf-8")
    for banned in ("os.remove", "unlink", "truncate", "write_text",
                   "rmtree", "rename(", "'w'", '"w"', "'a'", '"a"',
                   "shutil", "subprocess"):
        assert banned not in src, f"checker source must not contain {banned!r}"


def test_board_unmodified_by_run(tmp_path):
    """A run over a copy leaves the bytes identical."""
    board = write_board(
        tmp_path, MINIMAL_BOARD.replace(
            "## Proposed\n",
            "## Proposed\n\n- **bad** — planted malformed, no meta.\n", 1))
    before = board.read_bytes()
    proc = run_checker(board)
    assert proc.returncode == 1  # the planted row faults
    assert board.read_bytes() == before


def test_ci_wiring_board_lint_step_and_branch_filter():
    """CI runs the board lint, and runs at all on the default branch."""
    ci = CI.read_text(encoding="utf-8")
    assert "Board lint" in ci
    assert "tools/check_board.py" in ci
    assert "IDEAS.md" in ci
    # the workflow triggered on main only while the default branch is
    # master — radar CI had never run before this fix
    assert "branches: [main, master]" in ci


def test_missing_board_is_structural(tmp_path):
    proc = run_checker(tmp_path / "nope.md")
    assert proc.returncode == 2
    assert "cannot read" in proc.stdout
    assert "nope.md" in proc.stdout


def test_board_without_proposed_section_is_structural(tmp_path):
    board = write_board(tmp_path, "# Radar\n\n## Run log\n\n- 2026-01-01 — nothing.\n")
    proc = run_checker(board)
    assert proc.returncode == 2
    assert "no '## Proposed' section" in proc.stdout
