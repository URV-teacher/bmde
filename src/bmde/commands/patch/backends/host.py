import hashlib
import shutil
import subprocess
import urllib.request
from pathlib import Path

import platformdirs

from bmde.core import logging
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import is_command_available
from bmde.core.types import APP_NAME

from ..spec import PatchSpecOpts
from .backend import PatchBackend

log = logging.get_logger(__name__)

# DLDI driver of the M3 / G6 / SuperCard CompactFlash, the one of the emulator, as in the image of dlditool
# (dlditool-docker/scripts/download_assets.sh)
DLDI_DRIVER = "mpcf.dldi"
DLDI_DRIVER_URL = f"https://www.chishm.com/DLDI/downloads/{DLDI_DRIVER}"
DLDI_DRIVER_SHA256 = "9ad482e6520f631644a808ef53d5a35f55223ebe3d6d2754c94329ba04585a86"  # pragma: allowlist secret


def dldi_driver(dlditool: str, download: bool = True) -> str:
    """Driver to patch the ROMs with.

    Its name, if dlditool has it in its dldi/ directory (where it looks for the drivers given by name, and where the
    BMDE installs it), or else the copy in the cache of bmde, downloaded the first time. The cache is outside of the
    repositories, so the driver can never be committed by mistake.

    Args:
        dlditool: Path of the dlditool executable.
        download: Download the driver if it is not in the cache (not in a dry run).

    """
    if (Path(dlditool).resolve().parent / "dldi" / DLDI_DRIVER).is_file():
        return DLDI_DRIVER
    cached = platformdirs.user_cache_path(APP_NAME, appauthor=False) / "dldi" / DLDI_DRIVER
    if download and not cached.is_file():
        log.info(f"Downloading the DLDI driver {DLDI_DRIVER} into {cached}")
        with urllib.request.urlopen(DLDI_DRIVER_URL, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != DLDI_DRIVER_SHA256:
            raise RuntimeError(f"{DLDI_DRIVER_URL} does not have the expected SHA-256 {DLDI_DRIVER_SHA256}")
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
    return str(cached)


class HostRunner(PatchBackend):
    def is_available(self) -> bool:
        return is_command_available("dlditool")

    def run(self, spec: PatchSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            dlditool_path = shutil.which("dlditool")
            entry = "dlditool" if dlditool_path is None else dlditool_path
        # As the docker backend: the arguments replace the default ones, the driver and the ROM
        if exec_opts.arguments is not None:
            args = [entry, *exec_opts.arguments]
        else:
            args = [entry, dldi_driver(entry, download=not exec_opts.dry_run), str(spec.nds_rom)]
        return run_cmd(args, exec_opts)
