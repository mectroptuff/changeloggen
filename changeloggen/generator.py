"""Renders parsed commits into a CHANGELOG.md-style markdown document."""

from __future__ import annotations

from .parser import OTHER_LABEL, TYPE_LABELS, ParsedCommit, group_by_type

_SECTION_ORDER = list(TYPE_LABELS.values()) + [OTHER_LABEL]


def render_section(title: str, parsed_commits: list[ParsedCommit], repo_url: str | None) -> list[str]:
    lines = [f"### {title}", ""]
    for parsed in parsed_commits:
        scope_prefix = f"**{parsed.scope}:** " if parsed.scope else ""
        short_hash = parsed.commit.hash[:7]
        commit_ref = f"[`{short_hash}`]({repo_url}/commit/{parsed.commit.hash})" if repo_url else f"`{short_hash}`"
        lines.append(f"- {scope_prefix}{parsed.description} ({commit_ref})")
    lines.append("")
    return lines


def render_changelog_section(
    version_title: str,
    date_str: str | None,
    parsed_commits: list[ParsedCommit],
    repo_url: str | None,
) -> list[str]:
    lines: list[str] = []
    heading = f"## {version_title}" + (f" - {date_str}" if date_str else "")
    lines.append(heading)
    lines.append("")

    breaking = [p for p in parsed_commits if p.breaking]
    if breaking:
        lines.append("### Breaking Changes")
        lines.append("")
        for parsed in breaking:
            short_hash = parsed.commit.hash[:7]
            commit_ref = f"[`{short_hash}`]({repo_url}/commit/{parsed.commit.hash})" if repo_url else f"`{short_hash}`"
            lines.append(f"- {parsed.description} ({commit_ref})")
        lines.append("")

    groups = group_by_type(parsed_commits)
    for label in _SECTION_ORDER:
        commits_in_group = groups.get(label)
        if not commits_in_group:
            continue
        lines.extend(render_section(label, commits_in_group, repo_url))

    return lines


def render_full_changelog(sections: list[tuple[str, str | None, list[ParsedCommit]]], repo_url: str | None) -> str:
    lines = ["# Changelog", ""]
    for version_title, date_str, parsed_commits in sections:
        if not parsed_commits:
            continue
        lines.extend(render_changelog_section(version_title, date_str, parsed_commits, repo_url))
    return "\n".join(lines).rstrip() + "\n"
