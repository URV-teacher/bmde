import os
import subprocess


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