FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    git \
    expect && \
    rm -rf /var/lib/apt/lists/* && \
    git config --global advice.detachedHead false

COPY ./src/git_clone.exp /git_clone.exp
RUN chmod +x /git_clone.exp

COPY ./src/git.exp /git.exp
RUN chmod +x /git.exp

COPY ./src/clone_repos.sh /clone_repos.sh
RUN chmod +x /clone_repos.sh

COPY git-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd -m -u 1000 app
USER app
ENV HOME=/home/app
WORKDIR /home/app

ENTRYPOINT ["/entrypoint.sh"]
#CMD []