import subprocess
from typing import Optional

from bmde.core import logging

log = logging.get_logger(__name__)


def can_run_docker() -> bool:
    """
    Return True if the current user can run Docker containers, False otherwise.
    """
    # Try using the Docker CLI directly
    try:
        # Run 'docker info' quietly; suppress output
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        log.debug("Docker container running")
        return True
    except FileNotFoundError:
        # Docker CLI not installed
        return False
    except subprocess.CalledProcessError:
        # Docker CLI exists but user cannot access the daemon
        return False
    except Exception:
        # Catch any unexpected errors
        return False


def docker_container_exists(container_name: str) -> bool:
    try:
        subprocess.check_output(
            ["docker", "inspect", container_name], stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def docker_inspect_health(container_name: str) -> Optional[str]:
    """
    Return health status string: "healthy", "unhealthy", "starting", or None if not found/no health.
    """
    try:
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_name],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        return out if out else None
    except subprocess.CalledProcessError:
        # Container absent or no Health configured
        return None


def docker_network_exists(network_name: str) -> bool:
    """
    Return True if a Docker network with the given name exists, False otherwise.
    """
    try:
        subprocess.check_output(
            ["docker", "network", "inspect", network_name], stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def docker_create_network(network_name: str) -> None:
    """
    Create a Docker network with the given name if it does not already exist.
    """
    log.info(f"Creating Docker network '{network_name}'...")
    subprocess.run(["docker", "network", "create", network_name], check=True)


def docker_remove_network(network_name: str) -> None:
    """
    Remove a Docker network with the given name if it exists.
    """
    if docker_network_exists(network_name):
        log.info(f"Removing Docker network '{network_name}'...")
        subprocess.run(["docker", "network", "rm", network_name], check=True)


def ensure_network_is_present(network_name: str) -> None:
    if not docker_network_exists(network_name):
        docker_create_network(network_name)
