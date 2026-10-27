# Installation

The BMDE can be installed in several ways. They differ in what your computer needs and in how you work with your
projects, but all of them use the same [components](components.md) (devkitARM, DeSmuME, Insight...), installed in your
computer or run from their Docker images.

| Method                                                     | Your computer needs                           | In your projects you use               | Features of `bmde`¹ |
|------------------------------------------------------------|-----------------------------------------------|----------------------------------------|---------------------|
| [1. The bmde CLI](#1-the-bmde-cli) (recommended)           | Python, and Docker or the host components     | `bmde build`, `bmde run`, ...          | ✅                  |
| [2. Host components](#2-host-components)                   | Ubuntu / Debian                               | `make`, `make run`, `make debug`, git  | ❌                  |
| [3. Development environment in Docker](#3-development-environment-in-docker) | Docker                      | a shell with `make`, git, ...          | ❌                  |
| [4. The bmde CLI in Docker](#4-the-bmde-cli-in-docker)     | Docker                                        | `bmde build`, `bmde run`, ...          | ✅                  |
| [5. Makefile with Docker](#5-makefile-with-docker)         | Docker                                        | `make`, `make run`, `make debug`       | ❌                  |
| [6. From the sources](#6-from-the-sources-developers) (developers of `bmde`) | Python, git and make        | `bmde`, from your copy of the code     | ✅                  |

¹ Choosing the backend of each command, git without typing passwords (and connected to the VPN of the URV when
needed), the debugger connected to the emulator automatically, FAT images, controls of the course...

The [prerequisites](prerequisites.md) explain how to install Python, Docker and the rest of the requirements.

## 1. The bmde CLI

The recommended method: the `bmde` command in your computer, which runs each component with the backend you choose,
in Docker or installed in your computer, so you can mix and match them.

1. Install Python 3.11 or newer and pipx ([prerequisites](prerequisites.md#python)).
2. Install `bmde`:
    ```shell
    pipx install bmde
    bmde --version
    ```
3. Install the components that its commands need, in any of the [ways to install a component](components.md):
    * [Docker](components.md#docker-components) (recommended): install Docker, and `bmde` downloads the image of each
      component the first time it uses it.
    * [Host](components.md#host-components): install them in your computer with `scripts/install.sh`.
    * [Flatpak](components.md#flatpak-desmume), only for `bmde run`.
4. Check which backends each command can use (and [choose them](components.md#choosing-the-backend-of-each-command)
   if you want):
    ```shell
    bmde check
    ```
5. To use git with the server of the course, write your credentials of the VPN and of the git server in
   `~/.config/bmde/bmde.toml` (never in a repository), in the sections `[git.git]`, `[git.ssh]` and `[git.vpn]` (see
   [git](../commands/git.md) and [configuration](../commands/config.md)):
    ```toml
    [git.ssh]
    username = "12345678-A"
    password = "..."

    [git.vpn]
    username = "..."
    password = "..."
    ```
   On Linux, the VPN may also need the `ppp_async` kernel module loaded on the host (`sudo modprobe ppp_async`, and
   `echo ppp_async | sudo tee /etc/modules-load.d/ppp.conf` to load it on every boot, see
   [git](../commands/git.md#vpn-with-the-docker-backend-on-linux-the-ppp_async-kernel-module)).
6. Use it in your projects:
    ```shell
    bmde git clone 12345678-A@git.deim.urv.cat:comp_20
    cd comp_20
    bmde build
    bmde run
    bmde debug
    ```

Update it with `pipx upgrade bmde`.

## 2. Host components

The components installed in your computer, without `bmde`: the same environment as the Windows BMDE, but in Linux, so
you can follow the original documentation of the course with its Makefiles. There are no features of `bmde`: the
connection to the VPN, git and the debugger are done by hand.

1. Install the components in your computer with `scripts/install.sh`, as explained in
   [host components](components.md#host-components):
    ```shell
    git clone https://github.com/URV-teacher/bmde
    bmde/scripts/install.sh
    ```
2. Open a new session, so the environment of the components is loaded.
3. Use the Makefile of your project, as in the Windows BMDE:
    ```shell
    make            # build
    make run        # run in DeSmuME
    make debug      # debug with DeSmuME and Insight
    ```
4. To use the git server of the course from outside the URV, connect to the VPN with `connect_vpn.sh`, as your user
   (it uses `sudo` itself, only for openfortivpn). It takes your credentials from the variables `VPN_USERNAME`,
   `VPN_PASSWORD` (or `VPN_PASSWORD_FILE`, a file with it), `VPN_HOST`, `VPN_PORT`, `VPN_REALM` and `VPN_CERT`, waits
   until the VPN works and stays connected until you stop it (Ctrl+C), so run it in another terminal. Then use git as
   usual; `vpn_healthcheck.sh -v` tells whether the VPN still works:
    ```shell
    connect_vpn.sh                                   # in another terminal
    git clone 12345678-A@git.deim.urv.cat:comp_20
    ```

## 3. Development environment in Docker

A shell inside the full development environment of the BMDE (`aleixmt/bmde-full`), with every component and the git
and VPN helpers: your computer only needs [Docker](prerequisites.md#docker). Inside it, work as in the
[host components](#2-host-components) method.

1. Install Docker ([prerequisites](prerequisites.md#docker)).
2. From the root of your project, open a shell in the image (the first time, it downloads about 3 GB):
    ```shell
    docker run --rm -it -e MODE=host -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$PWD:/home/bmde/$(basename "$PWD")" -w "/home/bmde/$(basename "$PWD")" aleixmt/bmde-full:latest
    ```
   The project is mounted in a folder with its name, because the Makefiles of the course name the ROM after it. Your
   user in the image is `bmde`, with UID 1000 (the one of the first user of Linux): with another UID, the files of the
   build are not yours. If the windows of DeSmuME and Insight do not open, allow the user of the image with
   `xhost +SI:localuser:$(id -un)`.
3. Use it as in a host: `make`, `make run`, `make debug`, `git`... To connect to the VPN, run `connect_vpn.sh &`,
   which takes your credentials from `/run/secrets` (see below).

To avoid typing all of that, copy [`examples/shell/compose.yml`](https://github.com/URV-teacher/bmde/blob/master/examples/shell/compose.yml)
to the root of your project. It also brings the sound of DeSmuME, the VPN, your credentials (as Docker secrets, from
`~/.config/bmde/secrets`, see the comments of the file) and keeps the settings of DeSmuME and VS Code between runs:

```shell
mkdir -p ~/.config/bmde/secrets                 # your credentials, one file each (see compose.yml)
export PROJECT="$(basename "$PWD")"             # the name of the ROM (project.nds otherwise)
docker compose run --rm shell                   # a shell
docker compose run --rm shell make              # or one command
```

To add tools to the environment, copy also [`examples/shell/Dockerfile`](https://github.com/URV-teacher/bmde/blob/master/examples/shell/Dockerfile),
which extends `aleixmt/bmde-full`, add your packages to it, and replace `image:` by `build: .` in `compose.yml`.

With VS Code, the [dev container](devcontainer.md) opens the same environment from the editor.

## 4. The bmde CLI in Docker

The same as [the bmde CLI](#1-the-bmde-cli), for computers with Docker but without Python: `bmde` runs in its own
image (`aleixmt/bmde`), which runs the images of the components with the Docker of your computer (and also has every
component, for the `host` backend). It needs Linux (or WSL 2), because the image mounts the Docker, the X server and
the sound of your computer.

1. Install Docker ([prerequisites](prerequisites.md#docker)).
2. Download [`compose.cli.yml`](https://github.com/URV-teacher/bmde/blob/master/compose.cli.yml), which runs `bmde`
   in its image with everything it needs, and create the folder of your `bmde.toml` (even if you do not have one):
    ```shell
    mkdir -p ~/.config/bmde
    curl -fsSLo ~/.config/bmde/compose.cli.yml https://raw.githubusercontent.com/URV-teacher/bmde/master/compose.cli.yml
    ```
3. Add these lines to your `~/.bashrc` and open a new terminal: your user and the group of Docker, which the
   container needs, and a `bmde` command that runs it:
    ```shell
    export BMDE_UID="$(id -u)" BMDE_GID="$(id -g)" DOCKER_GID="$(stat -c %g /var/run/docker.sock)"
    bmde() { docker compose -f ~/.config/bmde/compose.cli.yml run --rm bmde "$@"; }
    ```
4. Use it as [the bmde CLI](#1-the-bmde-cli), from step 4: `bmde check`, `bmde build`, `bmde run`... It reads your
   `~/.config/bmde/bmde.toml` and the `bmde.toml` of the project.

`BMDE_TAG=1.15.0` pins a version of `bmde` and of the images it runs. Without compose, the same is:

```shell
docker run --rm -it --init --user "$(id -u):$(id -g)" --group-add "$(stat -c %g /var/run/docker.sock)" \
  -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w "$PWD" \
  -v "$XDG_RUNTIME_DIR:$XDG_RUNTIME_DIR" -e XDG_RUNTIME_DIR \
  -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY -e XAUTHORITY \
  -v "$HOME/.config/bmde:/config/bmde:ro" \
  aleixmt/bmde:latest build
```

The project, the runtime directory of your user and the X server are mounted at the same paths as in your computer
because the Docker of your computer, which runs the images of the components, looks for the paths that `bmde` gives it
in your computer, not in the container.

## 5. Makefile with Docker

The Makefile of your project runs each target in the Docker image of its component, so you work as in the
[host components](#2-host-components) method (`make`, `make run`, `make debug`) with only Docker in your computer.
There are no features of `bmde`, and git and the VPN are not included: use the ones of your computer, or another
method for them.

1. Install Docker ([prerequisites](prerequisites.md#docker)).
2. Replace the Makefile of your project by one of these, adaptations of the Makefile of the course
   ([`examples/Makefile`](https://github.com/URV-teacher/bmde/blob/master/examples/Makefile)):
    * [`examples/makefile-docker/Makefile`](https://github.com/URV-teacher/bmde/blob/master/examples/makefile-docker/Makefile):
      runs the images with `docker run`.
    * [`examples/makefile-compose/Makefile`](https://github.com/URV-teacher/bmde/blob/master/examples/makefile-compose/Makefile),
      with [`compose.yml`](https://github.com/URV-teacher/bmde/blob/master/examples/makefile-compose/compose.yml) next
      to it: runs the services of `compose.yml`, which you can edit (e.g. to extend an image with a Dockerfile, as
      explained in its comments).
3. Use it:
    ```shell
    make            # build, in aleixmt/devkitarm-nds
    make clean      # and any other target of the Makefile, also in aleixmt/devkitarm-nds
    make run        # run, in aleixmt/desmume
    make debug      # debug, in aleixmt/desmume and aleixmt/insight
    ```

Inside the containers (`DOCKER_FLAG`, which the Makefile passes to them), and wherever the components are installed
(`DEVKITARM` is set, e.g. with the [host components](#2-host-components) or in the shell of the
[development environment in Docker](#3-development-environment-in-docker)), these Makefiles are the Makefile of the
course as is, so they work in every method. `BMDE_TAG=1.15.0 make` pins the version of the images.

## 6. From the sources (developers)

For the developers of `bmde`: the `bmde` command runs the code of your copy of the repository, so your changes are
used right away. The [development installation](../development/installation.md) explains it:

```shell
git clone --recurse-submodules https://github.com/URV-teacher/bmde
cd bmde
make dev                # venv/ with bmde in editable mode, and the tools of development
venv/bin/bmde --help
```

To have that `bmde` in your `PATH` (e.g. to try your changes in your NDS projects), install the copy in editable mode
with pipx: `pipx install --editable .`. It follows the branch that is checked out. The components are installed as in
the other methods (e.g. Docker, or `scripts/install.sh`), and `docker buildx bake` builds their images from
`components/` ([images](../development/images.md)).
