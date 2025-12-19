#!/bin/bash

set -euo pipefail

# Usage: read_secret <VAR_NAME>
# Reads secret value from:
#   1) /run/secrets/<lowercase var name>
#   2) $<VAR_NAME>_FILE (path to file containing secret)
#   3) $<VAR_NAME> (value itself)
# Returns the value on stdout.

read_secret() {
  local name="$1"

  local secret_path="/run/secrets/${name}"
  local file_var="$(echo ${name} | tr '[:lower:]' '[:upper:]')_FILE"
  local env_var="$(echo ${name} | tr '[:lower:]' '[:upper:]')"
  local val=""

  if [ -f "$secret_path" ]; then
    val="$(<"$secret_path")"
  elif [ -n "${!file_var:-}" ] && [ -f "${!file_var}" ]; then
    val="$(<"${!file_var}")"
  elif [ -n "${!env_var:-}" ]; then
    val="${!env_var}"
  fi

  printf '%s' "$val"
}

# Path to secrets
VPN_USERNAME="$(read_secret vpn_username)"
VPN_PASSWORD="$(read_secret vpn_password)"
VPN_HOST="$(read_secret vpn_host)"
VPN_PORT="$(read_secret vpn_port)"
VPN_REALM="$(read_secret vpn_realm)"
VPN_CERT="$(read_secret vpn_cert)"

VPN_TEST_DNS="$(read_secret vpn_test_dns)"
VPN_TEST_IP="$(read_secret vpn_test_ip)"

# Configure openfortiVPN
tee /etc/openfortivpn/config > /dev/null <<EOF
host = $VPN_HOST
port = $VPN_PORT
username = $VPN_USERNAME
password = $VPN_PASSWORD
realm = $VPN_REALM
trusted-cert = $VPN_CERT
set-routes = 1
set-dns = 1
EOF

echo "🔐 Connecting to VPN"
openfortivpn -v 2>&1 | tee -a /var/log/vpn.log &
VPN_PID=$!

echo "Waiting for the VPN to establish..."
TRIES=0
while ! grep -q "Remote gateway has allocated a VPN" /var/log/vpn.log; do
    sleep 1
    TRIES=$((TRIES+1))
    if [ $TRIES -gt 20 ]; then
        echo "VPN did not connect after 20 seconds. Aborting."
        cat /etc/openfortivpn/config

        cat /var/log/vpn.log
        exit 1
    fi
done

echo "VPN active. Testing"
echo "IP solvable? (wait, this usually takes approximately 2 minutes and 10 seconds)"
if wget $VPN_TEST_IP -O /var/log/ip.html 2>&1 | tee -a /var/log/ip.log; then
  echo "Yes"
else
  echo "No. Aborting"
  exit 1
fi

echo "DNS solvable?"
if wget $VPN_TEST_DNS -O /var/log/dns.html 2>&1 | tee -a /var/log/dns.log ; then
  echo "Yes"
else
  echo "No. Aborting"
  exit 2
fi
echo "VPN validated. Continuing"

touch /READY  # Healthcheck
echo "Waiting for the termination of the VPN process"
wait $VPN_PID
