# Development environment of the bmde CLI: the full development environment of the BMDE (shell/Dockerfile), with every
# NDS tool, plus what developing and testing the CLI needs. Used by .devcontainer/bmde-dev/devcontainer.json.
#
# Built and published as aleixmt/bmde-dev by docker-bake.hcl (docker buildx bake dev), on the full development
# environment being built. To build it alone, on the published one:
#   docker build -t aleixmt/bmde-dev .devcontainer/bmde-dev

# docker-bake.hcl replaces this stage by the full development environment being built
FROM aleixmt/bmde-full:latest AS bmde-full

FROM bmde-full

USER root
# - python3-venv, python3-pip: `make dev` creates the venv of the project (the Python of the image is the one of the
#   system, newer than the 3.11 the project supports, which ruff and mypy still check against)
# - dosfstools, mtools: the integration tests create and read FAT images
# The Docker client comes from the docker-outside-of-docker feature of devcontainer.json, which uses the daemon of the
# host
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    python3-pip \
    dosfstools \
    mtools \
    && rm -rf /var/lib/apt/lists/*

USER bmde
