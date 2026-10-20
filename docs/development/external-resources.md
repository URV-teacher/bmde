# External resources

The BMDE components download some of their files from the internet when they are built or installed, from sources
that are not under our control. This page lists them, so we know what can break, disappear or change without notice.

For each file, the **integrity** column says how we know we get the expected file:

* **SHA-256**: the script checks the download against a pinned checksum, and fails if it changed.
* **TLS**: the file comes over HTTPS with the certificate verified, but its content is not pinned.
* **None**: neither, so it relies only on the source being trustworthy.

Every fixed version of a third-party file is pinned with SHA-256. The ones that are not are either always the latest
version (so they change by design), Docker images, packages of APT (which verifies their signatures) or resources of
our own repositories.

Resources downloaded from other repositories of [URV-teacher](https://github.com/URV-teacher) are listed at the end,
since they are under our control.

## Common to every component

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `ubuntu:26.04` image | [Docker Hub](https://hub.docker.com/_/ubuntu) | Base of `aleixmt/bmde-base` (`base/Dockerfile`), on which every image is built | TLS |
| Ubuntu packages | `archive.ubuntu.com` (APT) | System packages installed by the install scripts with `apt-get`, listed in each section below | APT signatures |
| `xvfb`, `xauth`, `x11vnc`, `xfonts-base` | `archive.ubuntu.com` (APT) | Virtual display and VNC server of the graphical images, installed by `bmde-install-display` | APT signatures |

## devkitarm-nds-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `devkitARM_r46-x86_64-linux.tar.bz2` | <https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2> | devkitARM r46, the toolchain of the course. devkitPro no longer distributes old versions, so it comes from a community mirror | SHA-256 |
| `make` and `bzip2` (APT) | `archive.ubuntu.com` | Building the projects, extracting devkitARM | APT signatures |

`data/libnds.tar.bz2` (libnds and libfat of the course) and `data/examples.tar.bz2` (the devkitPro NDS examples) are
stored in the repository, so they are not downloaded.

## desmume-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `desmume_0.9.11.orig.tar.gz` | <https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/desmume/0.9.11-3build2/desmume_0.9.11.orig.tar.gz>, falling back to <http://archive.ubuntu.com/ubuntu/pool/universe/d/desmume/desmume_0.9.11.orig.tar.gz> | Upstream sources of DeSmuME 0.9.11, the version of the course, built with HUD and GDB stub | SHA-256 |
| `desmume_0.9.11-3build2.diff.gz` | <https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/desmume/0.9.11-3build2/desmume_0.9.11-3build2.diff.gz>, falling back to <http://archive.ubuntu.com/ubuntu/pool/universe/d/desmume/desmume_0.9.11-3build2.diff.gz> | Patches of the Ubuntu package, which make the 0.9.11 sources build with current compilers | SHA-256 |
| Build dependencies (APT) | `archive.ubuntu.com` | Compiling DeSmuME: `build-essential`, `autoconf`, `automake`, `intltool`, `pkg-config`, `patch`, `libgtk2.0-dev`, `libsdl1.2-dev`, `libagg-dev`, `libsoundtouch-dev`, `libopenal-dev`, `libosmesa6-dev`, `libglu1-mesa-dev`, `libtinyxml-dev`, `libpcap-dev`, `zlib1g-dev` | APT signatures |
| Runtime dependencies (APT) | `archive.ubuntu.com` | Running DeSmuME: the packages of the libraries it links, computed when it is built, and `python3` | APT signatures |

Launchpad keeps the source files of every Ubuntu package permanently. The Ubuntu archive drops them once no supported
release uses the package. The upstream tarball is also identical to `desmume-0.9.11.tar.gz` of
[SourceForge](https://sourceforge.net/projects/desmume/files/desmume/0.9.11/), if both sources ever disappear.

## insight-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `ubuntu:14.04` image | [Docker Hub](https://hub.docker.com/_/ubuntu) | Builder of Insight: its 2011 sources only compile with a toolchain of their time. Ubuntu 14.04 is end of life | TLS |
| Build dependencies (APT) | `archive.ubuntu.com` (Ubuntu 14.04) | Compiling Insight: `build-essential`, `bison`, `flex`, `m4`, `texinfo`, `libncurses5-dev`, `libexpat1-dev`, `zlib1g-dev`, `libx11-dev` | APT signatures |
| `gdb-multiarch` and runtime libraries (APT) | `archive.ubuntu.com` | The alternative debugger, and the libraries Insight needs at runtime (`libx11-6`, `libexpat1`, `zlib1g`) | APT signatures |
| CVS repository of GDB / Insight | `rsync://sourceware.org/src-cvs/` | Only used by `scripts/fetch_source.sh` to regenerate `src/insight-7.3.50.20110803-cvs.tar.xz` (~900 MB download), which is stored in the repository. Not used by the build | None |

The Insight sources (`src/insight-7.3.50.20110803-cvs.tar.xz`) are stored in the repository: that version was never
released as a tarball, and it is rebuilt from the CVS history of sourceware.org.

## dlditool-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `dlditool-linux-x86_64.zip` | <https://www.chishm.com/DLDI/downloads/dlditool-linux-x86_64.zip> | dlditool, which patches the NDS ROMs with DLDI drivers so they can use the FAT library | SHA-256 |
| `mpcf.dldi` | <https://www.chishm.com/DLDI/downloads/mpcf.dldi> | DLDI driver of the M3 / G6 / SuperCard CompactFlash, the one used by the course | SHA-256 |

The test ROM of `scripts/test_dlditool.sh` is built from the `libfatdir` example installed by devkitarm-nds-docker.

## grit-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `devkitARM_r46-x86_64-linux.tar.bz2` | <https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2> | Only `grit` (the image converter of devkitARM r46) is extracted from it | SHA-256 |

## git-urv-vpn-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| `git`, `gitk`, `expect`, `jq`, `openssh-client` (APT) | `archive.ubuntu.com` | git client of the course, and the tools of its helper scripts | APT signatures |
| `openfortivpn` (APT) | `archive.ubuntu.com` | FortiClient-compatible VPN client, to reach the git server of the university | APT signatures |

## vscode-arm-syntax-docker

| File | URL | Purpose | Integrity |
|------|-----|---------|-----------|
| Visual Studio Code `.deb` | <https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64> | Visual Studio Code. It is always the latest stable version, so the image changes with each release | TLS |

## arm-syntax-vscode-extension

Downloads nothing from third parties: see the resources from URV-teacher repositories below.

## Resources from URV-teacher repositories

These are under our control, but are downloaded from GitHub rather than read from the repository being built.

| File | URL | Used by | Purpose | Integrity |
|------|-----|---------|---------|-----------|
| `hello-world-nds.nds` (v1.0) | <https://github.com/URV-teacher/hello-world-nds/releases/download/v1.0/hello-world-nds.nds> | desmume-docker (`test/test_desmume.sh`, `test/test_gdbport.sh`) | ROM run by the tests of DeSmuME | SHA-256 |
| hello-world-nds repository | <https://github.com/URV-teacher/hello-world-nds.git> | `test_operation.sh` of desmume-docker, devkitarm-nds-docker and insight-docker | Project of the course built and run by the tests of the whole workflow | TLS |
| Insight release tarball | <https://github.com/URV-teacher/insight-docker/releases/latest/download/insight-7.3.50.20110803-cvs-linux-x86_64.tar.xz> | insight-docker (`scripts/install_insight.sh`, in hosts) | Insight already built, so hosts do not need to compile it | TLS |
| `install_extension.sh` | <https://raw.githubusercontent.com/URV-teacher/arm-syntax-vscode-extension/main/scripts/install_extension.sh> | vscode-arm-syntax-docker (`Dockerfile`) | Install script of the extension, when the image is built outside of bmde | TLS |
| Extension `.vsix` (latest release) | `https://github.com/URV-teacher/arm-syntax-vscode-extension/releases/download/v<version>/arm-syntax-vscode-extension-<version>.vsix` | arm-syntax-vscode-extension (`scripts/install_extension.sh`) | Extension of the ARM assembly syntax of the course | TLS |
| `aleixmt/bmde-linux` image | [Docker Hub](https://hub.docker.com/r/aleixmt/bmde-linux) | dlditool-docker (`scripts/test_dlditool.sh`) | Builds the test ROM when there is no local devkitARM | TLS |
| Files of the repository itself | `https://raw.githubusercontent.com/URV-teacher/<component>/master/...` | The install scripts of every component | Helper scripts and data, when an install script is run on its own outside of its repository | TLS |
