import logging

from .backend import RunBackend
from ..spec import RunSpec
from ...core.exec import run_cmd, ExecOptions

log = logging.getLogger(__name__)


class DockerRunner(RunBackend):
    def is_available(self) -> bool:
        return True  # optionally check docker info

    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        entry = str(spec.entrypoint) or "desmume"
        if spec.shell:
            entry = "bash"
        docker_img = "aleixmt/desmume:latest"
        mounts = ["-v", f"{spec.nds.parent}:/roms:ro"]
        envs = []
        ports = []
        img_opt = []
        if spec.image:
            mounts += ["-v", f"{spec.image}:/fs/fat.img:rw"]
            img_opt += ["--cflash-image", "/fs/fat.img"]

        if spec.docker_screen == "host":
            mounts += ["-v", "/tmp/.X11-unix:/tmp/.X11-unix"]
            envs += ["-e", "MODE=host",
                     "-e", "DISPLAY=:0",
                     "-e", "XVFB_DISPLAY=:99",
                     "-e", "GEOMETRY=1024x768x24",
                     "-e", "VNC_PORT=5900"]
        if spec.docker_screen == "vnc":
            ports += ["-p", "3000:3000",
                      "-p", "3001:3001"]
            envs += ["-e", "MODE=vnc",
                     "-e", "DISPLAY=:0"]
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint)]

        debug_opt = ["--gdb-stub", "--arm9gdb-port", str(spec.port)] if spec.debug else []
        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *mounts, *envs, *ports, *entry, docker_img, f"/roms/{spec.nds.name}", *img_opt,
                    *debug_opt, *spec.arguments]

        return run_cmd(run_args, exec_opts)
