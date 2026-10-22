import os
import subprocess
import sys
import time
from pathlib import Path

from bmde.core import logging
from bmde.core.docker import (
    can_run_docker,
    docker_container_exists,
    docker_image,
    docker_inspect_health,
    docker_secrets,
)
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import host_uid_gid

from ..spec import GitSpecOpts
from .backend import GitBackend

log = logging.get_logger(__name__)


def vpn_secrets(spec: GitSpecOpts) -> dict[str, str | None]:
    """Credentials of the VPN, by the name connect_vpn.sh reads them with."""
    return {
        "vpn_username": spec.vpn_username,
        "vpn_password": spec.vpn_password,
        "vpn_host": spec.vpn_host,
        "vpn_port": str(spec.vpn_port) if spec.vpn_port is not None else None,
        "vpn_realm": spec.vpn_realm,
        "vpn_cert": spec.vpn_cert,
        "vpn_test_dns": spec.vpn_test_dns,
        "vpn_test_ip": spec.vpn_test_ip,
    }


def git_secrets(spec: GitSpecOpts) -> dict[str, str | None]:
    """Credentials of the git server, by the name git-entrypoint.sh and git.exp read them with."""
    return {
        "ssh_username": spec.ssh_username,
        "ssh_password": spec.ssh_password,
        "ssh_host": spec.ssh_host,
        "git_name": spec.git_name,
        "git_email": spec.git_email,
    }


def _run_vpn(spec: GitSpecOpts, exec_opts: ExecOptions, container_name: str) -> int | subprocess.Popen[bytes] | None:
    docker_img = docker_image("forticlient")

    run_args = [
        "docker",
        "run",
        "--pull=always",
        "-d",
        "--rm",
    ]

    if exec_opts.interactive:
        run_args += ["-it"]

    # Started detached (-d): when docker run returns, the container exists with the secrets mounted, so their files can
    # be removed
    with docker_secrets(vpn_secrets(spec)) as secrets:
        run_args += [
            "--name",
            container_name,
            "--cap-add",
            "NET_ADMIN",
            "--device",
            "/dev/ppp",
            "--health-cmd=[ -f /READY ] || exit 1",
            "--health-interval=5s",
            "--health-timeout=2s",
            "--health-retries=12",
            "--health-start-period=120s",
            *secrets,
            docker_img,
        ]
        return run_cmd(run_args, exec_opts)


def _ensure_vpn_healthy(spec: GitSpecOpts, exec_opts: ExecOptions, timeout_s: int = 20000) -> None:
    """Ensure the 'forti-vpn' service is running and HEALTHY.

    If absent or not healthy, start with `docker compose up -d forti-vpn` and wait.
    """
    container_name = "forti-vpn"
    if exec_opts.dry_run:
        # Only show the command that starts the VPN: there is no container to inspect, remove or wait for
        _run_vpn(spec, exec_opts, container_name)
        return
    status = docker_inspect_health(container_name)

    log.debug("VPN container status: " + str(status))
    if status == "healthy":
        log.debug("VPN is healthy")
        return
    elif docker_container_exists(container_name):
        log.debug(f"Container '{container_name}' exists but is not healthy ({status}); removing it...")
        try:
            subprocess.run(["docker", "rm", "-f", container_name], check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to remove unhealthy container '{container_name}': {e}") from e

    log.info("Running VPN")
    _run_vpn(spec, exec_opts, container_name)

    # Poll until healthy or timeout
    previous_state = None  # Will be used to determine if the container started and stopped, which means failure
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = docker_inspect_health(container_name)
        if status == "healthy":
            log.info("VPN is healthy.")
            return
        elif status == "starting":
            log.info(f"VPN health: {status}. Please, wait. The VPN connection usually takes 120 seconds.")
            previous_state = status
        else:
            log.info(f"VPN health: {status}. Please, wait. The VPN connection usually takes 120 seconds.")
            if previous_state == "starting":
                log.error(
                    f"'{container_name}' was starting and now it is not healthy, meaning the container could not "
                    f"start. Your configuration may be wrong. Aborting..."
                )
                sys.exit(1)
            previous_state = status
        time.sleep(10)

    raise TimeoutError(f"'{container_name}' did not become healthy within {timeout_s} seconds")


# --------------------------- Git Runner ----------------------------


class DockerRunner(GitBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: GitSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        """Runs the git container through the VPN.

        1) Ensure 'forti-vpn' compose service is up & healthy (start in background if needed).
        2) Run the git container sharing the network namespace with 'forti-vpn' with the command.
        """
        docker_img = docker_image("git-sshpass")

        # 2) Ensure VPN is healthy (starts it if needed), unless it is disabled (e.g. inside the network of the URV)
        if spec.vpn_enabled:
            _ensure_vpn_healthy(spec, exec_opts, timeout_s=getattr(spec, "vpn_timeout_s", 300))

        # 3) Build docker run args for the git container
        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        # primary project mount (writable)
        host_path = str(Path(spec.d).resolve())
        dirname = os.path.basename(host_path)

        # TODO mount logs
        mounts = ["-v", f"{spec.d}:/repos/{dirname}:rw"]
        workdir_opt = ["-w", f"/repos/{dirname}"]

        # share network namespace with the running VPN container
        net = ["--network", "container:forti-vpn"] if spec.vpn_enabled else []
        uid, gid = host_uid_gid()
        user_opt = ["--user", f"{uid}:{gid}"]

        args: list[str] = []
        if exec_opts.arguments:
            args = exec_opts.arguments

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
        ]

        if exec_opts.interactive:
            run_args += ["-it"]

        # A container started in the background may not have mounted the secrets when docker run returns
        with docker_secrets(git_secrets(spec), keep=bool(exec_opts.background)) as secrets:
            run_args += [
                *user_opt,
                *net,
                *mounts,
                *secrets,
                *entry,
                *workdir_opt,
                docker_img,
                *args,
            ]

            log.debug("Run args for Docker" + str(run_args))
            return run_cmd(run_args, exec_opts)
