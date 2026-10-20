# BMDE full development environment: all the components of the BMDE (build, run, debug, patch, git, VPN, edit) in one
# image, built on the base image shared with the image of each component. The installation is done by the install
# scripts of the components, the same ones used by their images and to install them in a host.
#
# Build it with docker-bake.hcl of the repository root (docker buildx bake full), which provides the scripts of the
# components (named context "components") and uses the images of the components being built. To build it alone:
#   docker build --build-context components=components -f shell/Dockerfile shell

# Base image of the BMDE images and images of the components with programs that need a build. docker-bake.hcl replaces
# these stages by the images being built
FROM aleixmt/bmde-base:latest AS bmde-base
FROM aleixmt/bmde-linux:latest AS devkitarm
FROM aleixmt/desmume:latest AS desmume
FROM aleixmt/insight:latest AS insight
FROM aleixmt/dlditool:latest AS dlditool
FROM aleixmt/grit:latest AS grit
FROM aleixmt/vscode:latest AS vscode

FROM bmde-base

RUN bmde-install-display

# Programs built by the images of the components; their install scripts find them and do not build them again
COPY --from=devkitarm /URV/bmde/devkitPro /URV/bmde/devkitPro
COPY --from=desmume /URV/bmde/DeSmuME_0.9.11 /URV/bmde/DeSmuME_0.9.11
COPY --from=insight /URV/bmde/insight /URV/bmde/insight
COPY --from=dlditool /URV/bmde/dlditool /URV/bmde/dlditool
COPY --from=grit /URV/bmde/grit /URV/bmde/grit
COPY --from=vscode /URV/bmde/vscode /URV/bmde/vscode

RUN --mount=type=bind,from=components,target=/components \
    cd /components \
    && devkitarm-nds-docker/scripts/install_make.sh \
    && devkitarm-nds-docker/scripts/install_devkitarm.sh \
    && devkitarm-nds-docker/scripts/install_libnds.sh \
    && devkitarm-nds-docker/scripts/install_examples.sh \
    && desmume-docker/scripts/install_desmume.sh \
    && desmume-docker/scripts/install_wrapper.sh \
    && insight-docker/scripts/install_insight.sh \
    && insight-docker/scripts/install_gdb_multiarch.sh \
    && insight-docker/scripts/install_wrapper.sh \
    && dlditool-docker/scripts/install_dlditool.sh \
    && grit-docker/scripts/install_grit.sh \
    && git-urv-vpn-docker/scripts/install_ssh.sh \
    && git-urv-vpn-docker/scripts/install_git.sh \
    && git-urv-vpn-docker/scripts/install_vpn.sh \
    && vscode-arm-syntax-docker/scripts/install_vscode.sh \
    && apt-get install -y --no-install-recommends sudo \
    && rm -rf /var/lib/apt/lists/*

COPY --chmod=755 entrypoint.sh /entrypoint.sh

# Development user, with sudo for the tasks that need root (e.g. connecting to the VPN)
RUN useradd --create-home --uid 1000 --shell /bin/bash bmde \
    && echo "bmde ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/bmde \
    && chmod 0440 /etc/sudoers.d/bmde
USER bmde
# Extensions are installed for the user
RUN --mount=type=bind,from=components,target=/components \
    /components/arm-syntax-vscode-extension/scripts/install_extension.sh
WORKDIR /home/bmde

ENTRYPOINT ["/entrypoint.sh"]
CMD []
