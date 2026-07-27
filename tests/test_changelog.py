import subprocess
from pathlib import Path

import pytest

from changeloggen.generator import render_full_changelog
from changeloggen.git import get_commits, list_tags_chronological
from changeloggen.parser import parse_commit


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(f"DEBUG $ {' '.join(cmd)} -> rc={result.returncode} out={result.stdout!r} err={result.stderr!r}")
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _run(["git", "init", "-q"], tmp_path)
    _run(["git", "config", "user.email", "a@a.com"], tmp_path)
    _run(["git", "config", "user.name", "Alice"], tmp_path)

    (tmp_path / "a.txt").write_text("1\n")
    _run(["git", "add", "-A"], tmp_path)
    _run(["git", "commit", "-m", "feat(auth): add login flow", "-q"], tmp_path)

    (tmp_path / "a.txt").write_text("2\n")
    _run(["git", "add", "-A"], tmp_path)
    _run(["git", "commit", "-m", "fix: crash on empty input", "-q"], tmp_path)

    (tmp_path / "a.txt").write_text("3\n")
    _run(["git", "add", "-A"], tmp_path)
    _run(["git", "commit", "-m", "feat!: change public API\n\nBREAKING CHANGE: renamed foo to bar", "-q"], tmp_path)
    _run(["git", "tag", "v0.1.0"], tmp_path)

    (tmp_path / "a.txt").write_text("4\n")
    _run(["git", "add", "-A"], tmp_path)
    _run(["git", "commit", "-m", "docs: update readme", "-q"], tmp_path)

    return tmp_path


def test_parses_conventional_types(repo: Path) -> None:
    commits = get_commits(repo, None)
    parsed = [parse_commit(c) for c in commits]
    types = {p.type for p in parsed}
    assert {"feat", "fix", "docs"} <= types


def test_detects_breaking_change(repo: Path) -> None:
    commits = get_commits(repo, None)
    parsed = [parse_commit(c) for c in commits]
    breaking = [p for p in parsed if p.breaking]
    assert len(breaking) == 1
    assert "change public API" in breaking[0].description


def test_full_changelog_includes_all_tags(repo: Path) -> None:
    debug = subprocess.run(["git", "tag", "--list"], cwd=repo, capture_output=True, text=True)
    print("DEBUG tag --list stdout:", repr(debug.stdout))
    print("DEBUG tag --list stderr:", repr(debug.stderr))
    print("DEBUG tag --list returncode:", debug.returncode)
    debug2 = subprocess.run(["git", "log", "--oneline", "--all", "--decorate"], cwd=repo, capture_output=True, text=True)
    print("DEBUG log:", debug2.stdout)

    tags = list_tags_chronological(repo)
    assert len(tags) == 1

    unreleased = get_commits(repo, f"{tags[-1].name}..HEAD")
    tagged = get_commits(repo, tags[0].name)

    sections = [
        ("Unreleased", None, [parse_commit(c) for c in unreleased]),
        (tags[0].name, "2026-01-01", [parse_commit(c) for c in tagged]),
    ]
    changelog = render_full_changelog(sections, None)

    assert "## Unreleased" in changelog
    assert "## v0.1.0" in changelog
    assert "### Breaking Changes" in changelog
    assert "### Features" in changelog
    assert "### Bug Fixes" in changelog
    assert "### Documentation" in changelog
