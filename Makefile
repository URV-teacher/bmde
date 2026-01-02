# Makefile for bmde
# Usage examples:
#   make venv
#   make lint
#   make fmt
#   make test
#   make run CMD="run -f demo.nds --debug"
#   make clean

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ---- config ---------------------------------------------------------------

PYTHON_BIN ?= python
VENV_DIR   ?= venv
PYTHON     := $(VENV_DIR)/bin/$(PYTHON_BIN)
PIP        := $(VENV_DIR)/bin/pip

PKG_NAME   := bmde

# ---- build ----------------------------------------------------------------

dist: $(VENV_DIR)/bin/pyproject-build ## Build source and wheel distribution
	@$(PYTHON) -m build

# ---- helpers --------------------------------------------------------------

# Create virtualenv
$(VENV_DIR)/bin/python:
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON_BIN) -m pip install --upgrade pip

# Install runtime dependencies (creates bmde executable)
$(VENV_DIR)/bin/bmde: $(VENV_DIR)/bin/python pyproject.toml
	@$(PIP) install -e .

# Install dev dependencies
# We use PKG-INFO as the target because pip updates it when dependencies change.
# This avoids the loop where 'make fmt && make lint' rebuilds twice because binaries
# like 'bin/ruff' might not have their timestamp updated by pip if they are already present.
src/bmde.egg-info/PKG-INFO: $(VENV_DIR)/bin/python pyproject.toml
	@$(PIP) install -e ".[dev]"

# Install build tool
$(VENV_DIR)/bin/pyproject-build: $(VENV_DIR)/bin/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_DIR)/bin/python  ## Create virtualenv
	@echo "✅ venv ready at $(VENV_DIR)"

install: $(VENV_DIR)/bin/bmde  ## Install package in editable mode

dev: src/bmde.egg-info/PKG-INFO  ## Install package and dev dependencies

# ---- quality --------------------------------------------------------------

lint:  ## Run static checks (ruff + mypy)
	@$(VENV_DIR)/bin/ruff check .
	@$(VENV_DIR)/bin/mypy src

fmt:  ## Auto-format (black + ruff --fix)
	@$(VENV_DIR)/bin/black src tests
	@$(VENV_DIR)/bin/ruff check --fix .

test:  ## Run tests
	@PYTHONPATH=src $(VENV_DIR)/bin/pytest -s

# ---- run ------------------------------------------------------------------

# Pass arguments to the CLI via CMD, e.g.:
#   make run CMD="run -f demo.nds --debug"
CMD ?= --help
run: install  ## Run the bmde CLI (python -m bmde)
	@$(PYTHON) -m $(PKG_NAME) $(CMD)

# ---- maintenance ----------------------------------------------------------

clean:  ## Remove build/test artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info "$(VENV_DIR)"

# ---- meta -----------------------------------------------------------------

.PHONY: venv lint fmt test run clean help dist install dev

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
