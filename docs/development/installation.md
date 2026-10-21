### Installation

#### Dev container (recommended)

The repository has a [dev container](https://code.visualstudio.com/docs/devcontainers/containers) with everything
needed to develop the CLI, `.devcontainer/bmde-dev/`, on the `aleixmt/bmde-dev` image: the full development environment
of the BMDE (`aleixmt/bmde-full`, every NDS tool) plus Python, the packages of the integration tests and its own Docker
daemon, so the docker backend of the CLI and the integration tests work inside it.

1. Clone the repository and open it in VS Code, with the
   [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
2. Run **Dev Containers: Reopen in Container** and choose **BMDE: bmde CLI development**. On creation it checks out the
   submodules and runs `make dev`.
3. Run `make lint`, `make test` or `make run CMD="--help"` in its terminal.

Graphical programs open in the X server of the host, like in the [dev container of the students](../getting-started/devcontainer.md).
The container is privileged (Docker in Docker) and keeps the images of its Docker daemon in the `bmde-dev-docker`
volume, so they survive rebuilding it. Git worktrees can't be opened in it (their `.git` points to a path of the host).

The other configuration, **BMDE: NDS development** (`.devcontainer/nds/`), is the template for the projects of the
students.

#### In your computer

You need Python 3.11+, git, make and Docker.

1. Clone the repository with its submodules
    ```shell
    git clone --recurse-submodules https://github.com/URV-teacher/bmde
    cd bmde
    ```
2. Create the virtual environment in `venv/` and install the package, the development dependencies and the pre-commit
   hooks
    ```shell
    make dev
    ```
3. Check that the CLI works
    ```shell
    ./venv/bin/bmde --help
    ```
