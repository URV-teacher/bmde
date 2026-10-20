#!/usr/bin/env bash
set -Eeuo pipefail

# Logging, validation and graphical output (MODE, VNC_*) shared by the BMDE images (from the base image)
# shellcheck source=/dev/null
source /usr/local/lib/bmde/entrypoint.sh

setup_display

# Runs the given command, or an interactive shell, with the environment of the BMDE programs. Not exec'd, so the X /
# VNC servers are stopped on exit
if (( $# == 0 )); then
  set -- bash
fi
"$@"
