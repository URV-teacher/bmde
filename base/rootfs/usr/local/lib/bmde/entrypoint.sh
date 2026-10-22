# Library shared by the entrypoints of the BMDE images. Source it from a bash entrypoint:
#   source /usr/local/lib/bmde/entrypoint.sh
#
# It provides logging and validation helpers, and the graphical output of the container, selected with MODE:
#   host: windows in the X server of the host (needs DISPLAY and, for Xwayland, XAUTHORITY)
#   vnc:  a virtual X server (Xvfb) shared through a VNC server (x11vnc) on VNC_PORT
#   none: no graphical output
# shellcheck shell=bash

# -------------------- Defaults --------------------
: "${MODE:=none}"                     # 'host' | 'vnc' | 'none'
: "${VNC_XVFB_DISPLAY:=:99}"          # display of Xvfb, used only in vnc mode
: "${VNC_GEOMETRY:=1024x768x24}"      # WIDTHxHEIGHTxDEPTH (24 or 32)
: "${VNC_PORT:=5900}"
: "${VNC_LISTEN:=0.0.0.0}"
: "${VNC_PASSWORD:=}"                 # optional; empty => no auth

# -------------------- Helpers --------------------
log() { printf '[entrypoint] %s\n' "$*"; }
die() { printf '[entrypoint][ERROR] %s\n' "$*" >&2; exit 2; }

require_bin() { command -v "$1" >/dev/null 2>&1 || die "Missing required binary: $1"; }

validate_int() {
  [[ "$1" =~ ^[0-9]+$ ]] || die "Expected integer, got '$1' for $2"
}

# Waits up to $3 seconds for $1:$2 to accept TCP connections. Returns 1 on timeout.
wait_for_port() {
  local host="$1" port="$2" seconds="$3" i
  for (( i = 0; i < seconds; i++ )); do
    if timeout 1 bash -c "</dev/tcp/${host}/${port}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  return 1
}

# -------------------- Graphical output --------------------
stop_display() {
  if [[ -n "${X11VNC_PID:-}" ]]; then kill "${X11VNC_PID}" 2>/dev/null || true; fi
  if [[ -n "${XVFB_PID:-}" ]]; then kill "${XVFB_PID}" 2>/dev/null || true; fi
}

start_vnc_stack() {
  require_bin Xvfb
  require_bin x11vnc

  log "Starting Xvfb on ${VNC_XVFB_DISPLAY} with geometry ${VNC_GEOMETRY}"
  Xvfb "${VNC_XVFB_DISPLAY}" -screen 0 "${VNC_GEOMETRY}" -nolisten tcp &
  XVFB_PID=$!
  export DISPLAY="${VNC_XVFB_DISPLAY}"

  local vnc_auth=()
  if [[ -n "${VNC_PASSWORD}" ]]; then
    mkdir -p "${HOME}/.vnc"
    x11vnc -storepasswd "${VNC_PASSWORD}" "${HOME}/.vnc/passwd" >/dev/null
    vnc_auth=(-rfbauth "${HOME}/.vnc/passwd")
  else
    log "WARNING: x11vnc running without password (set VNC_PASSWORD to secure)"
  fi

  mkdir -p "${HOME}/logs"
  log "Starting x11vnc on ${VNC_LISTEN}:${VNC_PORT} (DISPLAY=${DISPLAY})"
  x11vnc \
    -display "${DISPLAY}" \
    -listen "${VNC_LISTEN}" \
    -rfbport "${VNC_PORT}" \
    -forever -shared \
    -noshm -noxdamage \
    -o "${HOME}/logs/x11vnc.log" \
    "${vnc_auth[@]}" &
  X11VNC_PID=$!
}

# Prepares the graphical output selected with MODE. The X / VNC servers it starts are stopped when the entrypoint
# exits, so the program must not be exec'd.
setup_display() {
  case "${MODE}" in
    vnc)
      validate_int "${VNC_PORT}" "VNC_PORT"
      trap stop_display EXIT
      start_vnc_stack
      ;;
    host)
      export DISPLAY="${DISPLAY:-:0}"
      log "Using host X DISPLAY=${DISPLAY} (no VNC in this mode)"
      if [[ -z "${XAUTHORITY:-}" || ! -r "${XAUTHORITY}" ]]; then
        log "WARNING: no readable XAUTHORITY; the host X server (e.g. Xwayland) may refuse the connection."
        log "WARNING: mount the host cookie and set XAUTHORITY, or run 'xhost +SI:localuser:\$USER' on the host."
      fi
      ;;
    none)
      log "MODE=none: no X/VNC will be started."
      ;;
    *)
      die "Invalid MODE='${MODE}'. Use MODE=host, MODE=vnc or MODE=none."
      ;;
  esac
}
