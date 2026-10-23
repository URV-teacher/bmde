# External resources

The BMDE components need files that come from the internet, from sources that are not under our control. This page
lists all of them, so we know what can break, disappear or change without notice.

Downloading and building are separate stages (see [Docker images](images.md)):

1. **Download**: `scripts/download_assets.sh` of each component downloads its **assets** into its `assets/` folder
   (not in git). If an asset is already there, it only checks it; if it is not, it downloads it and then checks it. The
   script fails if any asset could not be downloaded or does not match its checksum. Run it with names of assets as
   arguments to download only those. The download logic is the same in every component: `scripts/download_lib.sh`,
   whose canonical copy is the one of bmde, copied into each component by `make fmt` and checked by `make lint`.
2. **Build**: the install scripts (`src/`) and the tests (`test/`) only take files from the repository (`src/`,
   `config/` and `assets/`), never from the internet. The only exceptions are the packages of the system, installed with
   APT, and the Docker base images, both verified by their own tools.

The **check** column says how the download script knows that an asset is the expected one:

* **SHA-256**: the asset is checked against a pinned SHA-256, and the script fails if it does not match.
* **SHA-256 of the files**: the asset is checked against the pinned SHA-256 of the files it contains, not of the file
  itself (used for the sources of Insight, which are packed by the download script).
* **Stored in the repository**: a few assets are not published anywhere else, so they are stored in git, in the
  `assets/` folder too, and the download script only checks them.
* **Not checked**: the asset is always the latest version of its source, so it cannot be pinned. It is only downloaded
  if it is not in `assets/`: delete it to download the latest version again.

## Common to every component

Installed during the build, not by the download scripts.

| Resource | Source | Purpose | Check |
|----------|--------|---------|-------|
| `ubuntu:26.04` image | [Docker Hub](https://hub.docker.com/_/ubuntu) | Base of `aleixmt/bmde-base` (`base/Dockerfile`), on which every image is built | Docker (TLS, image digest) |
| `xvfb`, `xauth`, `x11vnc`, `xfonts-base` | `archive.ubuntu.com` (APT) | Virtual display and VNC server of the graphical images, installed by `bmde-install-display` | APT signatures |
| Other packages of the system | `archive.ubuntu.com` (APT) | Dependencies installed by the install scripts with `apt-get`, listed in each section below | APT signatures |

## devkitarm-nds-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `devkitARM_r46-x86_64-linux.tar.bz2` | <https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2> | devkitARM r46, the toolchain of the course. devkitPro no longer distributes old versions, so it comes from a community mirror | SHA-256 |
| `libnds.tar.bz2` | Stored in the repository | libnds 1.6.2 of devkitPro, with dswifi, maxmod, libfat 1.1.0 and libfilesystem, as used by the course. Not published anywhere else in this form | SHA-256 |
| `examples.tar.bz2` | Stored in the repository | NDS examples of devkitPro, as used by the course. Not published anywhere else in this form | SHA-256 |
| `hello-world-nds.tar.gz` | <https://github.com/URV-teacher/hello-world-nds/archive/refs/heads/master.tar.gz> | Hello world project of the course, built by `test/test_operation.sh` | Not checked |

Installed during the build: `make` and `bzip2` (APT).

`test/test_windows_builds.sh` compares the examples built by the image with the binaries built by the Windows BMDE,
using their SHA-1, stored in the repository (`test/windows_builds.sha1`): it needs no external resources.

## desmume-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `desmume_0.9.11.orig.tar.gz` | <https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/desmume/0.9.11-3build2/desmume_0.9.11.orig.tar.gz>, falling back to <http://archive.ubuntu.com/ubuntu/pool/universe/d/desmume/desmume_0.9.11.orig.tar.gz> | Upstream sources of DeSmuME 0.9.11, the version of the course, built with HUD and GDB stub | SHA-256 |
| `desmume_0.9.11-3build2.diff.gz` | <https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/desmume/0.9.11-3build2/desmume_0.9.11-3build2.diff.gz>, falling back to <http://archive.ubuntu.com/ubuntu/pool/universe/d/desmume/desmume_0.9.11-3build2.diff.gz> | Patches of the Ubuntu package, which make the 0.9.11 sources build with current compilers | SHA-256 |
| `hello-world-nds.nds` | <https://github.com/URV-teacher/hello-world-nds/releases/download/v1.0/hello-world-nds.nds> | ROM run by `test/test_desmume.sh` and `test/test_gdbport.sh` | SHA-256 |
| `filesystem-nds.nds` | Built from the sources of [filesystem-nds](https://github.com/URV-teacher/filesystem-nds) at a fixed commit (<https://github.com/URV-teacher/filesystem-nds/archive/0121751d8ce58cd63fd959653b1c2f786f50d124.tar.gz>), with the local devkitARM and dlditool or with the images `aleixmt/bmde-linux` and `aleixmt/dlditool` | ROM run by `test/image/test_fat.sh`, which checks the files that it writes in the FAT image. The build is reproducible | SHA-256 |
| `hello-world-nds.tar.gz` | <https://github.com/URV-teacher/hello-world-nds/archive/refs/heads/master.tar.gz> | Hello world project of the course, built and run by `test/test_operation.sh` | Not checked |

Installed during the build (APT): the build dependencies of DeSmuME (`build-essential`, `autoconf`, `automake`,
`intltool`, `pkg-config`, `patch`, `libgtk2.0-dev`, `libsdl1.2-dev`, `libagg-dev`, `libsoundtouch-dev`,
`libopenal-dev`, `libosmesa6-dev`, `libglu1-mesa-dev`, `libtinyxml-dev`, `libpcap-dev`, `zlib1g-dev`), and its runtime
dependencies (the packages of the libraries it links, computed when it is built, and `python3`).

The FAT image used as the CompactFlash card of the emulator is not downloaded: `scripts/create_fat_image.sh` creates an
empty one with `mkfs.fat` (package `dosfstools`). `test/image/test_fat.sh` also needs `mtools`, installed with APT in
the machine that runs it.

Launchpad keeps the source files of every Ubuntu package permanently. The Ubuntu archive drops them once no supported
release uses the package. The upstream tarball is also identical to `desmume-0.9.11.tar.gz` of
[SourceForge](https://sourceforge.net/projects/desmume/files/desmume/0.9.11/), if both sources ever disappear.

## insight-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `insight-7.3.50.20110803-cvs.tar.xz` | CVS repository of sourceware.org, `rsync://sourceware.org/src-cvs/` | Sources of Insight 7.3.50.20110803-cvs, the version of the Windows BMDE, built by the image (and by `scripts/build_tarball.sh` into a tarball to install it in hosts). That version was never released as a tarball, so `scripts/fetch_source.sh` reconstructs it from the CVS history (~900 MB download with `rsync`, checked out with `cvs`): `gdb/` as of 2011-08-03, and `bfd/`, `opcodes/` and `include/` as of 2011-08-01 | SHA-256 of the files |
| `hello-world-nds.tar.gz` | <https://github.com/URV-teacher/hello-world-nds/archive/refs/heads/master.tar.gz> | Hello world project of the course, built and debugged by `test/test_operation.sh` | Not checked |

Installed during the build:

* `ubuntu:14.04` image ([Docker Hub](https://hub.docker.com/_/ubuntu)): builder of Insight, since its 2011 sources only
  compile with a toolchain of their time. Ubuntu 14.04 is end of life.
* Build dependencies (APT, Ubuntu 14.04): `build-essential`, `bison`, `flex`, `m4`, `texinfo`, `libncurses5-dev`,
  `libexpat1-dev`, `zlib1g-dev`, `libx11-dev`, `xz-utils`.
* `gdb-multiarch`, the alternative debugger, and the runtime libraries of Insight (`libx11-6`, `libexpat1`, `zlib1g`)
  (APT).

The download script needs `rsync` and `cvs` to reconstruct the sources of Insight. sourceware.org only serves this
repository through `rsync`: if it stops doing so, the image can no longer be built from scratch, but the last source
tarball stored in git (history of insight-docker, `src/insight-7.3.50.20110803-cvs.tar.xz`) has the same sources.

## dlditool-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `dlditool-linux-x86_64.zip` | <https://www.chishm.com/DLDI/downloads/dlditool-linux-x86_64.zip> | dlditool, which patches the NDS ROMs with DLDI drivers so they can use the FAT library | SHA-256 |
| `mpcf.dldi` | <https://www.chishm.com/DLDI/downloads/mpcf.dldi> | DLDI driver of the M3 / G6 / SuperCard CompactFlash, the one used by the course | SHA-256 |
| `libfatdir.nds` | Built from the `libfatdir` example of devkitPro (installed by devkitarm-nds-docker), with the local devkitARM or with the image `aleixmt/bmde-linux` ([Docker Hub](https://hub.docker.com/r/aleixmt/bmde-linux)) | ROM patched by `test/test_dlditool.sh`: it uses libfat, so it has a DLDI section. The build is reproducible | SHA-256 |

Installed during the build: `unzip` (APT).

## grit-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `devkitARM_r46-x86_64-linux.tar.bz2` | <https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2> | Only `grit` (the image converter of devkitARM r46) is extracted from it. Not used if devkitARM is already installed | SHA-256 |

Installed during the build: `bzip2` (APT). The image used by `test/test_grit.sh` is generated by the test itself.

## git-urv-vpn-docker

No assets. Installed during the build (APT): `git`, `gitk`, `expect`, `jq`, `openssh-client` (git client of the course
and the tools of its helper scripts) and `openfortivpn` (FortiClient-compatible VPN client, to reach the git server of
the university).

## vscode-arm-syntax-docker

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `vscode.deb` | <https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64> | Visual Studio Code | Not checked |
| `arm-syntax-vscode-extension/src/install_extension.sh` | <https://raw.githubusercontent.com/URV-teacher/arm-syntax-vscode-extension/main/src/install_extension.sh> | Install script of the extension of the ARM assembly syntax of the course (`docker-bake.hcl` of bmde uses the checkout of the extension instead) | Not checked |
| `arm-syntax-vscode-extension/assets/arm-syntax-vscode-extension.vsix` | Latest release of [arm-syntax-vscode-extension](https://github.com/URV-teacher/arm-syntax-vscode-extension/releases) (found with the API of GitHub, `api.github.com`) | The extension (`docker-bake.hcl` of bmde uses the checkout of the extension instead) | Not checked |

Installed during the build: the dependencies of VS Code declared by its package (APT).

## arm-syntax-vscode-extension

| Asset | Source | Purpose | Check |
|-------|--------|---------|-------|
| `arm-syntax-vscode-extension.vsix` | Latest release of [arm-syntax-vscode-extension](https://github.com/URV-teacher/arm-syntax-vscode-extension/releases) (found with the API of GitHub, `api.github.com`) | The extension, installed by `src/install_extension.sh` (unless `VSIX` gives another `.vsix`) | Not checked |

## Resources of URV-teacher

These assets are under our control, but they are downloaded from GitHub like any other asset: the ROM and the project
of `hello-world-nds` (desmume-docker, devkitarm-nds-docker, insight-docker), the ROM of `filesystem-nds`
(desmume-docker), the extension and its install script (vscode-arm-syntax-docker, arm-syntax-vscode-extension), and the
images `aleixmt/bmde-linux` and `aleixmt/dlditool`, which build test ROMs (desmume-docker, dlditool-docker).
