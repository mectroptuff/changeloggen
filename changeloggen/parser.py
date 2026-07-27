"""Conventional Commits parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .git import Commit

_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z]+)(\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$"
)

TYPE_LABELS: dict[str, str] = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "docs": "Documentation",
    "test": "Tests",
    "build": "Build System",
    "ci": "Continuous Integration",
    "chore": "Chores",
    "style": "Style",
    "revert": "Reverts",
}

# Order in which sections are rendered.
TYPE_ORDER = list(TYPE_LABELS.keys())

OTHER_LABEL = "Other Changes"


@dataclass
class ParsedCommit:
    commit: Commit
    type: str | None
    scope: str | None
    breaking: bool
    description: str


def parse_commit(commit: Commit) -> ParsedCommit:
    match = _PATTERN.match(commit.subject.strip())
    breaking = bool(commit.body and "BREAKING CHANGE" in commit.body.upper())

    if not match:
        return ParsedCommit(commit=commit, type=None, scope=None, breaking=breaking, description=commit.subject.strip())

    commit_type = match.group("type").lower()
    scope = match.group("scope")
    breaking = breaking or bool(match.group("breaking"))
    description = match.group("description").strip()

    return ParsedCommit(commit=commit, type=commit_type, scope=scope, breaking=breaking, description=description)


def group_by_type(parsed_commits: list[ParsedCommit]) -> dict[str, list[ParsedCommit]]:
    groups: dict[str, list[ParsedCommit]] = {}
    for parsed in parsed_commits:
        label = TYPE_LABELS.get(parsed.type, OTHER_LABEL) if parsed.type else OTHER_LABEL
        groups.setdefault(label, []).append(parsed)
    return groups
