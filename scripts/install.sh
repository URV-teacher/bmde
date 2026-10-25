#!/usr/bin/env bash
# Installs the components of the BMDE in an Ubuntu / Debian host, with the install scripts of each component (the same
# ones that build their Docker images, see docs/getting-started/host_components_installation.md), or downloads their
# Docker images. These are the tools that the host backends of bmde use, and the ones that the Makefiles of the course
# use (make, make run, make debug), as in the Windows BMDE.
#
#   scripts/install.sh [OPTION...] [COMPONENT...]    (every component by default)
#
# For each component, downloads its assets (scripts/download_assets.sh) and runs its install scripts (src/), in the
# order that the full development environment uses (shell/Dockerfile), whatever the order of the arguments. The
# components are taken from the submodules in components/ (checked out if they are not), or cloned into
# BMDE_COMPONENTS_DIR when the script runs outside of a checkout of bmde. Run it as your user, not with sudo: the
# install scripts call sudo themselves, and the extension of VS Code is installed for the user that runs it.
#
# Environment:
#   BMDE_ROOT            directory where the programs are installed (/URV/bmde by default)
#   BMDE_TAG             tag of the Docker images (latest by default): the ones pulled with --docker, and the one of
#                        Insight, whose tarball is taken from its image when it has not been built (see below)
#   BMDE_COMPONENTS_DIR  checkouts of the components to use (components/ of bmde by default)
#   INSIGHT_TARBALL      tarball of Insight to install (see components/insight-docker/src/install_insight.sh)
set -Eeuo pipefail

REGISTRY=aleixmt
BMDE_TAG="${BMDE_TAG:-latest}"
GITHUB=https://github.com/URV-teacher

# Components, in the order they are installed (each one can need the ones before it: grit reuses devkitARM, the
# wrappers of Insight go into devkitPro and the extension needs VS Code)
COMPONENTS=(devkitarm desmume insight dlditool grit git vpn vscode)

# The "repository:script[:assets]" steps that install each component: download_assets.sh with the names of the assets
# it needs (not the ones of the tests), a step of this script (insight_tarball) or an install script of src/
declare -A STEPS=(
  [devkitarm]="devkitarm-nds-docker:download_assets:devkitARM_r46-x86_64-linux.tar.bz2,libnds.tar.bz2
               devkitarm-nds-docker:download_assets:nds-examples.tar.gz
               devkitarm-nds-docker:install_make devkitarm-nds-docker:install_devkitarm
               devkitarm-nds-docker:install_libnds devkitarm-nds-docker:install_examples"
  [desmume]="desmume-docker:download_assets:desmume_0.9.11.orig.tar.gz,desmume_0.9.11-3build2.diff.gz
             desmume-docker:install_desmume desmume-docker:install_wrapper"
  [insight]="insight-docker:insight_tarball insight-docker:install_insight insight-docker:install_gdb_multiarch
             insight-docker:install_wrapper"
  [dlditool]="dlditool-docker:download_assets:dlditool-linux-x86_64.zip,mpcf.dldi dlditool-docker:install_dlditool"
  [grit]="grit-docker:download_assets:devkitARM_r46-x86_64-linux.tar.bz2 grit-docker:install_grit"
  [git]="git-urv-vpn-docker:install_ssh git-urv-vpn-docker:install_git"
  [vpn]="git-urv-vpn-docker:install_vpn"
  [vscode]="vscode-arm-syntax-docker:download_assets:vscode.deb vscode-arm-syntax-docker:install_vscode
            arm-syntax-vscode-extension:download_assets:arm-syntax-vscode-extension.vsix
            arm-syntax-vscode-extension:install_extension"
)
# Docker image of each component, the one that the docker backend of bmde runs
declare -A IMAGE=(
  [devkitarm]=bmde-linux
  [desmume]=desmume
  [insight]=insight
  [dlditool]=dlditool
  [grit]=grit
  [git]=git-sshpass
  [vpn]=forticlient
  [vscode]=vscode
)
declare -A DESCRIPTION=(
  [devkitarm]="make, devkitARM r46, libnds and the NDS examples of devkitPro (bmde build, make)"
  [desmume]="DeSmuME 0.9.11, with its DeSmuME.exe wrappers (bmde run, make run)"
  [insight]="Insight 7.3.50, gdb-multiarch and the arm-eabi-insight wrappers (bmde debug, make debug)"
  [dlditool]="dlditool and the DLDI driver of the emulator (bmde patch)"
  [grit]="grit, to convert images into graphics data"
  [git]="git, the SSH client and the git helpers of the BMDE (bmde git)"
  [vpn]="openfortivpn, the client of the VPN of the URV, and connect_vpn.sh (bmde git)"
  [vscode]="Visual Studio Code with the ARM assembly syntax extension of the course"
)

# BASH_SOURCE is empty when the script is piped into bash: there is no checkout of bmde around it then
SCRIPT_PATH="${BASH_SOURCE[0]:-}"
BMDE_DIR=""
if [ -n "${SCRIPT_PATH}" ] && [ -f "${SCRIPT_PATH}" ]; then
  BMDE_DIR="$(cd "$(dirname "${SCRIPT_PATH}")/.." && pwd)"
fi
if [ -n "${BMDE_COMPONENTS_DIR:-}" ]; then
  COMPONENTS_DIR="${BMDE_COMPONENTS_DIR}"
elif [ -n "${BMDE_DIR}" ] && [ -f "${BMDE_DIR}/.gitmodules" ]; then
  COMPONENTS_DIR="${BMDE_DIR}/components"
else
  COMPONENTS_DIR="${XDG_CACHE_HOME:-${HOME}/.cache}/bmde/components"
fi

usage() {
  cat <<USAGE
Usage: $0 [OPTION...] [COMPONENT...]

Installs the components of the BMDE in this host (every component by default), or downloads their Docker images.

Options:
  --docker    download the Docker images of the components instead of installing them in the host
  --dry-run   print the steps without running them
  --list      list the components
  -h, --help  show this help

Components:
USAGE
  list
}

list() {
  local component
  for component in "${COMPONENTS[@]}"; do
    printf '  %-10s %s\n' "${component}" "${DESCRIPTION[${component}]}"
  done
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

DRY_RUN=0
# Prints the command $@, and runs it unless in a dry run
run() {
  echo "+ $*"
  if [ "${DRY_RUN}" -eq 0 ]; then
    "$@"
  fi
}

# Makes sure the checkout of the component repository $1 is in COMPONENTS_DIR
checkout() {
  local repository="$1" directory="${COMPONENTS_DIR}/$1"
  if [ -d "${directory}/src" ]; then
    return 0
  fi
  if [ "${COMPONENTS_DIR}" = "${BMDE_DIR}/components" ]; then
    run git -C "${BMDE_DIR}" submodule update --init "components/${repository}"
  else
    run git clone --depth 1 "${GITHUB}/${repository}" "${directory}"
  fi
}

# Loads the environment (PATH, DEVKITPRO...) that the install scripts write into /etc/profile.d, so each script finds
# the programs installed by the previous ones (e.g. install_extension.sh needs the code of install_vscode.sh)
load_environment() {
  local file
  for file in /etc/profile.d/bmde-*.sh; do
    if [ -r "${file}" ]; then
      # shellcheck source=/dev/null
      . "${file}"
    fi
  done
}

# Puts the tarball of Insight where install_insight.sh looks for it, if it is not there. Building it needs the CVS
# repository of sourceware.org and Docker (scripts/build_tarball.sh of insight-docker), so it is taken from the
# published image of Insight instead, which installs the same tarball
insight_tarball() {
  local directory="$1"
  local tarball="${INSIGHT_TARBALL:-${directory}/build/insight-7.3.50.20110803-cvs-linux-x86_64.tar.xz}"
  if [ -f "${tarball}" ] || [ -x "${BMDE_ROOT:-/URV/bmde}/insight/bin/arm-eabi-insight" ]; then
    return 0
  fi
  if ! command -v docker > /dev/null; then
    die "${tarball} not found, and Docker is needed to make it: install Docker, or build it with" \
      "${directory}/scripts/build_tarball.sh and set INSIGHT_TARBALL"
  fi
  local image="${REGISTRY}/insight:${BMDE_TAG}"
  echo "+ copy /URV/bmde/insight of ${image} into ${tarball}"
  if [ "${DRY_RUN}" -eq 0 ]; then
    local container
    docker pull "${image}"
    container="$(docker create "${image}")"
    mkdir -p "$(dirname "${tarball}")"
    # docker cp writes a tar of the directory, with insight/ at its root like the tarball of build_tarball.sh
    docker cp "${container}:/URV/bmde/insight" - | xz -T0 > "${tarball}"
    docker rm "${container}" > /dev/null
  fi
}

# Runs the step $1 (repository:script[:assets]) of a component
step() {
  local repository script assets directory
  IFS=: read -r repository script assets <<< "$1"
  directory="${COMPONENTS_DIR}/${repository}"
  checkout "${repository}"
  case "${script}" in
    download_assets)
      # grit is copied from devkitARM when it is installed, so its copy of devkitARM is not needed
      if [ "${repository}" = grit-docker ] && [ -x "${BMDE_ROOT:-/URV/bmde}/devkitPro/devkitARM/bin/grit" ]; then
        return 0
      fi
      # shellcheck disable=SC2086  # The names of the assets are separate arguments
      run "${directory}/scripts/download_assets.sh" ${assets//,/ }
      ;;
    insight_tarball)
      insight_tarball "${directory}"
      ;;
    install_extension)
      # VS Code refuses to run as root, and the extension would be installed for root instead of the user
      if [ "$(id -u)" -eq 0 ]; then
        echo "WARNING: the extension of VS Code is not installed as root:" \
          "run ${directory}/src/${script}.sh as your user" >&2
        return 0
      fi
      run bash "${directory}/src/${script}.sh"
      ;;
    *)
      run bash "${directory}/src/${script}.sh"
      ;;
  esac
  load_environment
}

# download_assets.sh downloads with wget or curl, and the install scripts extract the assets with xz
prepare() {
  local sudo=()
  if [ "$(id -u)" -ne 0 ]; then
    sudo=(sudo)
  fi
  if ! command -v git > /dev/null || { ! command -v wget > /dev/null && ! command -v curl > /dev/null; } \
    || ! command -v xz > /dev/null; then
    run "${sudo[@]}" apt-get update
    run "${sudo[@]}" apt-get install -y --no-install-recommends ca-certificates git wget xz-utils
  fi
}

main() {
  local docker=0 selected=() component
  while [ $# -gt 0 ]; do
    case "$1" in
      --docker) docker=1 ;;
      --dry-run) DRY_RUN=1 ;;
      --list) list; return 0 ;;
      -h|--help) usage; return 0 ;;
      -*) usage >&2; die "unknown option $1" ;;
      *)
        if [ -z "${DESCRIPTION[$1]+set}" ]; then
          die "unknown component $1 (components: ${COMPONENTS[*]})"
        fi
        selected+=("$1")
        ;;
    esac
    shift
  done
  if [ ${#selected[@]} -eq 0 ]; then
    selected=("${COMPONENTS[@]}")
  fi

  if [ "${docker}" -eq 1 ]; then
    command -v docker > /dev/null || die "Docker is not installed (see docs/getting-started/prerequisites.md)"
    for component in "${COMPONENTS[@]}"; do
      if [[ " ${selected[*]} " == *" ${component} "* ]]; then
        run docker pull "${REGISTRY}/${IMAGE[${component}]}:${BMDE_TAG}"
      fi
    done
    return 0
  fi

  prepare
  load_environment
  for component in "${COMPONENTS[@]}"; do
    if [[ " ${selected[*]} " == *" ${component} "* ]]; then
      echo "==> ${component}: ${DESCRIPTION[${component}]}"
      local s
      for s in ${STEPS[${component}]}; do
        step "${s}"
      done
    fi
  done
  if [ "${DRY_RUN}" -eq 1 ]; then
    return 0
  fi
  echo "Installed: ${selected[*]}. Open a new session, or load the environment in this one with:"
  echo "  for f in /etc/profile.d/bmde-*.sh; do . \"\$f\"; done"
}

main "$@"
