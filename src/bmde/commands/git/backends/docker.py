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
from bmde.core.os_utils import host_uid_gid, ppp_line_discipline_unavailable

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
            # The image tells if the VPN works from the state of openfortivpn (vpn_healthcheck.sh). The images before it
            # (e.g. pinned with docker.image_tag) do not have it, and create /READY instead once the VPN works
            "--health-cmd=vpn_healthcheck.sh || [ -f /READY ]",
            "--health-interval=5s",
            # vpn_healthcheck.sh requests the test IP and DNS of the VPN
            "--health-timeout=10s",
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

    # Otherwise pppd fails inside the container ("Couldn't set tty to PPP discipline") after a misleading login
    if ppp_line_discipline_unavailable():
        raise RuntimeError(
            "The VPN needs the ppp_async kernel module, which containers cannot load on this host "
            "(dev.tty.ldisc_autoload = 0). Load it with 'sudo modprobe ppp_async', and add 'ppp_async' to "
            "/etc/modules-load.d/ppp.conf to load it on every boot"
        )

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
