# Template to extend the full development environment of the BMDE (aleixmt/bmde-full) with the tools that your project
# needs. Copy it next to the compose.yml of this template, in the root of your project, and replace the image of the
# compose.yml by `build: .`; `docker compose build` builds it (and `docker compose run --rm shell` too, the first
# time).

FROM aleixmt/bmde-full:latest

# The image runs as the user bmde, which can use sudo; packages are installed as root
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    tree \
    && rm -rf /var/lib/apt/lists/*
USER bmde
