import os
import subprocess
import shutil


def is_command_available(cmd: str) -> bool:
    """
    Return True if the given command is available in the system PATH.

    Args:
        cmd (str): The command to check, e.g. 'docker', 'make', 'git'.

    Returns:
        bool: True if the command is found, False otherwise.
    """
    return shutil.which(cmd) is not None


def host_uid_gid() -> tuple[int, int] | None:
    """Return (uid, gid) if available on this OS; otherwise None."""
    # Prefer Python stdlib where available (POSIX)
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        try:
            return os.getuid(), os.getgid()
        except Exception:
            pass
    # Fallback to `id` command (e.g., inside POSIX shells without getuid support).
    try:
        uid = subprocess.check_output(["id", "-u"], text=True).strip()
        gid = subprocess.check_output(["id", "-g"], text=True).strip()
        return int(uid), int(gid)
    except Exception:
        return None