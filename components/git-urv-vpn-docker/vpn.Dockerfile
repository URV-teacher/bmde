FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    openfortivpn \
    time \
    wget && \
    rm -rf /var/lib/apt/lists/*

COPY ./src/connect_vpn.sh /connect_vpn.sh
RUN chmod +x /connect_vpn.sh

COPY vpn-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]