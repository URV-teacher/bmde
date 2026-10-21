# Agent guidelines

Instructions for AI coding agents working on this repository. Humans: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Project

`bmde` is a Python CLI (Typer + Pydantic) that wraps the Bare Metal Development Environment for Nintendo DS
development used in the Computers subject at URV. Each command (`build`, `run`, `debug`, `git`, `patch`, ...) runs a
tool either on the host or inside a Docker image. The images are built from `base/`, the submodules in `components/`
and `shell/` (see `docker-bake.hcl`).

- `src/bmde/commands/<command>/`: `cli.py` (Typer options) -> `command.py` (merges CLI options and config into a
  spec) -> `service.py` (picks a backend) -> `backends/{docker,host,...}.py`.
- `src/bmde/config/`: Pydantic settings loaded from `bmde.toml` files and environment variables.
- `src/bmde/core/`: shared logging, Docker, subprocess and option helpers.
- `tests/unit/` and `tests/integration/`: pytest suites.

## Workflow

Everything goes through the Makefile, which uses the project venv in `venv/`. Do not call bare `python` or `pip`.

```shell
make dev     # create venv/, install the package with the dev extras and the pre-commit hooks
make fmt     # auto-fix: ruff check --fix, ruff format, regenerate examples/bmde.toml and the AI ignore files, whitespace
make lint    # every non-mutating check (ruff, mypy --strict, YAML/TOML, shellcheck, detect-secrets, ...)
make test    # pytest with coverage; fails under the fail_under of pyproject.toml
make run CMD="run -f demo.nds"
```

Before you consider a task done, `make lint` and `make test` must pass with no errors. If you change the settings
schema, run `make fmt` so `examples/bmde.toml` stays up to date (`make lint` checks it).

Never read, print or commit a root `bmde.toml` or `.env`: they hold real VPN/SSH credentials.

## Code conventions

- Python 3.11+. Full type annotations; the code must pass `mypy --strict` without `# type: ignore` unless there is no
  reasonable alternative.
- Modern syntax: `X | None`, `list[str]`, `collections.abc` types, `StrEnum` where it fits.
- `from __future__ import annotations` in modules with annotations, as the existing code does.
- Use `pathlib.Path`, not string paths.
- Use the logger from `bmde.core.logging` (`log = logging.get_logger(__name__)`), not `print`, except for CLI output.
- Keep the layering of a command (cli -> command -> service -> backend); add a new tool as a new backend.
- Comments explain *why*, not *what*. Do not delete existing comments, docstrings or log statements unless the change
  makes them wrong.
- Mention any change to the CLI options or to `bmde.toml` that breaks existing user configs.

## Tests

- Put tests in `tests/unit/` (no Docker, network or external tools) or `tests/integration/` (may need git, Docker or
  the `components/` submodules; `pytest.skip` when a requirement is missing).
- Plain `assert` statements; no message unless the check is not obvious. Do not test trivial things such as
  instantiating a Pydantic model.

## Commits and pull requests

- [Conventional Commits](https://www.conventionalcommits.org): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
  `build:`, `ci:`, `chore:`; `!` for breaking changes. See `.gitmessage`. The type decides the next version, because
  every merge to `master` is released to PyPI by semantic-release.
- One topic per branch; open the pull request against `master` (GitHub Flow).
