# bmde - Bare Metal Development Environment CLI
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.types import DockerOutputOptions

log = logging.get_logger(__name__)

DOCKER_REGISTRY = "aleixmt"
# Set from the settings by configure_docker_from_settings; None means the default of default_image_tag
_image_tag: str | None = None


def default_image_tag() -> str:
    """Tag of the images published with the installed version of bmde (e.g. 1.15.0)."""
    try:
        installed = version("bmde")
    except PackageNotFoundError:
        return "latest"
    # Only releases have images of their own: a development version (e.g. 1.14.1.dev3+g1234567) uses the latest ones
    return installed if re.fullmatch(r"\d+\.\d+\.\d+", installed) else "latest"


def configure_docker_from_settings(settings: Settings) -> None:
    # Set once at startup, so docker_image() does not need the settings passed down through every backend
    global _image_tag  # noqa: PLW0603
    _image_tag = settings.docker.image_tag


def docker_image(name: str) -> str:
    """Reference of the image NAME of the BMDE (e.g. desmume) with the configured tag."""
    return f"{DOCKER_REGISTRY}/{name}:{_image_tag or default_image_tag()}"


def can_run_docker() -> bool:
    """Return True if the current user can run Docker containers, False otherwise."""
    # Try using the Docker CLI directly
    try:
        # Run 'docker info' quietly; suppress output
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except FileNotFoundError:
        # Docker CLI not installed
        return False
    except subprocess.CalledProcessError:
        # Docker CLI exists but user cannot access the daemon
        return False
    except Exception:
        # Catch any unexpected errors
        return False
    else:
        log.debug("Docker container runtime running")
        return True


def docker_container_exists(container_name: str) -> bool:
    try:
        subprocess.check_output(["docker", "inspect", container_name], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def docker_inspect_health(container_name: str) -> str | None:
    """Return health status string: "healthy", "unhealthy", "starting", or None if not found/no health."""
    try:
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_name],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError:
        # Container absent or no Health configured
        return None
    else:
        return out if out else None


def docker_network_exists(network_name: str) -> bool:
    """Return True if a Docker network with the given name exists, False otherwise."""
    try:
        subprocess.check_output(["docker", "network", "inspect", network_name], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def docker_create_network(network_name: str) -> None:
    """Create a Docker network with the given name if it does not already exist."""
    log.info(f"Creating Docker network '{network_name}'...")
    subprocess.run(["docker", "network", "create", network_name], check=True)


def docker_remove_network(network_name: str) -> None:
    """Remove a Docker network with the given name if it exists."""
    if docker_network_exists(network_name):
        log.info(f"Removing Docker network '{network_name}'...")
        subprocess.run(["docker", "network", "rm", network_name], check=True)


def ensure_network_is_present(network_name: str) -> None:
    if not docker_network_exists(network_name):
        docker_create_network(network_name)


# Where docker compose mounts its secrets, and where the scripts of the components read them first (read_secret)
CONTAINER_SECRETS_DIR = "/run/secrets"


@contextmanager
def docker_secrets(secrets: dict[str, str | None], keep: bool = False) -> Iterator[list[str]]:
    """Mounts each value in CONTAINER_SECRETS_DIR/<name> of a container.

    This replaces passing it in its environment (-e), which any user of the machine can see with ps or docker inspect.

    Args:
        secrets: Value of each secret, by name (e.g. vpn_password). The ones that are None are not mounted.
        keep: Do not remove the files on exit, for a container started in the background, that may not have mounted
            them yet. They are in the runtime directory of the user, removed when the session ends.

    Yields:
        The docker run arguments that mount them. The files are only readable by the user, in a temporary directory
        removed on exit (the containers already started keep their mounted copy).

    """
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    directory = Path(
        tempfile.mkdtemp(
            prefix="bmde-secrets-", dir=runtime_dir if runtime_dir and Path(runtime_dir).is_dir() else None
        )
    )
    try:
        mounts: list[str] = []
        for name, value in secrets.items():
            if value is None:
                continue
            path = directory / name
            path.touch(mode=0o600)
            path.write_text(value)
            mounts += ["-v", f"{path}:{CONTAINER_SECRETS_DIR}/{name}:ro"]
        yield mounts
    finally:
        if not keep:
            shutil.rmtree(directory, ignore_errors=True)


def docker_project_dir(project: Path) -> str:
    """Path where a project is mounted in the BMDE containers.

    The debug information of ELFs built by the build command refers to the sources under it, so the debugger needs the
    project mounted in the same path to find them.
    """
    return f"/input/{project.name}"


# A path inside the container, not a temporary file of the host
CONTAINER_XAUTHORITY = "/tmp/.docker.xauth"  # noqa: S108


def _host_xauthority() -> Path | None:
    xauth = os.environ.get("XAUTHORITY")
    candidate = Path(xauth) if xauth else Path.home() / ".Xauthority"
    return candidate if candidate.is_file() else None


def host_x11_docker_args() -> tuple[list[str], list[str]]:
    """Return (mounts, envs) docker arguments that let a container draw on the host X server.

    This includes Xwayland, which requires an MIT-MAGIC-COOKIE.
    """
    display = os.environ.get("DISPLAY", ":0")
    # The fixed location of the X server sockets, not a temporary file
    mounts = ["-v", "/tmp/.X11-unix:/tmp/.X11-unix"]  # noqa: S108
    envs = ["-e", f"DISPLAY={display}"]

    source = _host_xauthority()
    if source is None:
        log.warning(
            "No Xauthority file found; the container may be refused by the X "
            "server. Set XAUTHORITY or run 'xhost +SI:localuser:$USER'."
        )
        return mounts, envs

    mounts += ["-v", f"{source}:{CONTAINER_XAUTHORITY}:ro"]
    envs += ["-e", f"XAUTHORITY={CONTAINER_XAUTHORITY}"]
    return mounts, envs


CONTAINER_PULSE_SOCKET = "/run/pulse/native"
CONTAINER_PULSE_COOKIE = "/run/pulse/cookie"


def _host_pulse_socket() -> Path | None:
    server = os.environ.get("PULSE_SERVER")
    if server:
        if not server.startswith("unix:"):
            return None
        candidate = Path(server.removeprefix("unix:"))
    else:
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        candidate = Path(runtime_dir) / "pulse" / "native"
    return candidate if candidate.is_socket() else None


def _host_pulse_cookie() -> Path | None:
    cookie = os.environ.get("PULSE_COOKIE")
    candidate = Path(cookie) if cookie else Path.home() / ".config" / "pulse" / "cookie"
    return candidate if candidate.is_file() else None


def host_pulse_docker_args() -> tuple[list[str], list[str]]:
    """Return (mounts, envs) docker arguments that let a container play sound through the host.

    The host needs a PulseAudio-compatible server (PulseAudio or PipeWire).
    """
    socket = _host_pulse_socket()
    if socket is None:
        log.warning(
            "No host PulseAudio socket found; sound will not be heard. Is PulseAudio or pipewire-pulse running?"
        )
        return [], []

    mounts = ["-v", f"{socket}:{CONTAINER_PULSE_SOCKET}"]
    envs = ["-e", f"PULSE_SERVER=unix:{CONTAINER_PULSE_SOCKET}"]

    cookie = _host_pulse_cookie()
    if cookie is not None:
        mounts += ["-v", f"{cookie}:{CONTAINER_PULSE_COOKIE}:ro"]
        envs += ["-e", f"PULSE_COOKIE={CONTAINER_PULSE_COOKIE}"]
    return mounts, envs


CONTAINER_VNC_PORT = 5900


def docker_screen_args(
    output: DockerOutputOptions | None, vnc_host_port: int = CONTAINER_VNC_PORT
) -> tuple[list[str], list[str], list[str]]:
    """Return (mounts, envs, ports) docker arguments to show the graphical output of a container of the BMDE images.

    The output (MODE of their entrypoint) is shown as windows of the host X server, through a VNC server published at
    vnc_host_port, or not at all.
    """
    if output == DockerOutputOptions.HOST:
        mounts, envs = host_x11_docker_args()
        return mounts, [*envs, "-e", "MODE=host"], []
    if output == DockerOutputOptions.VNC:
        return [], ["-e", "MODE=vnc"], ["-p", f"{vnc_host_port}:{CONTAINER_VNC_PORT}"]
    return [], ["-e", "MODE=none"], []
