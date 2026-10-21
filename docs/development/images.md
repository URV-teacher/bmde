# Docker images and component installation

Each component of the BMDE lives in its own repository (a submodule in `components/`) and can be installed in three
ways, all of them with the same install scripts of the component (`components/COMPONENT/src/install_*.sh`):

* In a Linux host, running the scripts directly (see
  [host components installation](../getting-started/host_components_installation.md)).
* In the Docker image of the component (e.g. `aleixmt/desmume`), used by the commands of the `bmde` CLI.
* In the full development environment (`aleixmt/bmde-full`), with all the components in one image.

## Structure of the repository of a component
* `scripts/`: scripts used in the repository, e.g. `download_assets.sh`, which downloads the assets of the component.
* `src/`: install scripts, and the scripts that end up in the image (entrypoints, helper scripts...).
* `config/`: configuration files that end up in the image (e.g. the default `desmume.ini` of the course).
* `test/`: tests, run in the image or in a host. `test/image/` has the tests that run the image from outside (e.g. with
  `docker run`), which take the image as argument.
* `assets/`: data used to build the image that we do not maintain: files downloaded from outside the repository by
  `scripts/download_assets.sh` (not in git), and the few that are not published anywhere else, stored in git (e.g. the
  libnds of the course).
* `Dockerfile`: the image of the component.

## Download and build stages
Downloading and building are separate stages. `scripts/download_assets.sh [ASSET...]` downloads every file that comes
from outside the repository into `assets/`: if a file is already there it only checks it, and if it is not, it
downloads it and then checks it. Every file with a fixed version is checked against its pinned SHA-256 (the files that
are always the latest version cannot be), and the script fails if any file could not be downloaded or does not match.

The install scripts (and the tests) never access the internet: they only take files from the repository, and
fail asking to run the download script if an asset is missing. So the images, the CI and the hosts always run the
download script first. Every external resource is listed in [external resources](external-resources.md).

## Conventions of the install scripts
* Programs are installed into `/URV/bmde/PROGRAM` (`BMDE_ROOT` changes `/URV/bmde`), and their environment (`PATH`,
  `DEVKITPRO`...) into `/etc/profile.d/bmde-PROGRAM.sh`.
* They can run as root (Docker) or as a user with `sudo` (hosts), and install their own dependencies with `apt-get`.
* They are idempotent: if the program is already in `/URV/bmde`, they only install its system dependencies and
  environment. The images use this to build a program once (e.g. DeSmuME in a build stage) and install it elsewhere.
* They run from a checkout of the repository (or from a bind mount of the Docker build context), and take every file
  from it: `src/`, `config/` and `assets/`.
* Tests (`test/test_*.sh`) are standalone too. `test_operation.sh` scripts test an operation of the BMDE, and may
  need other components (e.g. building a project to run it).

## Images
* `base/`: base image of all the images (`aleixmt/bmde-base`, Ubuntu 26.04). It loads the environment of
  `/etc/profile.d/bmde-*.sh` in every shell and in `bmde-exec COMMAND`, and provides the library of the entrypoints
  (`/usr/local/lib/bmde/entrypoint.sh`: graphical output with `MODE=host|vnc|none`, logging) and
  `bmde-install-display` (Xvfb / x11vnc, for the images with a graphical interface).
* `components/*/Dockerfile`: image of each component, built on the base image, which installs the component with its
  scripts, run from a bind mount of the build context (with the assets already downloaded).
* `shell/`: full development environment (`aleixmt/bmde-full`). It copies the programs already built by the images of
  the components, and runs the install scripts of all the components. It is also the image of the dev container of
  the students (`.devcontainer/nds/`).
* `.devcontainer/bmde-dev/`: development environment of the bmde CLI (`aleixmt/bmde-dev`), the full development
  environment plus Python and the packages of the integration tests (the Docker client comes from a feature of the dev
  container). Image of the dev container `.devcontainer/bmde-dev/`.

The Dockerfiles name the published images they use as stages (e.g. `FROM aleixmt/bmde-base:latest AS bmde-base`).
[`docker-bake.hcl`](https://github.com/URV-teacher/bmde/blob/master/docker-bake.hcl) builds every image replacing those
stages by the images being built, so a change in the base image or in a component is tested in all the images that use
it:

```shell
for script in components/*/scripts/download_assets.sh; do "${script}"; done   # assets of every component
docker buildx bake full --load   # full development environment, and the images it needs
shell/test.sh                    # tests of every component inside it
docker buildx bake dev --load    # development environment of the CLI
```

## Versions

Every image built by `docker-bake.hcl`, the ones of the components included, is pushed as `sha-<commit>` on every push
to master, tagged `latest` once it is released and, when that push releases a new version of bmde, also with that
version: `X.Y.Z`, `X.Y` and `X` (e.g. `aleixmt/desmume:1.15.0`, `:1.15` and `:1`). The tags come from the `TAG` and
`VERSION` variables of `docker-bake.hcl`. The repositories of the components also publish `latest` of their own image.

The CLI of a release runs the images tagged with its version (bmde 1.15.0 runs `aleixmt/desmume:1.15.0`), so it keeps
working with the environment it was tested with; a development version of the CLI runs `latest`. To pin another
environment, set the tag in `bmde.toml` (or `BMDE_DOCKER_IMAGE_TAG`), e.g. a known-good build:

```toml
[docker]
image_tag = "sha-0123456789abcdef0123456789abcdef01234567"
```

## CI
* Each component runs the reusable workflows of this repository (`.github/workflows/component-image.yml` and
  `component-host.yml`): it downloads its assets, builds its image, runs its tests inside it and its tests of
  `test/image/` (publishing it from its default branch), and installs it in an Ubuntu machine with its install scripts
  and runs its tests.
* This repository downloads the assets of every component, builds every image with `docker-bake.hcl` and runs the tests
  of every component inside the full development environment (`shell/test.sh`) on every pull request
  (`.github/workflows/images.yml`).
* On every push to master, `.github/workflows/release.yml` runs, in order and each step only if everything before it
  succeeded:
    1. the checks: lint, tests, and the images, built, tested and pushed with only the tag `sha-<commit>`;
    2. semantic-release, which tags the new version (if the commits make one) and creates its GitHub release;
    3. the publication of the tested images (retagged, not rebuilt) as `latest` and, if there is a new version, `X.Y.Z`,
       `X.Y` and `X`;
    4. the upload of the package to PyPI, only if there is a new version. After the images, because the CLI of the
       release runs the images of its version.

  If a step fails, nothing after it is published. The `sha-<commit>` tags stay in Docker Hub as a record of every
  tested build.
