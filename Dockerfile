# The bmde CLI in Docker (aleixmt/bmde), for those who have Docker but not Python: `docker run aleixmt/bmde COMMAND`
# instead of `bmde COMMAND`. It is the development environment of the CLI (.devcontainer/bmde-dev/Dockerfile, which has
# every NDS tool and Python) with bmde installed from this checkout and a Docker client, so both of its backends work:
#   - docker: the CLI runs the images of the components with the Docker of the host, through its socket (Docker outside
#     of Docker). The daemon looks for the paths that the CLI mounts in the host, so the project, the runtime directory
#     of the user (sound, X authority, the secrets of git) and the X server are mounted at their path of the host.
#   - host: the tools of the image itself (make, desmume, insight...).
# compose.cli.yml of the repository root runs it with all of that (see docs/getting-started/installation.md).
#
# Built and published by docker-bake.hcl (docker buildx bake cli), on the development environment being built. To build
# it alone, on the published one:
#   docker build -t aleixmt/bmde .

# The Docker client, a static binary
FROM docker:29-cli AS docker-cli
# docker-bake.hcl replaces this stage by the development environment being built
FROM aleixmt/bmde-dev:latest AS bmde-dev

FROM bmde-dev

# Version of the package: hatch-vcs takes it from git, which is not in the build context (.dockerignore).
# docker-bake.hcl passes the VERSION of a release, and the default is a development version, whose CLI runs the
# latest images (see default_image_tag of src/bmde/core/docker.py)
ARG BMDE_VERSION=0.0.0.dev0

USER root
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
RUN --mount=type=bind,target=/src,rw \
    python3 -m venv /opt/bmde \
    && SETUPTOOLS_SCM_PRETEND_VERSION="${BMDE_VERSION}" /opt/bmde/bin/pip install --no-cache-dir /src \
    && ln -s /opt/bmde/bin/bmde /usr/local/bin/bmde

# The container runs with the UID of the user of the host (so the files it creates are theirs), who may not exist in
# the image: a HOME that any user can create (logs and cache of bmde, lost with the container), and the configuration
# of the user of the host mounted at /config/bmde (bmde.toml)
ENV HOME=/tmp/home \
    XDG_CONFIG_HOME=/config
USER bmde

# With the environment (PATH, DEVKITPRO...) of the tools of the host backends. Not the entrypoint of the full
# development environment, whose messages would be mixed with the output of the CLI: the windows of the host backends
# only need the DISPLAY of the host
ENTRYPOINT ["bmde-exec", "bmde"]
CMD ["--help"]
