# Makefile for bmde
# Usage examples:
#   make venv
#   make dev
#   make lint
#   make fmt
#   make test
#   make run CMD="run -f demo.nds --debug"
#   make clean

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ---- config ---------------------------------------------------------------

# Prefer python3.11 (the oldest supported version, the one of CI), otherwise python3 (e.g. recent Debian/Ubuntu, which
# have no `python` command)
ifneq ($(shell command -v python3.11 2> /dev/null),)
    PYTHON_BIN ?= python3.11
else
    PYTHON_BIN ?= python3
endif

VENV_DIR   ?= venv
VENV_BIN   ?= $(VENV_DIR)/bin
PYTHON     := $(VENV_BIN)/python
PIP        := $(VENV_BIN)/pip
PRE_COMMIT := $(VENV_BIN)/pre-commit
GIT        := git

PKG_NAME   := bmde

# ---- build ------------------------------------------------------------------

dist: $(VENV_BIN)/pyproject-build  ## Build source and wheel distribution
	@$(PYTHON) -m build

# ---- helpers ----------------------------------------------------------------

# Create virtualenv
$(VENV_BIN)/python:
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON) -m pip install --upgrade pip

# Install runtime dependencies (creates the bmde executable)
$(VENV_BIN)/bmde: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e .
	@$(GIT) submodule update --init --recursive

# Install the package in editable mode plus one dependency group of pyproject.toml (test, lint, docs or dev, which has
# them all). A stamp file is the target because the editable install of hatchling leaves no file in the tree whose
# timestamp pip bumps, and tool binaries (e.g. ruff) keep theirs when they are already up to date.
# --group needs pip 25.1, which may be newer than the pip of an existing venv.
$(VENV_DIR)/.group-%: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install --quiet --upgrade "pip>=25.1"
	@$(PIP) install -e . --group $*
	@touch "$@"

$(VENV_BIN)/pyproject-build: $(VENV_BIN)/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_BIN)/python  ## Create virtualenv
	@echo "venv ready at $(VENV_DIR)"

install: $(VENV_BIN)/bmde  ## Install the package in editable mode

install-test: $(VENV_DIR)/.group-test  ## Install the package and the test dependencies (what CI tests with)

install-lint: $(VENV_DIR)/.group-lint  ## Install the package and the lint dependencies (what CI lints with)

install-docs: $(VENV_DIR)/.group-docs  ## Install the package and the documentation dependencies

dev: $(VENV_DIR)/.group-dev  ## Install the package, every dependency group and the pre-commit hooks
	@$(PRE_COMMIT) install

# ---- quality ----------------------------------------------------------------
#
# The checks are defined in .pre-commit-config.yaml: `git commit` runs them on the staged files, and `make lint` (also
# run by CI) on every tracked file. lint-pre-commit runs its hooks; the other lint-* targets are the ones its local
# hooks call, because they need the venv.

# ---- formatting (mutating: fixes what it can) ----

# The hooks of .pre-commit-config.yaml that fix files. pre-commit fails when a hook changes a file, so their result is
# ignored here: `make lint` reports what could not be fixed
FIX_HOOKS := ruff-check ruff-format trailing-whitespace end-of-file-fixer

EXAMPLE_CONFIG := examples/bmde.toml

fmt-example-config:  ## Regenerate examples/bmde.toml with every option and its default value
	@$(PYTHON) -m $(PKG_NAME) --show-default-config > "$(EXAMPLE_CONFIG)"

# Every AI tool reads its own ignore file, all in gitignore syntax: .aiexclude is the one to edit and the rest are
# copies, so a tool can never see a file that another one is told to skip.
AI_IGNORE_SOURCE := .aiexclude
AI_IGNORE_COPIES := .geminiignore .cursorignore .aiderignore .codeiumignore .aiignore
AI_IGNORE_HEADER := \# GENERATED from $(AI_IGNORE_SOURCE) by `make fmt-ai-ignore`, edit that file instead

fmt-ai-ignore:  ## Regenerate the ignore files of the other AI tools from .aiexclude
	@for f in $(AI_IGNORE_COPIES); do
		{ echo '$(AI_IGNORE_HEADER)'; cat "$(AI_IGNORE_SOURCE)"; } > "$$f"
	done

fmt: fmt-example-config fmt-ai-ignore  ## Auto-format and fix everything that can be fixed, in every tracked file
	@for hook in $(FIX_HOOKS); do
		$(PRE_COMMIT) run --all-files "$$hook" || true
	done

# ---- linting (fails on violation) ----

lint: lint-pre-commit lint-mypy lint-example-config lint-ai-ignore  ## Run every check on every tracked file (what CI runs)

# The local hooks of .pre-commit-config.yaml that have a target of their own, which `make lint` already runs
OWN_TARGET_HOOKS := mypy,example-config,ai-ignore

lint-pre-commit:  ## Run the hooks of .pre-commit-config.yaml (ruff, shellcheck, detect-secrets, ...) on every file
	@SKIP=$(OWN_TARGET_HOOKS) $(PRE_COMMIT) run --all-files --show-diff-on-failure

lint-mypy:  ## Check types with mypy --strict
	@$(VENV_BIN)/mypy src

lint-example-config:  ## Check examples/bmde.toml is up to date with the settings schema (fix with make fmt)
	@$(PYTHON) -m $(PKG_NAME) --show-default-config | diff -u "$(EXAMPLE_CONFIG)" - \
		|| { echo "$(EXAMPLE_CONFIG) is outdated, run 'make fmt'"; exit 1; }

lint-ai-ignore:  ## Check the AI ignore files are up to date with .aiexclude (fix with make fmt)
	@status=0
	for f in $(AI_IGNORE_COPIES); do
		{ echo '$(AI_IGNORE_HEADER)'; cat "$(AI_IGNORE_SOURCE)"; } | diff -u "$$f" - \
			|| { echo "$$f is outdated, run 'make fmt'"; status=1; }
	done
	exit $$status

test:  ## Run tests with coverage (fails under the fail_under of pyproject.toml)
	@PYTHONPATH=src PYTHONUNBUFFERED=1 $(VENV_BIN)/pytest -s --cov --cov-report=term --cov-report=xml

# ---- run ------------------------------------------------------------------

# Pass arguments to the CLI via CMD, e.g.:
#   make run CMD="run -f demo.nds --debug"
CMD ?= --help
run: install  ## Run the bmde CLI (python -m bmde)
	@$(PYTHON) -m $(PKG_NAME) $(CMD)

# ---- docs -------------------------------------------------------------------

readme:  ## Render the README guide
	./scripts/render-guide.py

docs-serve: install-docs  ## Serve the documentation site locally with hot reload
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs serve

docs-build: install-docs  ## Build the static documentation site into site/
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs build

docs-deploy: install-docs  ## Deploy the documentation site to GitHub Pages
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs gh-deploy --force

# ---- maintenance ------------------------------------------------------------

clean:  ## Remove build/test artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov dist build *.egg-info src/*.egg-info \
		site "$(VENV_DIR)"

# ---- meta -------------------------------------------------------------------


.PHONY: venv install install-test install-lint install-docs dev run clean help dist readme docs-serve docs-build docs-deploy \
        fmt fmt-example-config fmt-ai-ignore lint lint-pre-commit lint-mypy lint-example-config lint-ai-ignore test

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
