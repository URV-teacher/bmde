import subprocess
from typing import Optional

def docker_container_exists(container_name: str) -> bool:
    try:
        subprocess.check_output(
            ["docker", "inspect", container_name],
            stderr=subprocess.DEVNULL
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
            text=True, stderr=subprocess.STDOUT
        ).strip()
        return out if out else None
    except subprocess.CalledProcessError:
        # Container absent or no Health configured
        return None