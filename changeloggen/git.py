"""Thin wrappers around the git CLI — no third-party git library needed."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

_FIELD_SEP = "\x1f"
_RECORD_SEP = "\x1e"

# `git`'s `%aI`/`%(creatordate:iso-strict)` produce strict ISO-8601, either
# with a numeric UTC offset ("2026-07-27T15:36:20+00:00") or, on newer git
# versions, a trailing "Z" for UTC ("2026-07-27T15:36:20Z"). We parse it
# manually instead of relying on `datetime.fromisoformat`, whose parsing
# rules for this also differ meaningfully between Python 3.9/3.10 and 3.11+.
_GIT_ISO_DATE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?:Z|(?P<offset_sign>[+-])(?P<offset_hour>\d{2}):(?P<offset_minute>\d{2}))$"
)


def parse_git_date(value: str) -> datetime | None:
    match = _GIT_ISO_DATE.match(value.strip())
    if not match:
        return None

    parts = match.groupdict()
    if parts["offset_sign"] is None:
        offset_minutes = 0
    else:
        offset_minutes = int(parts["offset_hour"]) * 60 + int(parts["offset_minute"])
        if parts["offset_sign"] == "-":
            offset_minutes = -offset_minutes

    return datetime(
        int(parts["year"]), int(parts["month"]), int(parts["day"]),
        int(parts["hour"]), int(parts["minute"]), int(parts["second"]),
        tzinfo=timezone(timedelta(minutes=offset_minutes)),
    )


@dataclass
class Commit:
    hash: str
    subject: str
    body: str
    author: str
    date: datetime


@dataclass
class Tag:
    name: str
    date: datetime


def _run(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def list_tags_chronological(root: Path) -> list[Tag]:
    """List tags in chronological order.

    Uses each tag's target commit date (via `git log`) rather than
    `%(creatordate)` from `for-each-ref`, because lightweight tags don't
    always populate that field consistently across git versions/platforms.
    """
    names_output = _run(root, ["tag", "--list"])
    tags: list[Tag] = []
    for name in names_output.splitlines():
        name = name.strip()
        if not name:
            continue
        date_output = _run(root, ["log", "-1", "--format=%aI", name]).strip()
        date = parse_git_date(date_output)
        if date is None:
            continue
        tags.append(Tag(name=name, date=date))

    tags.sort(key=lambda tag: tag.date)
    return tags


def get_commits(root: Path, rev_range: str | None) -> list[Commit]:
    format_str = _FIELD_SEP.join(["%H", "%s", "%b", "%an", "%aI"]) + _RECORD_SEP
    args = ["log", f"--pretty=format:{format_str}"]
    if rev_range:
        args.append(rev_range)

    output = _run(root, args)
    if not output:
        return []

    commits: list[Commit] = []
    for record in output.split(_RECORD_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        parts = record.split(_FIELD_SEP)
        if len(parts) < 5:
            continue
        commit_hash, subject, body, author, date_str = parts[:5]
        date = parse_git_date(date_str) or datetime.now(timezone.utc)
        commits.append(Commit(hash=commit_hash, subject=subject, body=body, author=author, date=date))

    return commits


def current_repo_url(root: Path) -> str | None:
    output = _run(root, ["config", "--get", "remote.origin.url"])
    url = output.strip()
    if not url:
        return None
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url[len("git@github.com:"):]
    if url.endswith(".git"):
        url = url[: -len(".git")]
    return url
