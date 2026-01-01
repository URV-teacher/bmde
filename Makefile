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

# ---- helpers --------------------------------------------------------------
install: $(VENV_DIR)/bin/bmde  ## Installs package into the venv

$(VENV_DIR)/bin/bmde: $(VENV_DIR)/bin/python  ## Installs package into the venv
	@$(PIP) install -e .

$(VENV_DIR)/bin/python:  ## internal: create venv if missing
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON_BIN) -m pip install --upgrade pip

venv: $(VENV_DIR)/bin/python  ## Create virtualenv (.venv) and upgrade pip
	@echo "✅ venv ready at $(VENV_DIR)"

dev: $(VENV_DIR)/bin/python ## Installs package and dev deps into the venv
	@$(PIP) install -e ".[dev]"

install_build: venv
	@$(PIP) install build

# ---- quality --------------------------------------------------------------

lint: dev ## Run static checks (ruff + mypy)
	@$(VENV_DIR)/bin/ruff check .
	@$(VENV_DIR)/bin/mypy src

fmt: dev ## Auto-format (black + ruff --fix)
	@$(VENV_DIR)/bin/ruff check --fix .

test: dev ## Run tests
	@PYTHONPATH=src $(VENV_DIR)/bin/pytest -s

# ---- build ----------------------------------------------------------------

dist: install_build ## Build source and wheel distribution
	@$(PYTHON) -m build

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
