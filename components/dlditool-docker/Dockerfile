# Use a lightweight base image
FROM debian:latest

ENV DLDITOOL=/usr/bin/dlditool

# Install devkitARM directory
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip

# Remove used packages to make it lighter
# Add dlditool and the mpcf patch
RUN mkdir -p /usr/bin && \
    wget --no-check-certificate https://www.chishm.com/DLDI/downloads/mpcf.dldi -O /usr/bin/mpcf.dldi && \
    wget --no-check-certificate https://www.chishm.com/DLDI/downloads/dlditool-linux-x86_64.zip -O /tmp/dlditool.zip && \
    unzip -o /tmp/dlditool.zip -d /usr/bin && \
    chmod +x /usr/bin/dlditool && \
    rm /tmp/dlditool.zip

# Create directory for input volume
RUN mkdir -p /input

# Remove used packages to make it lighter
RUN apt-get purge -y \
    wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["dlditool"]
CMD []
