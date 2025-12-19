FROM ubuntu:24.04 AS build

# Required packages for building full feaatured DeSmuME
RUN apt-get update && apt-get install -y \
    build-essential  \
    gcc \
    make \
    autoconf \
    git \
    ca-certificates \
    cmake \
    libglu1-mesa-dev \
    libsdl2-dev \
    libpcap-dev \
    libgtk2.0-dev \
    libopenal-dev \
    libsoundtouch-dev \
    libagg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone and build DeSmuME CLI and GUI latest version
RUN git clone https://github.com/TASEmulators/desmume /desmume && \
    mkdir -p /desmume/desmume/src/frontend/posix/build && \
    cd /desmume/desmume/src/frontend/posix && \
    autoreconf -i && \
    ./configure --prefix=/usr --enable-gdb-stub && \
    make -j"$(nproc)" && \
    cd /desmume/desmume/src/frontend/posix/gtk2 && \
    make -j"$(nproc)" && \
    cd /desmume/desmume/src/frontend/posix && \
    make DESTDIR=/tmp/DeSmuME install


FROM ubuntu:24.04 AS runtime

# Runtime packages of desmume and x11 and VNC utilites
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libpcap-dev \
    libgtk2.0-dev \
    libopenal-dev \
    libsoundtouch-dev \
    libagg-dev \
    libosmesa6-dev \
    x11vnc \
    xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y --no-install-recommends \
    expect \
    less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p ~/.vnc && \
    touch ~/.vnc/passwd && \
    x11vnc -storepasswd "devopsil" ~/.vnc/passwd

# Copy the compiled binary from the builder stage
COPY --from=build /tmp/DeSmuME/usr/bin/desmume-cli /usr/bin
COPY --from=build /tmp/DeSmuME/usr/bin/desmume /usr/bin

# Change to use custom entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN export uid=1000 gid=1000 username=desmume && \
    mkdir -p /home/${username} && \
    mkdir -p /etc/sudoers.d/ && \
    echo "${username}:x:${uid}:${gid}:${username},,,:/home/${username}:/bin/bash" >> /etc/passwd && \
    echo "${username}:x:${uid}:" >> /etc/group && \
    echo "${username} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${username} && \
    chmod 0440 /etc/sudoers.d/${username} && \
    chown ${uid}:${gid} -R /home/${username}

USER desmume
ENV HOME /home/desmume

ENTRYPOINT ["/entrypoint.sh"]
CMD []