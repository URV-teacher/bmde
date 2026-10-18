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

# Check if python3.11 exists, otherwise default to python
ifneq ($(shell command -v python3.11 2> /dev/null),)
    PYTHON_BIN ?= python3.11
else
    PYTHON_BIN ?= python
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
	@$(PYTHON_BIN) -m pip install --upgrade pip

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

fmt: fmt-ruff fmt-ruff-format fmt-hygiene  ## Auto-format and fix everything that can be fixed

# ---- linting (non-mutating: fails on violation, used by CI and pre-commit) ----

lint-ruff:  ## Check lint rules with ruff
	@$(VENV_BIN)/ruff check .

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

lint: lint-ruff lint-mypy lint-yaml lint-toml lint-large-files lint-merge-conflict lint-case-conflict lint-shellcheck  ## Run every non-mutating check

test:  ## Run tests
	@PYTHONPATH=src PYTHONUNBUFFERED=1 $(VENV_BIN)/pytest -s

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
	@rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info src/*.egg-info site "$(VENV_DIR)"

# ---- meta -------------------------------------------------------------------

.PHONY: venv install dev run clean help dist readme docs-serve docs-build docs-deploy \
        fmt fmt-ruff fmt-ruff-format fmt-hygiene \
        lint lint-ruff lint-mypy lint-yaml lint-toml lint-large-files lint-merge-conflict lint-case-conflict \
        lint-shellcheck test

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
