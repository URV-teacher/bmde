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

# Install dev dependencies. PKG-INFO is used as the target because pip updates it when dependencies change,
# avoiding a rebuild loop when tool binaries (e.g. ruff) don't get their timestamp bumped by pip.
src/bmde.egg-info/PKG-INFO: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e ".[dev]"
	@$(PRE_COMMIT) install

$(VENV_BIN)/pyproject-build: $(VENV_BIN)/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_BIN)/python  ## Create virtualenv
	@echo "venv ready at $(VENV_DIR)"

install: $(VENV_BIN)/bmde  ## Install the package in editable mode

dev: src/bmde.egg-info/PKG-INFO  ## Install the package, dev dependencies and pre-commit hooks

# ---- quality ----------------------------------------------------------------
#
# Every check lives here: .pre-commit-config.yaml and CI just call these targets, so there is a single place that
# defines what "linted", "formatted" and "tested" mean for this repo, using the tool versions of pyproject.toml.

# -c core.quotepath=false so filenames with non-ASCII characters aren't octal-escaped in the output.
GIT_NQ      := git -c core.quotepath=false
TEXT_FILES  := $(shell $(GIT_NQ) grep -Il '' -- . 2>/dev/null)
YAML_FILES  := $(shell $(GIT_NQ) ls-files '*.yml' '*.yaml')
TOML_FILES  := $(shell $(GIT_NQ) ls-files '*.toml')
SH_FILES    := $(shell $(GIT_NQ) ls-files '*.sh' '*.bash')
ALL_FILES   := $(shell $(GIT_NQ) ls-files)

# ---- formatting (mutating: fixes what it can) ----

fmt-ruff:  ## Auto-fix lint issues with ruff
	@$(VENV_BIN)/ruff check --fix .

fmt-ruff-format:  ## Auto-format with ruff format
	@$(VENV_BIN)/ruff format .

fmt-hygiene:  ## Fix trailing whitespace and missing final newlines on every tracked text file
	@test -z "$(TEXT_FILES)" || $(VENV_BIN)/trailing-whitespace-fixer $(TEXT_FILES) || true
	@test -z "$(TEXT_FILES)" || $(VENV_BIN)/end-of-file-fixer $(TEXT_FILES) || true

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

fmt: fmt-ruff fmt-ruff-format fmt-example-config fmt-ai-ignore fmt-hygiene  ## Auto-format and fix everything that can be fixed

# ---- linting (non-mutating: fails on violation, used by CI and pre-commit) ----

lint-ruff:  ## Check lint rules with ruff
	@$(VENV_BIN)/ruff check .

lint-ruff-format:  ## Check the code is formatted with ruff format (fix with make fmt)
	@$(VENV_BIN)/ruff format --check .

lint-mypy:  ## Check types with mypy --strict
	@$(VENV_BIN)/mypy src

lint-yaml:  ## Check YAML files parse
	@test -z "$(YAML_FILES)" || $(VENV_BIN)/check-yaml $(YAML_FILES)

lint-toml:  ## Check TOML files parse
	@test -z "$(TOML_FILES)" || $(VENV_BIN)/check-toml $(TOML_FILES)

lint-large-files:  ## Check no accidentally large file was added
	@$(VENV_BIN)/check-added-large-files --enforce-all $(ALL_FILES)

lint-merge-conflict:  ## Check for leftover merge conflict markers
	@test -z "$(TEXT_FILES)" || $(VENV_BIN)/check-merge-conflict --assume-in-merge $(TEXT_FILES)

lint-case-conflict:  ## Check for filenames that only differ by case
	@$(VENV_BIN)/check-case-conflict

lint-shellcheck:  ## Lint shell scripts with shellcheck
	@test -z "$(SH_FILES)" || $(VENV_BIN)/shellcheck --external-sources $(SH_FILES)

# Mark a false positive with a `pragma: allowlist secret` comment on its line rather than with a baseline file, which
# detect-secrets would rewrite every time the line numbers of a known finding shift.
lint-secrets:  ## Check no credential or private key is committed
	@test -z "$(TEXT_FILES)" || $(VENV_BIN)/detect-secrets-hook $(TEXT_FILES)

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

lint: lint-ruff lint-ruff-format lint-mypy lint-example-config lint-ai-ignore lint-yaml lint-toml lint-large-files lint-merge-conflict lint-case-conflict lint-shellcheck lint-secrets  ## Run every non-mutating check

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

docs-serve: dev  ## Serve the documentation site locally with hot reload
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs serve

docs-build: dev  ## Build the static documentation site into site/
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs build

docs-deploy: dev  ## Deploy the documentation site to GitHub Pages
	@PATH="$(abspath $(VENV_BIN)):$$PATH" PYTHONPATH=src $(PYTHON) -m mkdocs gh-deploy --force

# ---- maintenance ------------------------------------------------------------

clean:  ## Remove build/test artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov dist build *.egg-info src/*.egg-info \
		site "$(VENV_DIR)"

# ---- meta -------------------------------------------------------------------

.PHONY: venv install dev run clean help dist readme docs-serve docs-build docs-deploy \
        fmt fmt-ruff fmt-ruff-format fmt-example-config fmt-ai-ignore fmt-hygiene \
        lint lint-ruff lint-ruff-format lint-mypy lint-example-config lint-ai-ignore lint-yaml lint-toml lint-large-files lint-merge-conflict lint-case-conflict \
        lint-shellcheck lint-secrets test

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
