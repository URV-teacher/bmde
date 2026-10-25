# Components installation

The `bmde` CLI does not build, run or debug anything by itself: each command wraps a **component** of the BMDE, a tool
of the course (devkitARM, DeSmuME, Insight...). Every [installation method](installation.md) needs some of them,
installed in one of these ways, which are always the same and can be mixed (e.g. build with the devkitARM of your
computer and run in Docker):

* [Docker](#docker-components): the image of the component, which the `docker` backend of `bmde` runs. Nothing to
  install besides Docker.
* [Host](#host-components): the component installed in your computer by `scripts/install.sh`, which the `host`
  backend of `bmde` and the Makefiles of the course use.
* [Flatpak](#flatpak-desmume): only DeSmuME, for the `flatpak` backend of `bmde run`.

| Component   | Used by                                  | Docker image           | `scripts/install.sh` | Flatpak |
|-------------|------------------------------------------|------------------------|----------------------|---------|
| `devkitarm` | `bmde build`, `make`                     | `aleixmt/bmde-linux`   | ✅                   |         |
| `desmume`   | `bmde run`, `make run`                   | `aleixmt/desmume`      | ✅                   | ✅      |
| `insight`   | `bmde debug`, `make debug`               | `aleixmt/insight`      | ✅                   |         |
| `dlditool`  | `bmde patch`                             | `aleixmt/dlditool`     | ✅                   |         |
| `grit`      | converting images into graphics data     | `aleixmt/grit`         | ✅                   |         |
| `git`       | `bmde git`, git                          | `aleixmt/git-sshpass`  | ✅                   |         |
| `vpn`       | `bmde git` (VPN of the URV)              | `aleixmt/forticlient`  | ✅                   |         |
| `vscode`    | editing, with the ARM assembly extension | `aleixmt/vscode`       | ✅                   |         |

## Docker components

1. Install Docker and let your user run it, as explained in the [prerequisites](prerequisites.md#docker).
2. That's all: the first time a command of `bmde` uses the `docker` backend, it downloads the image of its component
   (and on every run it checks for a newer one).

To download the images in advance (e.g. before a lab session, or to work offline later), use the `--docker` option of
[`scripts/install.sh`](#host-components), with the components you want (all of them by default):

```shell
bmde/scripts/install.sh --docker devkitarm desmume insight
```

`bmde` runs the images of its own version (`bmde` 1.15.0 runs `aleixmt/desmume:1.15.0`); `docker.image_tag` of
`bmde.toml` pins another one (see [images](../development/images.md#versions)).

## Host components

`scripts/install.sh` of the repository of `bmde` installs the components in an Ubuntu / Debian computer, with the
install scripts of each component: the same ones that build their Docker images, so both installations are the same.
It needs `sudo` and an internet connection.

1. Download the repository of `bmde` (the script checks out the repositories of the components it installs):
    ```shell
    git clone https://github.com/URV-teacher/bmde
    ```
2. Run the script **as your user**, not with `sudo` (it calls `sudo` itself, and the extension of VS Code is installed
   for the user that runs it). With no arguments it installs every component; with arguments, only those:
    ```shell
    bmde/scripts/install.sh --list                     # the components
    bmde/scripts/install.sh                            # every component
    bmde/scripts/install.sh devkitarm desmume insight  # only these
    bmde/scripts/install.sh --dry-run                  # only print what it would do
    ```
3. Open a new session (or log out and in), which loads the environment of the components (`PATH`, `DEVKITPRO`,
   `DESMUME`...). To load it in the current terminal:
    ```shell
    for f in /etc/profile.d/bmde-*.sh; do . "$f"; done
    ```
4. Check the installation, e.g. with `arm-none-eabi-gcc --version`, or with `bmde check` if you use the CLI.

For each component, the script downloads its assets (`scripts/download_assets.sh` of the component) and runs its
install scripts (`src/install_*.sh`), always in the order that the components depend on each other. The programs go to
`/URV/bmde` (set `BMDE_ROOT` to change it) and their environment to `/etc/profile.d/bmde-*.sh`. Running it again is
safe: a program that is already installed is not built again. Some components take a while: DeSmuME is built from its
sources.

Insight needs the toolchain of Ubuntu 14.04 to be built, so the script takes it from the Docker image of Insight
(`aleixmt/insight`), which needs Docker. Without Docker, build its tarball elsewhere with
`components/insight-docker/scripts/build_tarball.sh` and pass it in `INSIGHT_TARBALL`.

Without a copy of the repository, the script can be run directly from GitHub, and then it clones the components into
`~/.cache/bmde/components`:

```shell
curl -fsSL https://raw.githubusercontent.com/URV-teacher/bmde/master/scripts/install.sh | bash -s -- devkitarm
```

The [host components installation guide](host_components_installation.md) explains each install script, step by step,
and how to test each component. To uninstall the components, remove `/URV/bmde` and `/etc/profile.d/bmde-*.sh` (the
packages installed with `apt` stay).

## Flatpak DeSmuME

`bmde run --backend flatpak` runs the DeSmuME of Flathub, a newer version than the 0.9.11 of the course. It only opens
the ROM: the debug, FAT image and controls options of `bmde run` need the `docker` or `host` backends.

```shell
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub org.desmume.DeSmuME
```

## Choosing the backend of each command

By default, each command of `bmde` uses the first backend that is available, by order of preference: `docker` and then
`host` (`docker`, `flatpak` and `host` for `bmde run`, and `host` first for `bmde debug`). `bmde check` shows which ones
are available. To choose one, use `--backend` (e.g. `bmde build --backend host`), or set it in `bmde.toml`:

```toml
[build.execution_settings]
backend = "host"

[run.execution_settings]
backend = "docker"
```
