# changeloggen

[![CI](https://github.com/mectroptuff/changeloggen/actions/workflows/ci.yml/badge.svg)](https://github.com/mectroptuff/changeloggen/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Generate a clean `CHANGELOG.md` straight from your git history.** No config file, no API tokens, no service to sign up for — it just reads `git log` and groups commits by [Conventional Commit](https://www.conventionalcommits.org/) type.

```
$ changeloggen --full

# Changelog

## Unreleased

### Documentation

- update readme (`86e7203`)

## v0.1.0 - 2026-07-27

### Breaking Changes

- change public API (`a87b514`)

### Features

- change public API (`a87b514`)
- **auth:** add login flow (`e9ff9e0`)

### Bug Fixes

- crash on empty input (`3b5a0d3`)
```

## Why

Everyone agrees changelogs are useful. Almost nobody keeps one up to date by hand. If your commit messages already follow (or loosely follow) Conventional Commits, `changeloggen` turns them into a proper changelog in under a second — including breaking-change callouts and links back to each commit.

Commits that don't follow the convention aren't dropped — they land in an "Other Changes" section, so you get a complete history either way.

## Install

```bash
pip install changeloggen
```

Or without installing:

```bash
pipx run changeloggen --full
uvx changeloggen --full
```

## Usage

```bash
changeloggen                          # changes since the latest tag, titled "Unreleased"
changeloggen --full                   # full changelog: every tag, plus Unreleased at the top
changeloggen --from v1.0.0 --to HEAD  # a specific custom range
changeloggen --title "v2.0.0"         # override the section title
changeloggen -o CHANGELOG.md          # write to a file instead of stdout
```

## Supported commit types

`feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, `style`, `revert` — each mapped to a human-friendly section heading. A `!` after the type (e.g. `feat!:`) or a `BREAKING CHANGE:` footer promotes the entry into a dedicated "Breaking Changes" section at the top.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
