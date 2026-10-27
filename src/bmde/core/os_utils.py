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
import shutil
import subprocess
from pathlib import Path


def is_command_available(cmd: str) -> bool:
    """Return True if the given command is available in the system PATH.

    Args:
        cmd (str): The command to check, e.g. 'docker', 'make', 'git'.

    Returns:
        bool: True if the command is found, False otherwise.

    """
    return shutil.which(cmd) is not None


def host_uid_gid() -> tuple[int, int]:
    """Return (uid, gid) if available on this OS; otherwise None."""
    # Prefer Python stdlib where available (POSIX)
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        try:
            return os.getuid(), os.getgid()
        except Exception:
            return 1000, 1000
    # Fallback to `id` command (e.g., inside POSIX shells without getuid support).
    try:
        uid = subprocess.check_output(["id", "-u"], text=True).strip()
        gid = subprocess.check_output(["id", "-g"], text=True).strip()
        return int(uid), int(gid)
    except Exception:
        return 1000, 1000


def ppp_line_discipline_unavailable(root: Path = Path("/")) -> bool:
    """Return True if a container can't use the PPP line discipline that the VPN (pppd) needs.

    That happens when the ppp_async kernel module is neither loaded nor built in and the kernel doesn't let
    unprivileged processes autoload line disciplines (dev.tty.ldisc_autoload = 0), as in recent Ubuntu kernels.
    Returns False when it can't tell, e.g. outside Linux.
    """
    autoload = root / "proc" / "sys" / "dev" / "tty" / "ldisc_autoload"
    if not autoload.is_file():
        return False
    return autoload.read_text().strip() == "0" and not (root / "sys" / "module" / "ppp_async").is_dir()
