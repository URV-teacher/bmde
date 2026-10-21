### Installation

#### Dev container (recommended)

The repository has a [dev container](https://code.visualstudio.com/docs/devcontainers/containers) with everything
needed to develop the CLI, `.devcontainer/bmde-dev/`, on the `aleixmt/bmde-dev` image: the full development environment
of the BMDE (`aleixmt/bmde-full`, every NDS tool) plus Python, the packages of the integration tests and a Docker client
that uses the Docker of your computer (Docker outside of Docker), so the docker backend of the CLI and the integration
tests work inside it and share the images of your computer.

1. Clone the repository and open it in VS Code, with the
   [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
2. Run **Dev Containers: Reopen in Container** and choose **BMDE: bmde CLI development**. On creation it checks out the
   submodules and runs `make dev`.
3. Run `make lint`, `make test` or `make run CMD="--help"` in its terminal.

Graphical programs open in the X server of the host, like in the [dev container of the students](../getting-started/devcontainer.md).
The Docker daemon of your computer looks for the paths the CLI and the tests mount in your computer, not in the
container, so the project is mounted at the same path as in your computer and the temporary files go to its `tmp/`
(`TMPDIR`, ignored by git). That is why this dev container is meant for Linux hosts (or WSL 2). Git worktrees can't be
opened in it (their `.git` points to a path of the host).

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
