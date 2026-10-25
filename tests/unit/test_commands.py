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

"""The commands, run through the CLI as a user would: each test checks the command that bmde executes (docker run, make,
desmume...), with subprocess replaced by a recorder so nothing is executed.
"""

import logging
import os
import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner, Result

from bmde.cli import app
from bmde.config.schema import Settings
from bmde.core import docker
from bmde.core.docker import configure_docker_from_settings

runner = CliRunner()
ORIGINAL_POPEN = subprocess.Popen


class FakeProcess(ORIGINAL_POPEN):  # type: ignore[type-arg, misc]
    """A process started in the background, that runs until it is terminated (or killed, if wait_timeouts)."""

    wait_timeouts = False

    def __init__(self, args: list[str], **kwargs: Any) -> None:
        self.args = args
        self.returncode = None
        self._child_created = False
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        return 0 if self.terminated or self.killed else None

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        if self.wait_timeouts and timeout is not None:
            raise subprocess.TimeoutExpired(self.args, timeout)
        return 0


@dataclass
class Machine:
    """What the machine answers: the commands that bmde executes are recorded instead of being run."""

    # Commands executed (subprocess.call and Popen), with their keyword arguments
    executed: list[tuple[list[str], dict[str, Any]]] = field(default_factory=list)
    # Docker commands used to query and prepare Docker (docker info, network, inspect, rm...)
    docker_calls: list[list[str]] = field(default_factory=list)
    # Programs in the PATH
    installed: set[str] = field(default_factory=set)
    docker_running: bool = True
    networks: set[str] = field(default_factory=set)
    # Health of the VPN container returned by every docker inspect, in order (the last one is repeated)
    vpn_health: list[str] = field(default_factory=lambda: ["healthy"])
    vpn_container_exists: bool = True
    exit_code: int = 0
    # Processes started in the background
    processes: list[FakeProcess] = field(default_factory=list)

    # Content of the secrets mounted in each container (by name), read when the command is executed
    secrets: list[dict[str, str]] = field(default_factory=list)

    @property
    def commands(self) -> list[list[str]]:
        return [cmd for cmd, _ in self.executed]

    def record(self, cmd: list[str], kwargs: dict[str, Any]) -> None:
        self.executed.append((cmd, kwargs))
        mounted = {}
        for volume in option(cmd, "-v"):
            source, _, target = volume.partition(":")
            if target.startswith("/run/secrets/"):
                mounted[target.removeprefix("/run/secrets/").removesuffix(":ro")] = Path(source).read_text()
        self.secrets.append(mounted)

    def call(self, cmd: list[str], **kwargs: Any) -> int:
        self.record(cmd, kwargs)
        return self.exit_code

    def popen_class(self) -> type[FakeProcess]:
        """A replacement of subprocess.Popen (a class, because the code checks isinstance against it)."""
        machine = self

        class RecordedProcess(FakeProcess):
            def __init__(self, args: list[str], **kwargs: Any) -> None:
                super().__init__(args)
                machine.record(args, kwargs)
                machine.processes.append(self)

        return RecordedProcess

    def query(self, cmd: list[str], **kwargs: Any) -> Any:
        self.docker_calls.append(cmd)
        if cmd[:2] == ["docker", "info"] and not self.docker_running:
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[:3] == ["docker", "network", "inspect"] and cmd[3] not in self.networks:
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[:3] == ["docker", "network", "create"]:
            self.networks.add(cmd[3])
        if cmd[:3] == ["docker", "network", "rm"]:
            self.networks.discard(cmd[3])
        if cmd[:2] == ["docker", "inspect"] and len(cmd) == 3 and not self.vpn_container_exists:
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[:3] == ["docker", "inspect", "-f"]:
            health = self.vpn_health.pop(0) if len(self.vpn_health) > 1 else self.vpn_health[0]
            if health == "absent":
                raise subprocess.CalledProcessError(1, cmd)
            return health
        return ""


@pytest.fixture
def machine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Machine]:
    """The current directory is the project Hello (with its ROM and ELF), with no configuration of the machine."""
    project = tmp_path / "Hello"
    project.mkdir()
    (project / "Hello.nds").touch()
    (project / "Hello.elf").touch()
    monkeypatch.chdir(project)
    for name in list(os.environ):
        if name.startswith("BMDE_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    monkeypatch.delenv("XAUTHORITY", raising=False)
    monkeypatch.delenv("PULSE_SERVER", raising=False)
    monkeypatch.setattr(docker, "version", lambda _: "1.15.0")

    fake = Machine()
    monkeypatch.setattr(subprocess, "call", fake.call)
    monkeypatch.setattr(subprocess, "Popen", fake.popen_class())
    monkeypatch.setattr(subprocess, "run", fake.query)
    monkeypatch.setattr(subprocess, "check_output", fake.query)
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}" if name in fake.installed else None)
    yield fake

    # The CLI configures the logging and the image tag of the whole process
    logging.basicConfig(handlers=[logging.NullHandler()], force=True)
    configure_docker_from_settings(Settings())
    FakeProcess.wait_timeouts = False


def bmde(*args: str) -> Result:
    return runner.invoke(app, list(args))


def option(cmd: list[str], name: str) -> list[str]:
    """Values given to the option NAME (e.g. -v) in the command CMD."""
    return [cmd[i + 1] for i, arg in enumerate(cmd[:-1]) if arg == name]


# ---- build


def test_build_in_docker(machine: Machine) -> None:
    result = bmde("build", "clean")

    assert result.exit_code == 0, result.output
    (cmd,) = machine.commands
    project = Path.cwd()
    assert cmd[:4] == ["docker", "run", "--pull=always", "--rm"]
    assert "-it" in cmd
    assert option(cmd, "--user") == [f"{os.getuid()}:{os.getgid()}"]
    assert option(cmd, "-v") == [f"{project}:/input/Hello:rw"]
    assert option(cmd, "-w") == ["/input/Hello"]
    assert cmd[-2:] == ["aleixmt/devkitarm-nds:1.15.0", "clean"]


def test_build_with_another_entrypoint_and_no_tty(machine: Machine) -> None:
    result = bmde("build", "--entrypoint", "/bin/bash", "--no-interactive")

    assert result.exit_code == 0, result.output
    (cmd,) = machine.commands
    assert option(cmd, "--entrypoint") == ["/bin/bash"]
    assert "-it" not in cmd


def test_image_tag_setting_applies_to_the_cli(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BMDE_DOCKER__IMAGE_TAG", "sha-0123abc")

    assert bmde("build").exit_code == 0
    assert "aleixmt/devkitarm-nds:sha-0123abc" in machine.commands[0]


def test_build_in_the_host_runs_make_in_the_project(machine: Machine, tmp_path: Path) -> None:
    machine.installed = {"make", "arm-none-eabi-gcc"}
    other = tmp_path / "Other"
    other.mkdir()

    result = bmde("build", "-b", "host", "-d", str(other), "clean")

    assert result.exit_code == 0, result.output
    ((cmd, kwargs),) = machine.executed
    assert cmd == ["/usr/bin/make", "clean"]
    assert kwargs["cwd"] == str(other)


def test_build_fails_when_the_backend_is_not_available(machine: Machine) -> None:
    result = bmde("build", "-b", "host")

    assert isinstance(result.exception, RuntimeError)
    assert machine.commands == []


def test_dry_run_executes_nothing(machine: Machine) -> None:
    assert bmde("build", "--dry-run").exit_code == 0
    assert machine.commands == []


@pytest.mark.parametrize("command", ["build", "run", "patch", "git"])
def test_exit_code_of_the_tool_is_the_exit_code_of_bmde(machine: Machine, command: str) -> None:
    machine.exit_code = 2
    assert bmde(command, "-b", "docker").exit_code == 2


# ---- run


def test_run_in_docker(machine: Machine) -> None:
    result = bmde("run", "--no-sound", "-s", "vnc")

    assert result.exit_code == 0, result.output
    (cmd,) = machine.commands
    assert "--init" in cmd
    assert option(cmd, "-v") == [f"{Path.cwd()}:/roms:ro", "desmume_docker_config:/home/desmume/.config/desmume"]
    assert option(cmd, "-e") == ["MODE=vnc", "DESMUME_USE_SOUND=0"]
    assert option(cmd, "-p") == ["5900:5900"]
    assert cmd[-2:] == ["aleixmt/desmume:1.15.0", "/roms/Hello.nds"]


def test_run_in_docker_with_a_fat_image_custom_controls_and_debug(machine: Machine, tmp_path: Path) -> None:
    (tmp_path / "fat.img").touch()
    (tmp_path / "desmume.ini").touch()

    result = bmde(
        "run", "-i", str(tmp_path / "fat.img"), "--controls", str(tmp_path / "desmume.ini"), "--debug", "-p", "1000"
    )

    assert result.exit_code == 0, result.output
    (cmd,) = machine.commands
    assert f"{tmp_path / 'fat.img'}:/fs/fat.img:rw" in option(cmd, "-v")
    assert f"{tmp_path / 'desmume.ini'}:/config/desmume.ini:ro" in option(cmd, "-v")
    assert option(cmd, "--name") == ["desmume"]
    assert option(cmd, "--network") == ["bmde-debug"]
    assert "1000:1000" in option(cmd, "-p")
    assert cmd[-4:] == ["--cflash-image", "/fs/fat.img", "--arm9gdb=1000", "/roms/Hello.nds"]
    # The network of the debugger is created for the emulator and removed once it exits
    assert ["docker", "network", "create", "bmde-debug"] in machine.docker_calls
    assert ["docker", "network", "rm", "bmde-debug"] in machine.docker_calls


def test_a_debug_port_enables_debug_mode(machine: Machine) -> None:
    assert bmde("run", "-p", "2000").exit_code == 0
    assert "--arm9gdb=2000" in machine.commands[0]


def test_debug_mode_of_the_settings(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI does not override it when --debug is not given."""
    monkeypatch.setenv("BMDE_RUN__DEBUG", "true")

    assert bmde("run").exit_code == 0
    assert "--arm9gdb=1024" in machine.commands[0]


def test_run_in_docker_with_sound(machine: Machine, tmp_path: Path) -> None:
    import socket

    pulse = tmp_path / "runtime" / "pulse" / "native"
    pulse.parent.mkdir(parents=True)
    with socket.socket(socket.AF_UNIX) as sock:
        sock.bind(str(pulse))
        assert bmde("run").exit_code == 0

    (cmd,) = machine.commands
    assert f"{pulse}:/run/pulse/native" in option(cmd, "-v")
    assert "PULSE_SERVER=unix:/run/pulse/native" in option(cmd, "-e")


def test_dry_run_of_the_emulator_in_debug_mode_does_not_touch_docker(machine: Machine) -> None:
    machine.networks = {"bmde-debug"}

    assert bmde("run", "--debug", "--dry-run").exit_code == 0
    assert machine.commands == []
    assert not [call for call in machine.docker_calls if call[1] == "network"]


def test_run_in_the_host(machine: Machine, tmp_path: Path) -> None:
    machine.installed = {"desmume-cli"}
    (tmp_path / "fat.img").touch()
    (tmp_path / "desmume.ini").touch()

    result = bmde(
        "run",
        "-b",
        "host",
        "--no-sound",
        "--debug",
        "-i",
        str(tmp_path / "fat.img"),
        "--controls",
        str(tmp_path / "desmume.ini"),
        "--",
        "--3d-engine=0",
    )

    assert result.exit_code == 0, result.output
    rom = str(Path.cwd() / "Hello.nds")
    fat = str(tmp_path / "fat.img")
    assert machine.commands == [
        [
            "/usr/bin/desmume-cli",
            rom,
            "--cflash-image",
            fat,
            "--arm9gdb=1024",
            "--disable-sound",
            "--3d-engine=0",
        ]
    ]


def test_run_in_the_host_prefers_the_graphical_emulator(machine: Machine) -> None:
    machine.installed = {"desmume", "desmume-cli"}

    assert bmde("run", "-b", "host").exit_code == 0
    assert machine.commands[0][0] == "/usr/bin/desmume"


def test_run_with_flatpak(machine: Machine) -> None:
    machine.installed = {"flatpak"}

    assert bmde("run", "-b", "flatpak").exit_code == 0
    assert machine.commands == [["flatpak", "run", "org.desmume.DeSmuME", str(Path.cwd() / "Hello.nds")]]


# ---- patch


def test_patch_in_docker(machine: Machine) -> None:
    assert bmde("patch").exit_code == 0
    (cmd,) = machine.commands
    assert option(cmd, "-v") == [f"{Path.cwd()}:/input/Hello:rw"]
    assert option(cmd, "-w") == ["/input/Hello"]
    assert cmd[-3:] == ["aleixmt/dlditool:1.15.0", "mpcf.dldi", "/input/Hello/Hello.nds"]


def test_patch_a_rom_of_another_directory_without_a_tty(machine: Machine, tmp_path: Path) -> None:
    other = tmp_path / "Other"
    other.mkdir()
    (other / "Other.nds").touch()

    assert bmde("patch", "-d", str(other), "--no-interactive").exit_code == 0
    (cmd,) = machine.commands
    assert "-it" not in cmd
    assert cmd[-1] == "/input/Other/Other.nds"


def test_patch_in_docker_with_another_driver(machine: Machine) -> None:
    assert bmde("patch", "--entrypoint", "/bin/sh", "--", "r4.dldi", "game.nds").exit_code == 0
    (cmd,) = machine.commands
    assert option(cmd, "--entrypoint") == ["/bin/sh"]
    assert cmd[-2:] == ["r4.dldi", "game.nds"]


def test_patch_in_the_host_with_the_driver_of_the_bmde(machine: Machine, tmp_path: Path) -> None:
    """The BMDE installs the driver in the dldi/ directory of dlditool, where it finds the drivers given by name."""
    machine.installed = {"dlditool"}
    dlditool = tmp_path / "bmde" / "dlditool" / "dlditool"
    (dlditool.parent / "dldi").mkdir(parents=True)
    (dlditool.parent / "dldi" / "mpcf.dldi").touch()

    assert bmde("patch", "-b", "host", "--entrypoint", str(dlditool)).exit_code == 0
    assert machine.commands == [[str(dlditool), "mpcf.dldi", str(Path.cwd() / "Hello.nds")]]


class FakeDownload:
    """The response of urlopen, counting the downloads."""

    downloads = 0

    def __init__(self, data: bytes) -> None:
        self.data = data

    def __call__(self, url: str, timeout: float) -> "FakeDownload":
        assert url == "https://www.chishm.com/DLDI/downloads/mpcf.dldi"
        FakeDownload.downloads += 1
        return self

    def __enter__(self) -> "FakeDownload":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def read(self) -> bytes:
        return self.data


@pytest.fixture
def driver_download(monkeypatch: pytest.MonkeyPatch) -> FakeDownload:
    import hashlib
    import urllib.request

    from bmde.commands.patch.backends import host

    download = FakeDownload(b"DLDI driver")
    FakeDownload.downloads = 0
    monkeypatch.setattr(urllib.request, "urlopen", download)
    monkeypatch.setattr(host, "DLDI_DRIVER_SHA256", hashlib.sha256(download.data).hexdigest())
    return download


def test_patch_in_the_host_downloads_the_driver_once(
    machine: Machine, tmp_path: Path, driver_download: FakeDownload
) -> None:
    machine.installed = {"dlditool"}
    cached = tmp_path / "home" / ".cache" / "bmde" / "dldi" / "mpcf.dldi"

    assert bmde("patch", "-b", "host").exit_code == 0
    assert bmde("patch", "-b", "host").exit_code == 0

    assert machine.commands[0] == ["/usr/bin/dlditool", str(cached), str(Path.cwd() / "Hello.nds")]
    assert cached.read_bytes() == b"DLDI driver"
    assert FakeDownload.downloads == 1


def test_patch_in_the_host_refuses_a_wrong_driver(machine: Machine, driver_download: FakeDownload) -> None:
    machine.installed = {"dlditool"}
    driver_download.data = b"something else"

    result = bmde("patch", "-b", "host")

    assert isinstance(result.exception, RuntimeError)
    assert "does not have the expected SHA-256" in str(result.exception)
    assert machine.commands == []


def test_dry_run_of_patch_does_not_download_the_driver(machine: Machine, driver_download: FakeDownload) -> None:
    machine.installed = {"dlditool"}

    assert bmde("patch", "-b", "host", "--dry-run").exit_code == 0
    assert FakeDownload.downloads == 0


# ---- debug


def test_debug_in_docker(machine: Machine) -> None:
    result = bmde("debug")

    assert result.exit_code == 0, result.output
    emulator, debugger = machine.commands
    assert emulator[-2:] == ["--arm9gdb=1024", "/roms/Hello.nds"]
    assert option(debugger, "--network") == ["bmde-debug"]
    assert option(debugger, "-v")[0] == f"{Path.cwd()}:/input/Hello:ro"
    assert option(debugger, "-w") == ["/input/Hello"]
    assert {"DEBUGGER=insight", "GDB_TARGET=desmume:1024"} <= set(option(debugger, "-e"))
    assert debugger[-2:] == ["aleixmt/insight:1.15.0", "Hello.elf"]
    # The emulator is stopped and its network removed when the debugger exits
    assert ["docker", "network", "rm", "bmde-debug"] in machine.docker_calls


def test_debug_in_docker_with_the_emulator_in_the_host(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    machine.installed = {"desmume"}
    monkeypatch.setenv("BMDE_DEBUG__RUN__EXECUTION_SETTINGS__BACKEND", "host")

    result = bmde("debug", "-b", "docker", "-p", "2000")

    assert result.exit_code == 0, result.output
    emulator, debugger = machine.commands
    assert emulator[0] == "/usr/bin/desmume"
    assert option(debugger, "--add-host") == ["host.docker.internal:host-gateway"]
    assert "GDB_TARGET=host.docker.internal:2000" in option(debugger, "-e")


def test_debug_in_the_host_with_gdb(machine: Machine) -> None:
    machine.installed = {"gdb-multiarch"}
    project = Path.cwd()

    result = bmde("debug", "-b", "host", "-g", "gdb-multiarch", "-e", str(project / "Hello.elf"))

    assert result.exit_code == 0, result.output
    debugger = machine.commands[1]
    assert debugger == [
        "/usr/bin/gdb-multiarch",
        "-ex",
        f"set substitute-path /input/Hello {project}",
        "-ex",
        "target remote localhost:1024",
        str(project / "Hello.elf"),
    ]


def test_debug_in_the_host_with_insight(machine: Machine) -> None:
    machine.installed = {"insight"}

    assert bmde("debug", "-b", "host").exit_code == 0
    debugger = machine.commands[1]
    assert debugger[0] == "/usr/bin/insight"
    assert "target remote localhost:1024" not in debugger


def test_debug_stops_the_emulator_if_the_debugger_fails(machine: Machine) -> None:
    result = bmde("debug", "-b", "host")

    assert isinstance(result.exception, RuntimeError)
    (_emulator,) = machine.commands
    assert ["docker", "network", "rm", "bmde-debug"] in machine.docker_calls


def test_debug_kills_an_emulator_that_does_not_stop(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    from bmde.commands.debug import command

    FakeProcess.wait_timeouts = True
    monkeypatch.setattr(command, "docker_remove_network", raise_called_process_error)

    assert bmde("debug").exit_code == 0
    (emulator,) = machine.processes
    assert emulator.killed


def raise_called_process_error(name: str) -> None:
    raise subprocess.CalledProcessError(1, ["docker", "network", "rm", name])


def test_debug_in_the_background_leaves_the_emulator_running(machine: Machine) -> None:
    from bmde.commands.debug.command import debug_command
    from bmde.commands.debug.settings import DebugSettings

    debugger = debug_command(nds=None, elf=None, background=True, settings=DebugSettings())

    assert isinstance(debugger, FakeProcess)
    assert ["docker", "network", "rm", "bmde-debug"] not in machine.docker_calls


# ---- git


VPN = [
    "--vpn-user",
    "student",
    "--vpn-password",
    "vpn-secret",
    "--vpn-gateway",
    "vpn.example.org",
    "--vpn-port",
    "443",
    "--ssh-user",
    "student-dni",
    "--ssh-password",
    "ssh-secret",
    "--ssh-server",
    "git.example.org",
    "--git-name",
    "Student",
    "--git-email",
    "student@example.org",
]


def test_git_through_the_running_vpn(machine: Machine) -> None:
    result = bmde("git", *VPN, "--", "clone", "repo")

    assert result.exit_code == 0, result.output
    (cmd,) = machine.commands
    assert option(cmd, "--network") == ["container:forti-vpn"]
    assert option(cmd, "-v")[0] == f"{Path.cwd()}:/repos/Hello:rw"
    assert cmd[-3:] == ["aleixmt/git-sshpass:1.15.0", "clone", "repo"]
    # The credentials are files in /run/secrets, never in the command or the environment of the container
    assert machine.secrets[0] == {
        "ssh_username": "student-dni",
        "ssh_password": "ssh-secret",  # pragma: allowlist secret
        "ssh_host": "git.example.org",
        "git_name": "Student",
        "git_email": "student@example.org",
    }
    assert option(cmd, "-e") == []
    assert "ssh-secret" not in " ".join(cmd)


def test_secret_files_are_only_readable_by_the_user_and_removed(machine: Machine) -> None:
    # In memory (tmpfs) and only accessible by the user, when there is one
    Path(os.environ["XDG_RUNTIME_DIR"]).mkdir(mode=0o700)
    assert bmde("git", *VPN).exit_code == 0
    sources = [Path(volume.partition(":")[0]) for volume in option(machine.commands[0], "-v")[1:]]
    assert sources
    assert all(not source.exists() for source in sources)
    assert sources[0].parent.parent == Path(os.environ["XDG_RUNTIME_DIR"])


def test_git_without_the_vpn(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    machine.vpn_health = ["absent"]

    assert bmde("git", *VPN, "--no-vpn").exit_code == 0
    monkeypatch.setenv("BMDE_GIT__VPN__ENABLED", "false")
    assert bmde("git", *VPN).exit_code == 0

    # Only git, in the default network of Docker
    first, second = machine.commands
    assert option(first, "--network") == option(second, "--network") == []
    assert not [call for call in machine.docker_calls if call[1] == "inspect"]
    assert "vpn_password" not in machine.secrets[0]

    # --vpn wins over the settings
    machine.vpn_health = ["healthy"]
    assert bmde("git", *VPN, "--vpn").exit_code == 0
    assert option(machine.commands[-1], "--network") == ["container:forti-vpn"]


def test_git_starts_the_vpn_and_waits_for_it(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    machine.vpn_health = ["unhealthy", "starting", "starting", "healthy"]

    assert bmde("git", *VPN, "--entrypoint", "/bin/sh").exit_code == 0
    vpn, git = machine.commands
    assert ["docker", "rm", "-f", "forti-vpn"] in machine.docker_calls
    assert option(vpn, "--name") == ["forti-vpn"]
    assert option(vpn, "--cap-add") == ["NET_ADMIN"]
    # Only the credentials of the VPN, and only the ones that are set
    assert machine.secrets[0] == {
        "vpn_username": "student",
        "vpn_password": "vpn-secret",  # pragma: allowlist secret
        "vpn_host": "vpn.example.org",
        "vpn_port": "443",
    }
    assert option(vpn, "-e") == []
    assert vpn[-1] == "aleixmt/forticlient:1.15.0"
    assert option(git, "--entrypoint") == ["/bin/sh"]


def test_git_aborts_when_the_vpn_does_not_start(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    machine.vpn_health = ["absent", "starting", "absent"]

    result = bmde("git", *VPN)

    assert result.exit_code == 1
    assert len(machine.commands) == 1  # only the VPN


def test_git_times_out_waiting_for_the_vpn(machine: Machine) -> None:
    from bmde.commands.git.backends import docker as git_docker
    from bmde.commands.git.spec import GitSpecOpts
    from bmde.core.exec import ExecOptions

    machine.vpn_health = ["absent"]
    spec = GitSpecOpts(Path.cwd(), *([None] * 13))

    with pytest.raises(TimeoutError):
        git_docker._ensure_vpn_healthy(spec, ExecOptions(), timeout_s=0)


def test_git_fails_when_the_broken_vpn_cannot_be_removed(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    machine.vpn_health = ["unhealthy"]
    query = machine.query

    def rm_fails(cmd: list[str], **kwargs: Any) -> Any:
        if cmd[:2] == ["docker", "rm"]:
            raise subprocess.CalledProcessError(1, cmd)
        return query(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "run", rm_fails)

    result = bmde("git", *VPN)

    assert isinstance(result.exception, RuntimeError)
    assert "unhealthy container" in str(result.exception)


def test_dry_run_of_git_does_not_wait_for_the_vpn(machine: Machine) -> None:
    machine.vpn_health = ["absent"]

    assert bmde("git", *VPN, "--dry-run").exit_code == 0
    assert machine.commands == []
    assert not [call for call in machine.docker_calls if call[1] in ("inspect", "rm")]


def test_git_in_the_host(machine: Machine) -> None:
    machine.installed = {"git"}

    assert bmde("git", "-b", "host", "--", "status").exit_code == 0
    assert machine.commands == [["/usr/bin/git", "status"]]


def test_git_in_the_host_without_git() -> None:
    from bmde.commands.git.backends.host import HostRunner
    from bmde.commands.git.spec import GitSpecOpts
    from bmde.core.exec import ExecOptions

    spec = GitSpecOpts(Path.cwd(), *([None] * 13))
    original = shutil.which
    try:
        shutil.which = lambda name: None  # type: ignore[assignment]
        assert HostRunner().run(spec, ExecOptions()) == 127
    finally:
        shutil.which = original


# ---- check


def test_check_lists_the_backends_of_every_service(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    machine.installed = {"git"}
    monkeypatch.setenv("BMDE_GIT__EXECUTION_SETTINGS__BACKEND", "host")
    monkeypatch.setenv("BMDE_RUN__EXECUTION_SETTINGS__BACKEND", "flatpak")

    result = bmde("check")

    assert result.exit_code == 0, result.output
    assert "Service: Git\n    Selected backend: host ✅" in result.output
    assert "Service: Run\n    Selected backend: flatpak 🚫" in result.output
    assert "Service: Build\n    Selected backend: Auto (None configured)" in result.output
    assert "      - docker: ✅" in result.output


def test_check_without_settings_loads_them(machine: Machine, capsys: pytest.CaptureFixture[str]) -> None:
    from bmde.commands.check.command import check_command

    check_command()

    assert "Service: Patch" in capsys.readouterr().out


def test_check_reports_an_unknown_backend(machine: Machine, capsys: pytest.CaptureFixture[str]) -> None:
    from bmde.commands.check.command import check_command
    from bmde.core.types import BackendOptions

    settings = Settings()
    settings.patch.execution_settings.backend = BackendOptions.FLATPAK
    check_command(settings)

    assert "Selected backend: flatpak (Unknown backend?)" in capsys.readouterr().out


# ---- global options


def test_log_level_flags_and_log_file(machine: Machine, tmp_path: Path) -> None:
    log_file = tmp_path / "bmde.log"

    result = bmde("-v", "--trace", "-l", str(log_file), "build", "--dry-run")

    assert result.exit_code == 0, result.output
    text = log_file.read_text()
    assert "More than one log level" in text
    assert "[dry-run] docker run" in text


@pytest.mark.parametrize("flag", ["-q", "-Q"])
def test_quiet_flags(machine: Machine, tmp_path: Path, flag: str) -> None:
    log_file = tmp_path / "bmde.log"

    assert bmde(flag, "-l", str(log_file), "build", "--dry-run").exit_code == 0
    assert "[dry-run]" not in log_file.read_text()


def test_secrets_are_hidden_in_the_logs(machine: Machine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Also inside the command logged by run_cmd, where they are an argument of the message."""
    log_file = tmp_path / "bmde.log"
    monkeypatch.setenv("BMDE_GIT__VPN__PASSWORD", "vpn-secret")
    monkeypatch.setenv("BMDE_GIT__SSH__USERNAME", "student-dni")

    assert bmde("--trace", "-l", str(log_file), "git", "--dry-run").exit_code == 0
    text = log_file.read_text()
    # The command only has where the secrets are mounted, and the settings logged in trace mode are masked
    assert ":/run/secrets/vpn_password:ro" in text
    assert "password='*****'" in text
    assert "vpn-secret" not in text
    assert "student-dni" not in text


def test_api_exposes_the_commands() -> None:
    from bmde import api

    assert callable(api.build_command)
    assert callable(api.run_command)


# ---- background, entrypoints and the paths of the API


@pytest.mark.parametrize("command", ["build", "run", "patch", "debug"])
def test_background_commands_return_while_the_tool_runs(machine: Machine, command: str) -> None:
    result = bmde(command, "-B")

    assert result.exit_code == 0, result.output
    assert machine.processes


def test_git_in_the_background(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BMDE_GIT__EXECUTION_SETTINGS__BACKGROUND", "true")

    assert bmde("git", *VPN, "-d", str(Path.cwd())).exit_code == 0
    assert machine.processes


def test_settings_arguments_follow_the_cli_ones(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BMDE_BUILD__EXECUTION_SETTINGS__ARGUMENTS", '["-j4"]')
    monkeypatch.setenv("BMDE_RUN__EXECUTION_SETTINGS__ARGUMENTS", '["--3d-engine=0"]')
    monkeypatch.setenv("BMDE_DEBUG__EXECUTION_SETTINGS__ARGUMENTS", '["-nx"]')

    assert bmde("build", "clean").exit_code == 0
    assert bmde("run").exit_code == 0
    assert bmde("debug", "--", "-q").exit_code == 0
    build, run, _, debugger = machine.commands
    assert build[-2:] == ["clean", "-j4"]
    assert run[-2:] == ["--3d-engine=0", "/roms/Hello.nds"]
    assert debugger[-3:] == ["Hello.elf", "-q", "-nx"]


def test_host_build_with_devkitpro_environment(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    machine.installed = {"make", "arm-none-eabi-gcc"}
    monkeypatch.setenv("DEVKITPRO", "/opt/devkitpro")
    monkeypatch.setenv("DEVKITARM", "/opt/devkitpro/devkitARM")

    assert bmde("build", "-b", "host", "--entrypoint", "/usr/local/bin/gmake").exit_code == 0
    assert machine.commands == [["/usr/local/bin/gmake"]]


def test_host_tools_with_another_entrypoint(machine: Machine) -> None:
    machine.installed = {"dlditool", "desmume", "insight"}

    # The arguments replace the default driver and ROM, as with the docker backend
    assert bmde("patch", "-b", "host", "--entrypoint", "/opt/dlditool", "--", "r4.dldi", "game.nds").exit_code == 0
    assert bmde("run", "-b", "host", "--entrypoint", "/opt/desmume").exit_code == 0
    assert bmde("debug", "-b", "host", "--entrypoint", "/opt/insight").exit_code == 0
    patch, run, _, debugger = machine.commands
    assert patch == ["/opt/dlditool", "r4.dldi", "game.nds"]
    assert run[0] == "/opt/desmume"
    assert debugger[0] == "/opt/insight"


def test_docker_tools_with_another_entrypoint(machine: Machine) -> None:
    assert bmde("run", "--entrypoint", "/bin/sh").exit_code == 0
    assert bmde("debug", "--entrypoint", "/bin/bash").exit_code == 0
    run, _, debugger = machine.commands
    assert option(run, "--entrypoint") == ["/bin/sh"]
    assert option(debugger, "--entrypoint") == ["/bin/bash"]


def test_dry_run_of_debug(machine: Machine) -> None:
    assert bmde("debug", "--dry-run").exit_code == 0
    assert machine.commands == []
    assert not [call for call in machine.docker_calls if call[1] == "network"]


def test_backends_called_by_the_api_without_arguments(machine: Machine) -> None:
    """The API may give no arguments at all, unlike the CLI (which always gives a list)."""
    from bmde.commands.build.backends.docker import DockerRunner as BuildDocker
    from bmde.commands.build.backends.host import HostRunner as BuildHost
    from bmde.commands.build.spec import BuildSpecOpts
    from bmde.commands.debug.backends.docker import DockerRunner as DebugDocker
    from bmde.commands.debug.backends.host import HostRunner as DebugHost
    from bmde.commands.debug.command import create_debug_spec
    from bmde.commands.git.backends.docker import DockerRunner as GitDocker
    from bmde.commands.git.backends.host import HostRunner as GitHost
    from bmde.commands.git.spec import GitSpecOpts
    from bmde.commands.patch.backends.host import HostRunner as PatchHost
    from bmde.commands.patch.spec import PatchSpecOpts
    from bmde.commands.run.backends.docker import DockerRunner as RunDocker
    from bmde.commands.run.backends.host import HostRunner as RunHost
    from bmde.commands.run.command import create_run_spec
    from bmde.core.exec import ExecOptions

    machine.installed = {"git"}
    project = Path.cwd()
    no_arguments = ExecOptions(interactive=False)
    run = create_run_spec(nds_rom=None, directory=None).RunSpecOpts
    debug = create_debug_spec(nds=None, elf=None).DebugSpecOpts
    git = GitSpecOpts(project, *([None] * 13))

    BuildDocker().run(BuildSpecOpts(d=project), no_arguments)
    BuildHost().run(BuildSpecOpts(d=project), no_arguments)
    RunDocker().run(run, no_arguments)
    RunHost().run(run, no_arguments)
    DebugDocker().run(debug, no_arguments)
    DebugHost().run(debug, no_arguments)
    # dlditool is not in the PATH, so it is looked for (with its dldi/ directory) in the current directory
    (project / "dldi").mkdir()
    (project / "dldi" / "mpcf.dldi").touch()
    PatchHost().run(PatchSpecOpts(nds_rom=project / "Hello.nds"), no_arguments)
    GitHost().run(git, no_arguments)
    GitDocker().run(git, no_arguments)

    commands = machine.commands
    build_docker, build_host, run_docker, run_host, debug_docker, debug_host, patch_host, git_host, git_docker = (
        commands
    )
    assert build_docker[-1] == "aleixmt/devkitarm-nds:1.15.0"
    assert run_docker[-2:] == ["aleixmt/desmume:1.15.0", "/roms/Hello.nds"]
    assert "-it" not in build_docker
    assert build_host == ["make"]  # not in the PATH: the plain name
    assert run_host == ["desmume", str(project / "Hello.nds")]
    assert debug_docker[-1] == "Hello.elf"
    assert debug_host[0] == "arm-eabi-insight"
    assert patch_host == ["dlditool", "mpcf.dldi", str(project / "Hello.nds")]
    assert git_host == ["/usr/bin/git"]
    assert git_docker[-1] == "aleixmt/git-sshpass:1.15.0"
    # The default check of a backend passes
    assert BuildDocker().check()


def test_git_starts_the_vpn_without_a_tty(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    machine.vpn_container_exists = False
    # Unhealthy while the VPN starts is not a failure, only after having been starting
    machine.vpn_health = ["absent", "unhealthy", "healthy"]

    assert bmde("git", *VPN, "--no-interactive").exit_code == 0
    vpn, git = machine.commands
    assert ["docker", "rm", "-f", "forti-vpn"] not in machine.docker_calls
    assert "-it" not in vpn
    assert "-it" not in git


def test_api_loads_the_settings_when_not_given(machine: Machine, monkeypatch: pytest.MonkeyPatch) -> None:
    from bmde.commands.build.command import build_command
    from bmde.commands.debug.command import debug_command
    from bmde.commands.git.command import create_git_spec, git_command
    from bmde.commands.patch.command import patch_command
    from bmde.commands.run.command import run_command

    monkeypatch.setenv("BMDE_DOCKER__IMAGE_TAG", "sha-0123abc")

    assert build_command(d=None) == 0
    assert run_command(nds_rom=None) == 0
    assert patch_command(d=None) == 0
    assert git_command(d=None) == 0
    assert debug_command(nds=None, elf=None) == 0
    assert all(cmd[0] == "docker" for cmd in machine.commands)
    assert "aleixmt/devkitarm-nds:sha-0123abc" in machine.commands[0]
    assert create_git_spec(d=None).GitSpecOpts.d == Path.cwd()


def test_specs_have_defaults_without_settings(machine: Machine) -> None:
    from bmde.commands.build.command import create_build_spec
    from bmde.commands.patch.command import create_patch_spec
    from bmde.core.types import BackendOptions

    assert create_build_spec(d=None).SpecExecOpts.backend == BackendOptions.DOCKER
    assert create_patch_spec(d=None).PatchSpecOpts.nds_rom == Path.cwd() / "Hello.nds"
