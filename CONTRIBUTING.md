# Contributing

Contributions are welcome: bug reports, ideas, documentation and code. For questions, see
[SUPPORT.md](https://github.com/URV-teacher/bmde/blob/master/.github/SUPPORT.md).

## Reporting bugs and requesting features

Open an [issue](https://github.com/URV-teacher/bmde/issues/new/choose) using the bug report or feature request
template. For bugs, include the version (`bmde --version`) and the full command and its output with `--trace`.
Report security problems privately as described in
[SECURITY.md](https://github.com/URV-teacher/bmde/blob/master/SECURITY.md), not in an issue.

## Development setup

You need Python 3.11+, git, make and Docker (for the Docker backends and the integration tests).

```shell
git clone --recurse-submodules https://github.com/URV-teacher/bmde
cd bmde
make dev    # creates venv/, installs bmde with every dependency group and the pre-commit hooks
```

Run `make help` to list every target. The ones you will use most:

```shell
make fmt    # auto-fix formatting and lint issues
make lint   # every check CI runs on a pull request
make test   # tests with coverage
make run CMD="build --help"
make docs-serve
```

The checks are defined in `.pre-commit-config.yaml`. The pre-commit hooks run them on the files you commit (not on your
unstaged edits or untracked files) and the tests before every push; `make lint` and CI run them on every file, so CI
should not surprise you. Add a check there, not in the Makefile; Dependabot updates the versions of the hooks.

## Workflow

The project follows [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow): `master` is
always releasable, and every merge to it publishes a new version to PyPI.

1. Fork the repository (or create a branch, if you are a maintainer) from `master`, e.g. `feat/fat-image`.
2. Make your changes, with tests and documentation where it applies.
3. Check that `make lint` and `make test` pass.
4. Open a pull request against `master` and fill in the template.
5. Once CI passes and a maintainer approves it, it is merged and released automatically.

## Commit messages

Commits follow [Conventional Commits](https://www.conventionalcommits.org), because the commit types decide the next
version:

| Type | Use | Release |
| --- | --- | --- |
| `feat` | New feature | minor |
| `fix`, `perf` | Bug fix, performance improvement | patch |
| `docs`, `refactor`, `test`, `build`, `ci`, `chore` | Everything else | none |
| `<type>!` or a `BREAKING CHANGE:` footer | Incompatible change | major |

For example `feat(run): add --fat-image option` or `fix(git): retry the VPN connection`. To get the reminder in your
editor, run `git config commit.template .gitmessage`.

## Code style

Formatting and linting are enforced by ruff and `mypy --strict` (see `pyproject.toml`). See
[AGENTS.md](https://github.com/URV-teacher/bmde/blob/master/AGENTS.md) for the conventions of the code base; they
apply to people too.

By contributing you agree that your contributions are licensed under the
[GPL-3.0-or-later](https://github.com/URV-teacher/bmde/blob/master/LICENSE) and that you follow the
[Code of Conduct](https://github.com/URV-teacher/bmde/blob/master/CODE_OF_CONDUCT.md).
