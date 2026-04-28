# Repository Structure and Usage Guide

This document provides a deep dive into the BMDE repository structure. It explains not just what each file is, but **when** it is used, **why** it exists, and which **operations** or **workflows** rely on it.

---

## 1. Root Directory Configuration
These files define the project's identity, build process, and developer experience.

### Build & Dependency Management
*   **`pyproject.toml`**
    *   **Purpose**: The central configuration file for the Python project (PEP 621).
    *   **Usage**:
        *   **Dependencies**: Defines runtime requirements (`typer`, `docker`, etc.) and optional dev groups (`dev`, `docs`).
        *   **Build System**: Configures `hatchling` as the build backend and `hatch-vcs` for dynamic versioning from Git tags.
        *   **Tool Config**: Centralizes settings for `ruff` (linting/formatting), `pytest`, `mypy`, and `python-semantic-release`.
    *   **Operations**:
        *   `pip install .` / `make install`: Reads dependencies.
        *   `make lint` / `make test`: Reads tool configs.
        *   `make dist` / CI Release: Reads build-system and semantic-release configs.

*   **`Makefile`**
    *   **Purpose**: A command-line task runner for common development workflows.
    *   **Usage**: Simplifies complex commands into short targets (`install`, `lint`, `test`, `docs-serve`). It manages the virtual environment creation (`venv`) and ensures tools are run from the correct path.
    *   **Operations**:
        *   `make install`: Creates venv and installs package in editable mode.
        *   `make lint`: Runs `ruff` and `mypy`.
        *   `make test`: Runs `pytest`.
        *   `make docs-serve`: Serves MkDocs locally.

*   **`requirements.txt`**
    *   **Purpose**: Legacy or specific environment lock file.
    *   **Usage**: While `pyproject.toml` is the source of truth, this file can be used for reproducible builds in some environments or by specific tools that don't support `pyproject.toml` fully yet.
    *   **Operations**: `pip install -r requirements.txt`.

*   **`MANIFEST.in`**
    *   **Purpose**: Controls files included in the source distribution (`sdist`).
    *   **Usage**: Explicitly includes non-Python files (like `components/` scripts, `README.md`, `LICENSE`) that wouldn't be picked up automatically by `hatchling`.
    *   **Operations**: `python -m build` (or `make dist`), creating the tarball uploaded to PyPI.

### Developer Experience & Quality
*   **`.pre-commit-config.yaml`**
    *   **Purpose**: Configuration for `pre-commit` hooks.
    *   **Usage**: Defines checks that run automatically before every `git commit`. Includes `ruff` (formatting), `mypy` (types), `trailing-whitespace`, and `shellcheck`.
    *   **Operations**: `git commit` (blocks commit if checks fail).

*   **`.editorconfig`**
    *   **Purpose**: Cross-editor configuration for coding style.
    *   **Usage**: Ensures consistent indentation (spaces vs tabs), charset, and line endings across different IDEs (VS Code, PyCharm, etc.).
    *   **Operations**: File editing and saving in IDEs.

*   **`.coveragerc`**
    *   **Purpose**: Configuration for `coverage.py`.
    *   **Usage**: Defines which files to include/exclude when calculating test coverage (e.g., omitting `tests/` and `venv/`).
    *   **Operations**: Running tests with coverage (e.g., `pytest --cov`).

### Git Configuration
*   **`.gitignore`**
    *   **Purpose**: Specifies intentionally untracked files.
    *   **Usage**: Prevents version control of build artifacts (`dist/`, `site/`), virtual environments (`venv/`), caches (`__pycache__/`), and local secrets (`.env`).
    *   **Operations**: `git status`, `git add`.

*   **`.gitattributes`**
    *   **Purpose**: Defines path attributes for Git.
    *   **Usage**: Enforces line endings (`text eol=lf`), configures diff drivers for specific languages, and marks generated files (to exclude from GitHub language stats).
    *   **Operations**: `git checkout`, `git diff`, GitHub repository language statistics.

*   **`.gitmessage`**
    *   **Purpose**: Template for commit messages.
    *   **Usage**: Can be configured as the commit template (`git config commit.template .gitmessage`) to remind developers of the project's commit conventions (e.g., `ADDED:`, `FIXED:`).
    *   **Operations**: `git commit`.

*   **`.gitmodules`**
    *   **Purpose**: Configuration for Git Submodules.
    *   **Usage**: Tracks external repositories included within this repo (if any).
    *   **Operations**: `git submodule update`.

### Documentation & Metadata
*   **`README.md`**
    *   **Purpose**: The project's landing page.
    *   **Usage**: Displayed on the GitHub repository root. Contains an overview, installation instructions, usage examples, and badges.
    *   **Operations**: Viewing the repo on GitHub.

*   **`mkdocs.yml`**
    *   **Purpose**: Configuration for the MkDocs documentation site generator.
    *   **Usage**: Defines the site structure (`nav`), theme (`material`), plugins (`mkdocstrings`, `typer`), and extensions.
    *   **Operations**: `mkdocs build`, `mkdocs serve` (and via Makefile).

*   **`CNAME`**
    *   **Purpose**: Custom domain configuration for GitHub Pages.
    *   **Usage**: Tells GitHub Pages to serve the site from `docs.bmde.org` instead of the default URL.
    *   **Operations**: Deployment to GitHub Pages.

*   **`LICENSE`**
    *   **Purpose**: Legal terms of distribution (GPL-3.0-or-later).
    *   **Usage**: Defines how others can use, modify, and distribute the software.

*   **`CITATION.cff`**
    *   **Purpose**: Citation File Format.
    *   **Usage**: Provides metadata for academic citation of the software. GitHub uses this to generate a citation snippet in the sidebar.

*   **`CONTRIBUTORS`**
    *   **Purpose**: List of project contributors.
    *   **Usage**: Recognition of people who have worked on the project.

### Community Standards
*   **`CONTRIBUTING.md`**
    *   **Purpose**: Guidelines for contributors.
    *   **Usage**: Explains how to set up the dev environment, run tests, and submit PRs. Linked from GitHub PR creation page.

*   **`CODE_OF_CONDUCT.md`**
    *   **Purpose**: Community standards and enforcement.
    *   **Usage**: Sets expectations for behavior in the project's community spaces.

*   **`GOVERNANCE.md`**
    *   **Purpose**: Project decision-making rules.
    *   **Usage**: Describes roles (Maintainers, Contributors) and how decisions are made.

*   **`SECURITY.md`**
    *   **Purpose**: Security policy.
    *   **Usage**: Instructions on how to responsibly report security vulnerabilities.

### AI & Agent
*   **`AGENT.md`**
    *   **Purpose**: Context for AI coding agents.
    *   **Usage**: Provides project-specific context and instructions for AI tools interacting with the codebase.

*   **`.aiexclude`**
    *   **Purpose**: Exclusion list for AI tools.
    *   **Usage**: Prevents AI agents from reading or modifying specific files (similar to `.gitignore` but for AI contexts).

### Directories (Root Level)
*   **`.devcontainer/`**: Contains `devcontainer.json` for configuring VS Code Dev Containers / GitHub Codespaces.
*   **`.github/`**: Contains GitHub Actions workflows, templates, dependabot config, and other platform-specific settings.
*   **`.gemini/`**: (Likely) Configuration or context for Gemini AI tools.
*   **`src/`**: The source code of the Python package.
*   **`components/`**: External tools/Docker definitions wrapped by BMDE.
*   **`docs/`**: Source markdown files for the documentation site.
*   **`tests/`**: Automated test suite.
*   **`dist/`**: (Generated) Directory where build artifacts (wheels, tarballs) are placed after `make dist`.
*   **`venv/`**: (Generated) The Python virtual environment directory.
*   **`examples/`**: Contains example projects or usage demonstrations.
*   **`scripts/`**: (Optional) General utility scripts for repo maintenance (distinct from `components/*/scripts`).

---

## 2. Source Code (`src/bmde/`)
This directory contains the actual Python package installed by users.

### Entry Points
*   **`__main__.py`**
    *   **Purpose**: Module entry point.
    *   **Usage**: Executed when running `python -m bmde`. It calls the main CLI app.
*   **`cli.py`**
    *   **Purpose**: Main Typer application definition.
    *   **Usage**: Defines the `bmde` command, registers global callbacks (like logging setup), and imports/registers all subcommands (`build`, `run`, etc.).

### Configuration Logic (`src/bmde/config/`)
*   **`schema.py`**
    *   **Purpose**: Pydantic models defining the structure of `bmde.toml`.
    *   **Usage**: Validates user configuration at runtime.
*   **`loader.py`**
    *   **Purpose**: Logic to find and load configuration files.
    *   **Usage**: Runs at the start of every CLI command to merge defaults, config files, and environment variables.

### Core Utilities (`src/bmde/core/`)
*   **`logging.py`**: Configures the application's logging (Rich formatting, log levels). Used globally.
*   **`docker.py`**: Wrappers for the Docker SDK. Used by any command with a Docker backend to manage containers and networks.
*   **`exec.py`**: Wrappers for `subprocess`. Used by host backends to run system commands.
*   **`shared_options.py`**: Reusable Typer options (e.g., `--verbose`, `--dry-run`) imported by multiple commands to ensure consistency.

### Commands (`src/bmde/commands/`)
Each subdirectory here corresponds to a CLI subcommand (e.g., `bmde build`).

*   **Structure of a Command Module (e.g., `build/`)**:
    *   **`cli.py`**: The interface layer. Defines the arguments and options using Typer. It parses inputs and calls the `command.py`.
    *   **`command.py`**: The orchestration layer. It combines CLI arguments with configuration settings to create a "Spec" (Specification) object.
    *   **`spec.py`**: Data classes (Pydantic) that fully describe *what* needs to be done (e.g., "Build directory X with backend Y").
    *   **`service.py`**: The logic layer. It takes a Spec and executes it using the appropriate backend.
    *   **`backends/`**:
        *   **`docker.py`**: Implementation using Docker containers.
        *   **`host.py`**: Implementation using local system binaries.

---

## 3. Components (`components/`)
This directory contains the definitions for the external environments BMDE manages. These are not Python code but Docker definitions.

*   **`Dockerfile`**: Defines the environment (OS, tools, libraries) for a component (e.g., `desmume-docker` contains the emulator).
*   **`scripts/`**: Shell scripts used for:
    *   **Installation**: Installing the tool inside the Docker image or on the host (referenced in docs).
    *   **Testing**: Verifying the component works correctly.
    *   **Entrypoints**: Scripts that run when the container starts.
*   **Usage**:
    *   **Build Time**: Used by GitHub Actions (or manually) to build Docker images pushed to Docker Hub.
    *   **Run Time**: The `bmde` CLI (Docker backend) pulls these images to execute tasks.

---

## 4. Documentation (`docs/`)
The source for the project's website.

*   **`mkdocs.yml`** (Root): Configuration for MkDocs. Defines the theme, plugins (`mkdocstrings`, `typer`), and navigation structure.
*   **`*.md` files**: The actual content.
    *   **`components/*.md`**: Documentation for specific commands. These often use `::: mkdocs-typer` to auto-generate CLI references from the Python code.
    *   **`getting-started/host_components_installation.md`**: A special file that embeds scripts from `components/` using the `pymdownx.snippets` extension to ensure documentation stays in sync with actual installation scripts.
*   **Usage**: Processed by `mkdocs build` to generate a static HTML site in `site/`.

---

## 5. GitHub Automation (`.github/`)
Files that configure how GitHub interacts with the repository.

### Workflows (`workflows/`)
*   **`test.yml`**: Runs `pytest` on every push to ensure code correctness.
*   **`lint.yml`**: Runs `ruff` and `mypy` on every push to enforce style and types.
*   **`release.yml`**:
    *   **Trigger**: Push to `master`.
    *   **Action**: Uses `python-semantic-release` to analyze commits, bump the version, create a Git tag, generate a changelog in the Release body, and publish the package to PyPI.
*   **`docs.yml`**:
    *   **Trigger**: Push to `master`.
    *   **Action**: Builds the MkDocs site and deploys it to GitHub Pages.
*   **`dependabot.yml`**: Configures the bot to check for updates to Python packages, Docker base images, and GitHub Actions.

### Community Files
*   **`PULL_REQUEST_TEMPLATE/`**: Templates pre-filled when users open PRs (e.g., Bug Fix vs Feature).
*   **`CODEOWNERS`**: Automatically requests review from `@AleixMT` for PRs.
*   **`labeler.yml`**: Automatically adds labels (e.g., `documentation`, `docker`) to PRs based on which files were modified.

---

## 6. Tests (`tests/`)
*   **`conftest.py`**: Defines global Pytest fixtures (setup/teardown logic shared across tests).
*   **`integration/`**: Tests that run the full `bmde` CLI against real (or simulated) environments to verify end-to-end functionality.
