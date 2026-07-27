"""Command-line entry point for changeloggen."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .generator import render_full_changelog
from .git import current_repo_url, get_commits, list_tags_chronological
from .parser import parse_commit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="changeloggen",
        description="Generate a CHANGELOG.md from Conventional Commits in your git history.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to the repo (default: current directory).")
    parser.add_argument("--full", action="store_true", help="Generate a full changelog covering every tag, not just the latest range.")
    parser.add_argument("--from", dest="from_ref", default=None, help="Start ref (exclusive). Defaults to the latest tag.")
    parser.add_argument("--to", dest="to_ref", default="HEAD", help="End ref (inclusive). Defaults to HEAD.")
    parser.add_argument("--title", default="Unreleased", help="Section title to use for the generated range (default: Unreleased).")
    parser.add_argument("-o", "--output", default=None, help="Write output to this file instead of stdout.")
    parser.add_argument("--version", action="version", version=f"changeloggen {__version__}")
    return parser


def _build_range_sections(root: Path, args: argparse.Namespace) -> list[tuple[str, str | None, list]]:
    tags = list_tags_chronological(root)

    if args.full:
        sections: list[tuple[str, str | None, list]] = []

        head_commits = get_commits(root, f"{tags[-1].name}..HEAD" if tags else None)
        if head_commits:
            sections.append(("Unreleased", None, [parse_commit(c) for c in head_commits]))

        for index in range(len(tags) - 1, -1, -1):
            tag = tags[index]
            previous_tag = tags[index - 1] if index > 0 else None
            rev_range = f"{previous_tag.name}..{tag.name}" if previous_tag else tag.name
            commits = get_commits(root, rev_range)
            sections.append((tag.name, tag.date.strftime("%Y-%m-%d"), [parse_commit(c) for c in commits]))

        return sections

    from_ref = args.from_ref or (tags[-1].name if tags else None)
    rev_range = f"{from_ref}..{args.to_ref}" if from_ref else args.to_ref
    commits = get_commits(root, rev_range)
    return [(args.title, None, [parse_commit(c) for c in commits])]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: '{root}' is not a directory", file=sys.stderr)
        return 2

    sections = _build_range_sections(root, args)
    repo_url = current_repo_url(root)
    output = render_full_changelog(sections, repo_url)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
