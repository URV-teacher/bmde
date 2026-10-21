# Base image of the BMDE images: the image of each component and the full development environment (shell/Dockerfile)
# are built on top of it, so all of them share the same system and can be combined.
FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

# Tools used by the install scripts of the components. The images with a graphical interface also install the X11 /
# VNC stack with bmde-install-display, which is not included here because of its size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    bzip2 \
    xz-utils \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# The image comes with the user "ubuntu" with UID 1000, which the BMDE images use for their own users
RUN userdel --remove ubuntu

COPY rootfs/ /

# Environment of the programs installed in /URV/bmde for non-interactive (BASH_ENV) and interactive shells
ENV BASH_ENV=/etc/bmde/env.sh
RUN echo '. /etc/bmde/env.sh' >> /etc/bash.bashrc \
    && mkdir -p /URV/bmde
