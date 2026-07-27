# Contributing

Thanks for your interest! Ideas that would be especially welcome:

- Support scanning commit trailers other than `BREAKING CHANGE:`
- Support GitLab/Bitbucket commit URL formats in addition to GitHub
- A `--dry-run` diff mode that shows what would change in an existing `CHANGELOG.md`

## Development setup

```bash
git clone https://github.com/mectroptuff/changeloggen
cd changeloggen
pip install -e ".[dev]"
pytest
```

## Code style

`changeloggen` has zero runtime dependencies beyond Python's standard library and the `git` binary. Please don't add new third-party runtime dependencies without discussing it in an issue first.
