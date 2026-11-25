"""Tests for tools/check_board.py — the IDEAS.md board lint.

Acceptance (board row, radar — lint the board in CI):
- a planted malformed row fails naming the row and the missing part;
- the current board passes clean;
- the checker never edits the board (read-only, asserted on source and
  by bytes-identical runs);
- the board-lint step is wired into this repo's CI — including the
  branch filter fix (the workflow triggered on main only while the
  default branch is master, so radar CI had never run).

Ledger-pointer acceptance (board row, radar — lint the ledger's
pointers, 2026-11-12):
- a SHIPPED stamp with no same-title Done row fails naming the row;
- a commit ref that does not resolve fails naming the row, the sha and
  the repo;
- a ref bound to a repo the checker was not handed is reported, not
  faulted; the real board passes clean; git is only asked cat-file.
"""

import subprocess
import sys
from pathlib import Path

import pytest

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

- **ledger row** — done 2026-01-01 (shipped in `abc1234`; same title,
  so the SHIPPED stamp resolves).

## Skipped

*(none)*

## Run log

*(empty)*
"""


def run_checker(board_path, *extra):
    return subprocess.run(
        [sys.executable, str(CHECKER), str(board_path), *extra],
        capture_output=True,
        text=True,
        check=False,
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
                   "shutil", "shell=True"):
        assert banned not in src, f"checker source must not contain {banned!r}"
    # subprocess is allowed for exactly one read-only call site — does this
    # commit exist, and what kind of checkout is this? Every invocation
    # names git, and the site asserts its own verb against an allow-list.
    assert "subprocess" in src  # the git reader
    subprocess_calls = [
        block for block in src.split("subprocess.")[1:]
        if block.lstrip().startswith("run(")
    ]
    assert len(subprocess_calls) == 1, "one git call site, not a toolbox"
    call = subprocess_calls[0]
    assert '["git", "-C"' in call
    assert 'GIT_READ_VERBS = ("cat-file", "rev-parse")' in src
    assert "args[0] in GIT_READ_VERBS" in src
    for verb in ("commit", "add", "push", "reset", "checkout", "clean",
                 "gc", "prune", "update-ref", "fetch"):
        assert f'"{verb}"' not in call, f"git call site must stay read-only ({verb})"


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


# --- ledger pointers (2026-11-12) ---------------------------------------
#
# Acceptance: the current board passes clean; three planted violations
# each fail naming the row and the broken pointer.


def make_git_repo(path):
    """A one-commit repo, returning (path, sha)."""
    path.mkdir()
    env = {"GIT_AUTHOR_NAME": "radar", "GIT_AUTHOR_EMAIL": "radar@example.invalid",
           "GIT_COMMITTER_NAME": "radar", "GIT_COMMITTER_EMAIL": "radar@example.invalid",
           "PATH": "/usr/bin:/bin", "HOME": str(path)}
    def git(*args):
        return subprocess.run(["git", "-C", str(path), *args], check=True,
                              capture_output=True, text=True, env=env)
    git("init", "-q")
    # the seed names the directory: two fixtures made in the same second
    # with identical content and identity would otherwise be the SAME
    # commit, and a cross-repo test would pass without resolving anything
    (path / "seed.txt").write_text(f"seed {path.name}\n", encoding="utf-8")
    git("add", "seed.txt")
    git("commit", "-q", "-m", "seed")
    return path, git("rev-parse", "HEAD").stdout.strip()


def commit_file(path, name, message):
    """Add and commit one file in a fixture repo (returns the new sha)."""
    env = {"GIT_AUTHOR_NAME": "radar", "GIT_AUTHOR_EMAIL": "radar@example.invalid",
           "GIT_COMMITTER_NAME": "radar", "GIT_COMMITTER_EMAIL": "radar@example.invalid",
           "PATH": "/usr/bin:/bin", "HOME": str(path)}
    (path / name).write_text(name + "\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", name], check=True,
                   capture_output=True, env=env)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", message],
                   check=True, capture_output=True, env=env)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def test_planted_dangling_shipped_pointer_fails(tmp_path):
    """Violation 1: a SHIPPED stamp pointing at no Done row."""
    text = MINIMAL_BOARD.replace(
        "- **ledger row** — **SHIPPED 2026-01-01, see Done** (`abc1234`).",
        "- **ghost row** — **SHIPPED 2026-01-01, see Done** (`abc1234`).")
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 1, proc.stdout
    assert 'row "ghost row" stamped SHIPPED but no Done row carries that title' in proc.stdout
    assert f"{board}:6" in proc.stdout  # the row's own line


def test_shipped_pointer_needs_the_same_title_not_a_near_miss(tmp_path):
    """Violation 2: a Done row exists, but under another title."""
    text = MINIMAL_BOARD.replace(
        "- **ledger row** — done 2026-01-01 (shipped in `abc1234`; same title,",
        "- **ledger row, reworded** — done 2026-01-01 (shipped in `abc1234`; same title,")
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 1, proc.stdout
    assert 'row "ledger row" stamped SHIPPED but no Done row carries that title' in proc.stdout
    # the near-miss Done row is itself clean history, so only one fault
    assert "1 fault(s)" in proc.stdout


def test_planted_unresolvable_commit_fails_naming_sha_and_repo(tmp_path):
    """Violation 3: a commit ref that is not in the repo's history."""
    repo, _sha = make_git_repo(tmp_path / "farm")
    text = MINIMAL_BOARD.replace(
        "- **ledger row** — done 2026-01-01 (shipped in `abc1234`; same title,",
        "- **radar — planted pointer** — done 2026-01-01 (shipped in `0abc123`; new title,")
    text = text.replace(
        "- **ledger row** — **SHIPPED 2026-01-01, see Done** (`abc1234`).",
        "- **radar — planted pointer** — **SHIPPED 2026-01-01, see Done** (`0abc123`).")
    board = write_board(tmp_path, text)
    proc = run_checker(board, "--repo", f"radar={repo}")
    assert proc.returncode == 1, proc.stdout
    assert 'row "radar — planted pointer" cites `0abc123`, which is not in radar history' in proc.stdout


def test_resolvable_commit_passes_and_is_counted(tmp_path):
    """Control: the same row with a real sha resolves clean."""
    repo, sha = make_git_repo(tmp_path / "farm")
    text = MINIMAL_BOARD.replace("`abc1234`", f"`{sha}`")
    text = text.replace(
        "- **ledger row** — done 2026-01-01 (shipped in",
        "- **radar — real pointer** — done 2026-01-01 (shipped in")
    text = text.replace(
        "- **ledger row** — **SHIPPED 2026-01-01, see Done**",
        "- **radar — real pointer** — **SHIPPED 2026-01-01, see Done**")
    board = write_board(tmp_path, text)
    proc = run_checker(board, "--repo", f"radar={repo}")
    assert proc.returncode == 0, proc.stdout
    assert "2 commit ref(s) resolved in radar" in proc.stdout
    assert "0 unverified" in proc.stdout


def test_ref_bound_to_an_unsupplied_repo_is_unverified_not_faulted(tmp_path):
    """The checker cannot see a repo it was not handed: report, don't fault."""
    # rename the shipped row and its Done twin together, then plant a
    # ref to a repo the checker was not handed
    text = MINIMAL_BOARD.replace("ledger row", "cluster — planted pointer")
    text = text.replace("abc1234", "0abc123")
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    # the ref rides in both the stamp row and its Done twin
    assert "2 unverified (repo not supplied)" in proc.stdout
    assert "0 commit ref(s) resolved" in proc.stdout


def test_ref_binding_follows_the_title_prefix(tmp_path):
    """A bogus cluster ref stays unverified while a bogus radar ref faults."""
    repo, sha = make_git_repo(tmp_path / "farm")
    text = MINIMAL_BOARD.replace("ledger row", "cluster — other repo")
    text = text.replace("abc1234", "0abc123")
    board = write_board(tmp_path, text)
    proc = run_checker(board, "--repo", f"radar={repo}")
    assert proc.returncode == 0, proc.stdout  # cluster ref not checked against radar
    assert "2 unverified" in proc.stdout


def test_run_leaves_the_git_repo_untouched(tmp_path):
    """git is asked cat-file only: HEAD and the worktree do not move."""
    repo, sha = make_git_repo(tmp_path / "farm")
    text = MINIMAL_BOARD.replace("`abc1234`", f"`{sha}`").replace(
        "- **ledger row** — done 2026-01-01 (shipped in",
        "- **radar — real pointer** — done 2026-01-01 (shipped in")
    text = text.replace(
        "- **ledger row** — **SHIPPED 2026-01-01, see Done**",
        "- **radar — real pointer** — **SHIPPED 2026-01-01, see Done**")
    board = write_board(tmp_path, text)
    head_before = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                 capture_output=True, text=True, check=True).stdout
    before = sorted(p.name for p in repo.iterdir())
    proc = run_checker(board, "--repo", f"radar={repo}")
    assert proc.returncode == 0, proc.stdout
    head_after = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout
    assert head_after == head_before
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    assert status == ""
    assert sorted(p.name for p in repo.iterdir()) == before


def test_real_board_pointer_counts_are_reported():
    """The real board is clean and the OK line carries the new counts."""
    proc = run_checker(BOARD)
    assert proc.returncode == 0, proc.stdout
    assert "SHIPPED marker(s) matched to Done" in proc.stdout
    assert "commit ref(s) resolved in radar" in proc.stdout
    n_shipped = int(proc.stdout.split("exempt, ")[1].split(" SHIPPED")[0])
    assert n_shipped >= 1


def test_ci_checkout_fetches_full_history():
    """Commit refs resolve only if CI has the history to resolve them."""
    ci = CI.read_text(encoding="utf-8")
    assert "fetch-depth: 0" in ci


# --- deployment scope (2026-11-15) --------------------------------------
#
# Acceptance (board row, radar — make the board refuse a row it can never
# ship): a planted Proposed row naming twitter-launch fails with the repo
# named; the board as it stands exits 0; Done and Skipped parse untouched.

OUT_OF_SCOPE_ROW = (
    "- **twitter-launch — planted out-of-scope row** *(S; on-box)* — does "
    "a thing. **Acceptance: it works.**\n"
)


def board_with_proposed_row(tmp_path, row):
    text = MINIMAL_BOARD.replace("## Proposed\n", "## Proposed\n\n" + row, 1)
    return write_board(tmp_path, text)


def test_planted_out_of_scope_row_fails_naming_the_project(tmp_path):
    """The acceptance row: a Proposed twitter-launch row is refused."""
    board = board_with_proposed_row(tmp_path, OUT_OF_SCOPE_ROW)
    proc = run_checker(board)
    assert proc.returncode == 1, proc.stdout
    assert 'row "twitter-launch — planted out-of-scope row"' in proc.stdout
    assert "out-of-scope project twitter-launch" in proc.stdout
    assert "owner deployment scope, 2026-11-02" in proc.stdout
    # the row is otherwise well-formed: scope is the only fault
    assert "1 fault(s)" in proc.stdout
    assert "effort tag" not in proc.stdout
    assert "acceptance clause" not in proc.stdout
    assert f"{board}:5" in proc.stdout


def test_every_retired_prefix_is_refused(tmp_path):
    """Old-deployment repos and Train/cs2-train are all out of scope."""
    cases = {
        "forex-copybot": "forex-copybot",
        "copybot": "forex-copybot",
        "maritime-dashboard": "maritime-dashboard",
        "project-hub": "project-hub",
        "ais_analysis": "ais_analysis",
        "camoufox-setup": "camoufox-setup",
        "Train:": "Train (cs2-train)",
        "cs2-train": "Train (cs2-train)",
    }
    for prefix, reported in cases.items():
        separator = " " if prefix.endswith(":") else " — "
        row = (
            f"- **{prefix}{separator}planted {prefix} row** *(S; on-box)* — "
            "does a thing. **Acceptance: it works.**\n"
        )
        board = board_with_proposed_row(tmp_path, row)
        proc = run_checker(board)
        assert proc.returncode == 1, f"{prefix}: {proc.stdout}"
        assert f"out-of-scope project {reported}" in proc.stdout, prefix


def test_in_scope_prefixes_still_pass(tmp_path):
    """Control: every current-deployment project prefix stays clean."""
    rows = "".join(
        f"- **{prefix} — planted {prefix} row** *(S; on-box)* — does a "
        "thing. **Acceptance: it works.**\n"
        for prefix in ("radar", "personal-website", "cluster", "pi-cicd",
                       "switch-l4t-gpu")
    )
    board = board_with_proposed_row(tmp_path, rows)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    # the fixture's own good row is actionable too
    assert "6 actionable" in proc.stdout
    assert "0 out-of-scope" in proc.stdout


def test_out_of_scope_ledger_rows_are_exempt(tmp_path):
    """History naming a retired project is not a fault (Skipped/Done)."""
    text = MINIMAL_BOARD.replace(
        "- **skipped row** — **SKIPPED 2026-01-02: no longer wanted.**",
        "- **twitter-launch — retired row** — **SKIPPED 2026-01-02: out of "
        "scope (owner deployment directive); see Notes.**", 1)
    text = text.replace(
        "**ledger row** — **SHIPPED 2026-01-01, see Done**",
        "**forex-copybot — retired stamped row** — **SHIPPED 2026-01-01, "
        "see Done**", 1)
    text = text.replace(
        "- **ledger row** — done 2026-01-01 (shipped in `abc1234`; same title,",
        "- **forex-copybot — retired stamped row** — done 2026-01-01 "
        "(shipped in `abc1234`; same title,", 1)
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout
    assert "0 out-of-scope" in proc.stdout


def test_out_of_scope_check_reads_the_prefix_not_the_prose(tmp_path):
    """An in-scope row may mention a retired project in its prose."""
    row = (
        "- **radar — planted prose row** *(S; on-box)* — unlike\n"
        "  twitter-launch and forex-copybot, this repo is in scope.\n"
        "  **Acceptance: it works.**\n"
    )
    board = board_with_proposed_row(tmp_path, row)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout


def test_real_board_counts_zero_out_of_scope_rows():
    """The board as it stands is fully inside the deployment scope."""
    proc = run_checker(BOARD)
    assert proc.returncode == 0, proc.stdout
    assert "0 out-of-scope Proposed row(s)" in proc.stdout


def test_real_board_skipped_section_is_not_judged(tmp_path):
    """The real Skipped history names retired projects — still clean."""
    text = BOARD.read_text(encoding="utf-8")
    assert "**SKIPPED 2026-11-02: out of scope" in text  # the history is there
    board = write_board(tmp_path, text)
    proc = run_checker(board)
    assert proc.returncode == 0, proc.stdout


# --- a ref's repo is the one named beside it (2026-11-25) ---------------
#
# Acceptance (board row, radar — give the ledger's unresolvable refs a
# verdict): `check_board.py --repo` for all five owned checkouts exits 0
# with the resolved count named, or every remaining unverified ref carries
# a written reason. The row's premise was measured: the 28 faults were 21
# refs lost to a shallow pi-cicd checkout and 3 shas mis-bound to the
# title's prefix even though the row names their repo in the same breath.

DONE_BOARD = """# Radar — idea board

## Proposed

*(none)*

## In progress

*(none)*

## Done

- **{title}** — done 2026-01-01 ({body})

## Skipped

*(none)*

## Run log

*(empty)*
"""


def done_board(tmp_path, title, body):
    return write_board(tmp_path, DONE_BOARD.format(title=title, body=body))


def test_cross_repo_refs_bind_to_the_repo_named_beside_them(tmp_path):
    """A cluster row citing pi-cicd shas resolves each in its own repo."""
    cluster, sha_a = make_git_repo(tmp_path / "farm-a")
    piped, sha_b = make_git_repo(tmp_path / "farm-b")
    assert sha_a != sha_b  # two fixtures, two commits — not one sha twice
    board = done_board(
        tmp_path,
        "cluster — planted cross repo",
        f"shipped in cluster-prototype `{sha_a}` + pi-cicd `{sha_b}`:",
    )
    proc = run_checker(
        board,
        "--repo", f"cluster-prototype={cluster}",
        "--repo", f"pi-cicd={piped}",
    )
    assert proc.returncode == 0, proc.stdout
    assert "2 commit ref(s) resolved in cluster-prototype, pi-cicd, radar" in proc.stdout
    assert "0 unverified" in proc.stdout


def test_repeated_ref_keeps_the_binding_it_got_in_the_row(tmp_path):
    """A sha cited again later in the row stays with the repo it came from.

    The board names a commit once and then refers back to it in prose,
    often on a line with no repo name beside it; the old prefix-only
    binding sent that second mention to the title's repo and faulted.
    """
    cluster, sha_a = make_git_repo(tmp_path / "farm-a")
    piped, sha_b = make_git_repo(tmp_path / "farm-b")
    assert sha_a != sha_b
    board = done_board(
        tmp_path,
        "cluster — planted repeat",
        f"shipped in cluster-prototype `{sha_a}` + pi-cicd `{sha_b}`:\n"
        f"    CI runs for the second half (`{sha_b}`) were green.",
    )
    proc = run_checker(
        board,
        "--repo", f"cluster-prototype={cluster}",
        "--repo", f"pi-cicd={piped}",
    )
    assert proc.returncode == 0, proc.stdout
    assert "3 commit ref(s) resolved" in proc.stdout
    assert "not in cluster-prototype history" not in proc.stdout


def test_a_distant_repo_mention_does_not_steal_a_ref(tmp_path):
    """Only a name sitting beside the ref binds it; prose does not."""
    repo, _sha = make_git_repo(tmp_path / "farm")
    board = done_board(
        tmp_path,
        "radar — planted distant mention",
        "unlike the cluster work generally, this pointer `0abc123` is ours.",
    )
    proc = run_checker(board, "--repo", f"radar={repo}")
    assert proc.returncode == 1, proc.stdout
    assert "cites `0abc123`, which is not in radar history" in proc.stdout


def test_shallow_checkout_is_unverified_not_faulted(tmp_path):
    """A shallow clone cannot prove a commit absent, so it says so."""
    full, parent = make_git_repo(tmp_path / "farm")
    commit_file(full, "second.txt", "second")
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{full}", str(shallow)],
                   check=True, capture_output=True)
    assert parent not in subprocess.run(
        ["git", "-C", str(shallow), "rev-list", "--all"], check=True,
        capture_output=True, text=True).stdout  # the parent really is missing
    board = done_board(tmp_path, "radar — planted shallow",
                       f"shipped in `{parent}`.")
    proc = run_checker(board, "--repo", f"radar={shallow}", "--explain")
    assert proc.returncode == 0, proc.stdout
    assert "1 unverified (repo is shallow)" in proc.stdout
    assert f"ref `{parent}` (bound to radar): repo is shallow" in proc.stdout
    # control 1: the same sha against the full checkout resolves, so the
    # sha is real and the shallow verdict is about what the clone holds
    full_proc = run_checker(board, "--repo", f"radar={full}")
    assert full_proc.returncode == 0, full_proc.stdout
    assert "1 commit ref(s) resolved in radar" in full_proc.stdout
    # control 2: a sha that is nowhere still faults against the full repo,
    # so the fault path above the shallow branch is alive
    bogus = done_board(tmp_path, "radar — planted bogus", "shipped in `0abc1234`.")
    bogus_proc = run_checker(bogus, "--repo", f"radar={full}")
    assert bogus_proc.returncode == 1, bogus_proc.stdout
    assert "`0abc1234`, which is not in radar history" in bogus_proc.stdout


def test_unusable_repo_path_is_unverified_and_named(tmp_path):
    """A --repo path that is not a checkout is a reason, not 40 faults."""
    board = done_board(tmp_path, "radar — planted path", "shipped in `abc1234`.")
    proc = run_checker(board, "--repo", f"radar={tmp_path / 'nope'}", "--explain")
    assert proc.returncode == 0, proc.stdout
    assert "1 unverified (repo path is not a usable checkout)" in proc.stdout
    assert "ref `abc1234` (bound to radar): repo path is not a usable checkout" in proc.stdout


def test_explain_names_every_unverified_ref_and_is_silent_when_clean(tmp_path):
    """Each unverified ref gets a line with its repo and reason."""
    board = done_board(tmp_path, "cluster — planted explain",
                       "shipped in cluster-prototype `abc1234`.")
    proc = run_checker(board, "--explain")
    assert proc.returncode == 0, proc.stdout
    assert f"UNVERIFIED {board}:13 — ref `abc1234` (bound to cluster-prototype): repo not supplied" in proc.stdout
    cluster, sha = make_git_repo(tmp_path / "farm")
    clean = done_board(tmp_path, "cluster — planted explained clean",
                       f"shipped in cluster-prototype `{sha}`.")
    proc = run_checker(clean, "--repo", f"cluster-prototype={cluster}", "--explain")
    assert proc.returncode == 0, proc.stdout
    assert "UNVERIFIED" not in proc.stdout


OWNED_CHECKOUTS = {
    "radar": REPO,
    "pkia.github.io": Path("/home/ev/personal-website"),
    "pi-cicd": Path("/home/ev/pi-cicd"),
    "cluster-prototype": Path("/home/ev/cluster-prototype"),
    "switch-l4t-gpu": Path("/home/ev/switch-l4t-gpu-clone"),
}


def test_real_board_with_every_owned_checkout_exits_zero():
    """The row's acceptance: five checkouts supplied, resolved count named.

    CI only has radar's own checkout, so this runs on the box (and skips
    where the others are absent rather than pretending they are clean).
    """
    missing = [n for n, p in OWNED_CHECKOUTS.items() if not (p / ".git").exists()]
    if missing:
        pytest.skip(f"not checked out here: {', '.join(missing)}")
    extra = []
    for name, path in OWNED_CHECKOUTS.items():
        if name != "radar":
            extra += ["--repo", f"{name}={path}"]
    proc = run_checker(BOARD, *extra)
    assert proc.returncode == 0, proc.stdout
    assert "0 fault(s)" not in proc.stdout
    resolved = proc.stdout.split(" commit ref(s) resolved in ")[0].rsplit(", ", 1)[1]
    assert int(resolved) > 0
    assert "unverified (" in proc.stdout  # the remainder carries reasons
