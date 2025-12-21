import os
import time
import subprocess
from pathlib import Path
from typing import Optional

from .backend import GitBackend
from ..spec import GitSpec
from bmde.core import logging
from bmde.core.docker import docker_inspect_health, docker_container_exists, can_run_docker
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import host_uid_gid

log = logging.get_logger(__name__)



def _run_vpn(spec: GitSpec, exec_opts: ExecOptions, container_name: str) -> Optional[int]:
    docker_img = "aleixmt/forticlient:latest"

    envs: list[str] = [
        "-e", f"SSH_USERNAME={spec.ssh_username}",
        "-e", f"SSH_PASSWORD={spec.ssh_password}",
        "-e", f"SSH_HOST={spec.ssh_host}",

        "-e", f"GIT_NAME={spec.git_name}",
        "-e", f"GIT_EMAIL={spec.git_email}",

        "-e", f"VPN_USERNAME={spec.vpn_username}",
        "-e", f"VPN_PASSWORD={spec.vpn_password}",
        "-e", f"VPN_HOST={spec.vpn_host}",
        "-e", f"VPN_PORT={spec.vpn_port}",
        "-e", f"VPN_REALM={spec.vpn_realm}",
        "-e", f"VPN_CERT={spec.vpn_cert}",
        "-e", f"VPN_TEST_DNS={spec.vpn_test_dns}",
        "-e", f"VPN_TEST_IP={spec.vpn_test_ip}",
    ]

    run_args = [
        "docker", "run",
        "--pull=always",
        "-d",
        "--rm",
        "-it",
        "--name", container_name,
        "--cap-add", "NET_ADMIN",
        "--device", "/dev/ppp",
        "--health-cmd=[ -f /READY ] || exit 1",
        "--health-interval=5s",
        "--health-timeout=2s",
        "--health-retries=12",
        "--health-start-period=120s",
        *envs,
        docker_img,
    ]

    run_cmd(run_args, exec_opts)



def _ensure_vpn_healthy(spec: GitSpec, exec_opts: ExecOptions, timeout_s: int = 20000) -> None:
    """
    Ensure the 'forti-vpn' service is running and HEALTHY.
    If absent or not healthy, start with `docker compose up -d forti-vpn` and wait.
    """
    container_name = "forti-vpn"
    status = docker_inspect_health(container_name)

    log.debug("VPN container status: " + str(status))
    if status == "healthy":
        log.debug(f"VPN is healthy")
        return
    elif docker_container_exists(container_name):
        log.debug(f"Container '{container_name}' exists but is not healthy ({status}); removing it...")
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to remove unhealthy container '{container_name}': {e}")

    log.info("Running VPN")
    _run_vpn(spec, exec_opts, container_name)

    # Poll until healthy or timeout
    previous_state = None  # Will be used to determine if the container started and stopped, which means failure
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = docker_inspect_health(container_name)
        if status == "healthy":
            log.info(f"VPN is healthy.")
            return
        elif status == "starting":
            log.info(f"VPN health: {status}. Please, wait. The VPN connection usually takes 120 seconds.")
            previous_state = status
        else:
            log.info(f"VPN health: {status}. Please, wait. The VPN connection usually takes 120 seconds.")
            if previous_state == "starting":
                log.error(f"'{container_name}' was starting and now it is not healthy, meaning the container could not "
                      f"start. Your configuration may be wrong. Aborting...")
                exit(1)
            previous_state = status
        time.sleep(10)

    raise TimeoutError(f"'{container_name}' did not become healthy within {timeout_s} seconds")


# --------------------------- Git Runner ----------------------------

class DockerRunner(GitBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: GitSpec, exec_opts: ExecOptions) -> int:
        """
        1) Ensure 'forti-vpn' compose service is up & healthy (start in background if needed).
        2) Run the git container sharing the network namespace with 'forti-vpn' with the command.
        """

        docker_img = "aleixmt/git-sshpass:latest"

        # 2) Ensure VPN is healthy (starts `docker compose up -d forti-vpn` if needed)
        _ensure_vpn_healthy(spec, exec_opts, timeout_s=getattr(spec, "vpn_timeout_s", 300))

        # 3) Build docker run args for the git container
        entry = []
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint)]
        if spec.shell:
            entry = ["--entrypoint", "bash"]


        # primary project mount (writable)
        host_path = str(Path(spec.d).resolve())
        dirname = os.path.basename(host_path)

        # TODO mount logs
        mounts = ["-v", f"{spec.d}:/repos/{dirname}:rw"]
        img_opt = []
        workdir_opt = ["-w", f"/repos/{dirname}"]

        # share network namespace with the running VPN container
        net = ["--network", "container:forti-vpn"]
        uid, gid = host_uid_gid()
        user_opt = ["--user", f"{uid}:{gid}"]

        envs: list[str] = [
            "-e", f"SSH_USERNAME={spec.ssh_username}",
            "-e", f"SSH_PASSWORD={spec.ssh_password}",

            "-e", f"SSH_HOST={spec.ssh_host}",
            "-e", f"GIT_NAME={spec.git_name}",
            "-e", f"GIT_EMAIL={spec.git_email}",
        ]

        run_args = [
            "docker", "run", "--pull=always", "--rm", "-it",
            *user_opt,
            *net,
            *mounts, *envs, *entry, *workdir_opt,
            docker_img, *img_opt,
            *getattr(spec, "arguments", []),
        ]

        log.debug("Run args for Docker" + str(run_args))
        return run_cmd(run_args, exec_opts)
