# Prerequisites

What each [installation method](installation.md) needs in your computer. The components of the BMDE (devkitARM,
DeSmuME...) are explained in [components installation](components.md).

## Operating system

The BMDE is developed and tested in Ubuntu Linux (24.04 and 26.04), the recommended operating system. The install
scripts of the [host components](components.md#host-components) need Ubuntu or Debian (they use `apt`); the methods
that only need Docker also work in other Linux distributions and, with a [dev container](devcontainer.md), in Windows
(WSL 2) and macOS.

## Root permissions

Installing the host components, Docker or Flatpak needs root permissions, usually acquired with `sudo`.

## Python

[The bmde CLI](installation.md#1-the-bmde-cli) needs Python 3.11 or newer, and [pipx](https://pipx.pypa.io), which
installs Python programs like `bmde` in an environment of their own, with their command in your `PATH`. In Ubuntu /
Debian:

```shell
sudo apt install -y python3 pipx
pipx ensurepath   # then open a new terminal
```

## `make`

The Makefiles of the NDS projects need `make`, which the `devkitarm` [host component](components.md#host-components)
installs. Developing `bmde` needs it too ([development installation](../development/installation.md)). In Ubuntu /
Debian:

```shell
sudo apt install -y make
```

## Docker

The [Docker components](components.md#docker-components), and the methods that run the BMDE in Docker, need Docker.
Install it following the [official Docker installation guide][docker-installation-guide]. In Ubuntu, with `apt`:

```shell
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

`bmde` and the Makefiles call `docker` directly, so your user must be able to run it. Add your user to the `docker`
group (then reboot, or log out and log in):

```shell
sudo usermod -aG docker $USER
```

## Flatpak

Only for the [Flatpak DeSmuME](components.md#flatpak-desmume). Follow the [official installation guide][flathub-setup-url];
in Ubuntu:

```shell
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

[flathub-setup-url]: https://flathub.org/en/setup
[docker-installation-guide]: https://docs.docker.com/engine/install/ubuntu/
