from pathlib import Path


def _section(md_text: str, start_header: str, end_header: str) -> str:
    try:
        return md_text.split(start_header, 1)[1].split(end_header, 1)[0]
    except IndexError:
        return ""


def test_in_progress_at_most_one():
    text = Path("IDEAS.md").read_text()
    section = _section(text, "## In progress", "## Done")
    items = [l for l in section.splitlines() if l.strip().startswith("-")]
    assert len(items) <= 1, f"Expected at most one In progress item, found {len(items)}"


def test_proposed_non_empty():
    text = Path("IDEAS.md").read_text()
    section = _section(text, "## Proposed", "## In progress")
    items = [l for l in section.splitlines() if l.strip().startswith("-")]
    assert len(items) >= 1, "Proposed section should contain at least one idea"
