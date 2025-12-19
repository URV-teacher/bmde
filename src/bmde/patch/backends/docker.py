import logging
import os
import subprocess

from .backend import PatchBackend
from ..spec import PatchSpec
from ...core.exec import run_cmd, ExecOptions

log = logging.getLogger(__name__)

def _host_uid_gid() -> tuple[int, int] | None:
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

class DockerRunner(PatchBackend):
    def is_available(self) -> bool:
        return True  # optionally check docker info

    def run(self, spec: PatchSpec, exec_opts: ExecOptions) -> int:
        entry = []
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint)]

        if spec.shell:
            entry = ["--entrypoint", "bash"]
        docker_img = "aleixmt/dlditool:latest"

        dirname = os.path.basename(spec.d)
        mounts = ["-v", f"{spec.d}:/input/{dirname}:rw"]
        envs = []
        ports = []
        workdir_opt = ["-w", f"/input/{dirname}"]  # Workdir

        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *mounts, *envs, *ports, *entry, *workdir_opt, docker_img,
                    *spec.arguments]

        log.debug("Patch arguments for Docker backend" + str(run_args))
        return run_cmd(run_args, exec_opts)
