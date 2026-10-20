# Docker images and component installation

Each component of the BMDE lives in its own repository (a submodule in `components/`) and can be installed in three
ways, all of them with the same install scripts of the component (`components/COMPONENT/scripts/install_*.sh`):

* In a Linux host, running the scripts directly (see
  [host components installation](../getting-started/host_components_installation.md)).
* In the Docker image of the component (e.g. `aleixmt/desmume`), used by the commands of the `bmde` CLI.
* In the full development environment (`aleixmt/bmde-full`), with all the components in one image.

## Conventions of the install scripts
* Programs are installed into `/URV/bmde/PROGRAM` (`BMDE_ROOT` changes `/URV/bmde`), and their environment (`PATH`,
  `DEVKITPRO`...) into `/etc/profile.d/bmde-PROGRAM.sh`.
* They can run as root (Docker) or as a user with `sudo` (hosts), and install their own dependencies with `apt-get`.
* They are idempotent: if the program is already in `/URV/bmde`, they only install its system dependencies and
  environment. The images use this to build a program once (e.g. DeSmuME in a build stage) and install it elsewhere.
* Files of the repository are taken from it when the script runs from a checkout (or from the Docker build context),
  and downloaded from GitHub otherwise.
* Tests (`scripts/test_*.sh`) are standalone too. `test_operation.sh` scripts test an operation of the BMDE, and may
  need other components (e.g. building a project to run it).

## Images
* `base/`: base image of all the images (`aleixmt/bmde-base`, Ubuntu 26.04). It loads the environment of
  `/etc/profile.d/bmde-*.sh` in every shell and in `bmde-exec COMMAND`, and provides the library of the entrypoints
  (`/usr/local/lib/bmde/entrypoint.sh`: graphical output with `MODE=host|vnc|none`, logging) and
  `bmde-install-display` (Xvfb / x11vnc, for the images with a graphical interface).
* `components/*/Dockerfile`: image of each component, built on the base image, which installs the component with its
  scripts, run from a bind mount of the build context.
* `shell/`: full development environment (`aleixmt/bmde-full`). It copies the programs already built by the images of
  the components, and runs the install scripts of all the components.

The Dockerfiles name the published images they use as stages (e.g. `FROM aleixmt/bmde-base:latest AS bmde-base`).
[`docker-bake.hcl`](https://github.com/URV-teacher/bmde/blob/master/docker-bake.hcl) builds every image replacing those
stages by the images being built, so a change in the base image or in a component is tested in all the images that use
it:

```shell
docker buildx bake full --load   # full development environment, and the images it needs
shell/test.sh                    # tests of every component inside it
```

## CI
* Each component runs the reusable workflows of this repository (`.github/workflows/component-image.yml` and
  `component-host.yml`): it builds its image and runs its tests inside it (publishing it from its default branch), and
  installs it in an Ubuntu machine with its install scripts and runs its tests.
* This repository builds every image with `docker-bake.hcl`, runs the tests of every component inside the full
  development environment (`shell/test.sh`) and publishes the base image and the full development environment from
  master (`.github/workflows/images.yml`).
