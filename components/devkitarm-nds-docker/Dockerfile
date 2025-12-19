# Use a lightweight base image
FROM debian:latest

# Set environment variables for devkitPro
# Added DESMUME for compatibility with Makefile that need DESMUME env variable defined, even if it is not needed for compilation
ENV DEVKITPRO=/bmde/devkitPro \
    DEVKITARM=/bmde/devkitPro/devkitARM \
    PATH=/bmde/devkitPro/devkitARM/bin:/bmde/dlditool/bin:$PATH \
    DESMUME="/"

# Install only required tools in one layer and clean up to reduce image size
# Install required dependencies
# Create directories for devkitPro
# Install devkitARM directory
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    wget \
    bzip2 \
    unzip \
 && mkdir -p $DEVKITPRO $DEVKITARM \
 && wget --no-check-certificate "https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2" -O /tmp/devkitARM.tar.bz2 \
 && tar -xf /tmp/devkitARM.tar.bz2 -C /bmde/devkitPro/ \
 && rm /tmp/devkitARM.tar.bz2

# Copy and extract libnds.tar.bz2 for the subject. TODO: Obtain libnds from a reproducible source
COPY ./data/libnds.tar.bz2 /bmde/devkitPro/
RUN tar -xvjf $DEVKITPRO/libnds.tar.bz2 -C $DEVKITPRO/ \
    && rm $DEVKITPRO/libnds.tar.bz2

# Remove used packages to make it lighter
RUN apt-get purge -y \
    wget \
    bzip2 \
    unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Create directory for input volume
RUN mkdir -p /input

ENTRYPOINT ["make"]
CMD []