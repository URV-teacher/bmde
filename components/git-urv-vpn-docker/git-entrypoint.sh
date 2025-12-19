#!/bin/bash

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

set -euo pipefail

# Use read secret function
SSH_HOST="$(read_secret ssh_host)"

echo "Adding server key to known hosts"
if [ "$EUID" -ne 0 ]; then
  whoami
  mkdir -p ~/.ssh
  ssh-keyscan -H $SSH_HOST >> ~/.ssh/known_hosts
else
  mkdir -p /root/.ssh
  ssh-keyscan -H $SSH_HOST >> /etc/ssh/ssh_known_hosts
  echo "end adding key"
fi


GIT_EMAIL="$(read_secret git_email)"
GIT_NAME="$(read_secret git_name)"
echo "Configuring email"
git config --global user.email "${GIT_EMAIL}"
echo "Configuring username"
git config --global user.email "${GIT_NAME}"

echo "Running git command with SSH password bypass."
echo "Working directory is: $(pwd)"
echo "Command is: $@"
echo "User is: $(whoami)"
/git.exp $@