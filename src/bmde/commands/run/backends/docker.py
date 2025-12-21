
from .backend import RunBackend
from ..spec import RunSpec
from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions

log = logging.get_logger(__name__)


class DockerRunner(RunBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        entry = str(spec.entrypoint)
        docker_img = "aleixmt/desmume:latest"
        mounts = ["-v", f"{spec.nds.parent}:/roms:ro",
                  "-v", f"desmume_docker_config:/home/desmume/.config/desmume"]
        envs = ["-e", f"ROM=/roms/{spec.nds.name}"]
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
        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *mounts, *envs, *ports, *entry, docker_img, *img_opt,
                    *debug_opt, *spec.arguments]

        return run_cmd(run_args, exec_opts)
