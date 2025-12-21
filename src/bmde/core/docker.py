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
