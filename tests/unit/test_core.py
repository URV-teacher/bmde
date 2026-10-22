import logging
import os
import socket
import subprocess
import sys
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any

import pytest

from bmde.core import docker, file_utils, os_utils, paths
from bmde.core.backend import Backend
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.service import Service
from bmde.core.types import BackendOptions, DockerOutputOptions, LogLevel


@pytest.mark.parametrize("enum", [BackendOptions, DockerOutputOptions, LogLevel])
def test_options_parse_case_insensitively(enum: Any, capsys: pytest.CaptureFixture[str]) -> None:
    member = next(iter(enum))
    assert enum.parse(f"  {member.value.upper()} ") is member
    # Parsing prints nothing, which would mess the output of the CLI
    assert capsys.readouterr().out == ""
    assert enum.parse("") is None
    assert enum.parse(None) is None
    with pytest.raises(ValueError, match="Valid: "):
        enum.parse("nonsense")


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (LogLevel.TRACE, 0),
        (LogLevel.DEBUG, logging.DEBUG),
        (LogLevel.INFO, logging.INFO),
        (LogLevel.WARNING, logging.WARNING),
        (LogLevel.ERROR, logging.ERROR),
        (LogLevel.QUIET, logging.CRITICAL + 10),
    ],
)
def test_log_levels_map_to_logging_levels(level: LogLevel, expected: int) -> None:
    assert level.to_logging_level() == expected


# ---- exec


def test_dry_run_does_not_execute(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("executed")

    monkeypatch.setattr(subprocess, "call", fail)
    assert run_cmd(["rm", "-rf", "/"], ExecOptions(dry_run=True)) == 0
    assert run_cmd("rm -rf /", ExecOptions(dry_run=True)) == 0  # type: ignore[arg-type]


def test_output_goes_to_the_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "out.log"
    script = "import sys; print('out', flush=True); print('err', file=sys.stderr)"

    assert run_cmd([sys.executable, "-c", script], ExecOptions(log_file=log_file)) == 0
    assert log_file.read_text().split() == ["out", "err"]


def test_background_returns_the_process(tmp_path: Path) -> None:
    handle = run_cmd([sys.executable, "-c", "pass"], ExecOptions(background=True, cwd=str(tmp_path)))

    assert isinstance(handle, subprocess.Popen)
    assert handle.wait() == 0


# ---- file_utils


def test_validate_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        file_utils.validate_file(tmp_path / "missing.nds")
    (tmp_path / "game.elf").touch()
    with pytest.raises(ValueError, match="Expected a .nds file"):
        file_utils.validate_file(tmp_path / "game.elf")
    (tmp_path / "game.NDS").touch()
    assert file_utils.validate_file(tmp_path / "game.NDS") == tmp_path / "game.NDS"


def test_resolve_nds_discovers_the_first_rom(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(FileNotFoundError):
        file_utils.resolve_nds(None, tmp_path)
    (tmp_path / "b.nds").touch()
    (tmp_path / "a.nds").touch()

    assert file_utils.resolve_nds(None, tmp_path) == (tmp_path / "a.nds", True)
    assert "Multiple .nds files" in caplog.text
    assert file_utils.resolve_nds(tmp_path / "b.nds", tmp_path) == (tmp_path / "b.nds", False)


def test_resolve_elf(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No .elf file"):
        file_utils.resolve_elf(None, tmp_path)
    (tmp_path / "game.elf").touch()
    (tmp_path / "game.nds").touch()
    assert file_utils.resolve_elf(None, tmp_path) == (tmp_path / "game.elf", True)
    assert file_utils.resolve_elf(tmp_path / "game.elf", tmp_path) == (tmp_path / "game.elf", False)
    with pytest.raises(ValueError, match="Expected a .elf file"):
        file_utils.resolve_elf(tmp_path / "game.nds", tmp_path)


# ---- os_utils


def test_is_command_available() -> None:
    assert os_utils.is_command_available(sys.executable)
    assert not os_utils.is_command_available("bmde-command-that-does-not-exist")


def test_host_uid_gid(monkeypatch: pytest.MonkeyPatch) -> None:
    assert os_utils.host_uid_gid() == (os.getuid(), os.getgid())

    def broken() -> int:
        raise OSError

    monkeypatch.setattr(os, "getuid", broken)
    assert os_utils.host_uid_gid() == (1000, 1000)


def test_host_uid_gid_without_getuid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delattr(os, "getuid")
    monkeypatch.setattr(subprocess, "check_output", lambda cmd, text: "1234\n" if cmd[1] == "-u" else "5678\n")
    assert os_utils.host_uid_gid() == (1234, 5678)

    def missing(*args: Any, **kwargs: Any) -> str:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "check_output", missing)
    assert os_utils.host_uid_gid() == (1000, 1000)


# ---- paths


def test_find_git_root(tmp_path: Path) -> None:
    nested = tmp_path / "repo" / "src" / "pkg"
    nested.mkdir(parents=True)
    assert paths.find_git_root(nested) is None or paths.find_git_root(nested) != tmp_path / "repo"
    (tmp_path / "repo" / ".git").mkdir()
    assert paths.find_git_root(nested) == tmp_path / "repo"


def test_find_first(tmp_path: Path) -> None:
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "x.nds").touch()
    assert paths.find_first([tmp_path / "a", tmp_path / "b"], "*.nds") == tmp_path / "b" / "x.nds"
    assert paths.find_first([tmp_path], "*.elf") is None


# ---- docker


class FakeSubprocess:
    """Records the docker commands and answers them with the given results (an exception to raise or an output)."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, result: Any = "") -> None:
        self.calls: list[list[str]] = []
        self.result = result
        monkeypatch.setattr(subprocess, "run", self._call)
        monkeypatch.setattr(subprocess, "check_output", self._call)

    def _call(self, cmd: list[str], **kwargs: Any) -> Any:
        self.calls.append(cmd)
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ("", True),
        (FileNotFoundError(), False),
        (subprocess.CalledProcessError(1, "docker"), False),
        (RuntimeError(), False),
    ],
)
def test_can_run_docker(monkeypatch: pytest.MonkeyPatch, result: Any, expected: bool) -> None:
    FakeSubprocess(monkeypatch, result)
    assert docker.can_run_docker() is expected


def test_containers_and_health(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeSubprocess(monkeypatch, "healthy\n")
    assert docker.docker_container_exists("vpn")
    assert docker.docker_inspect_health("vpn") == "healthy"
    fake.result = ""
    assert docker.docker_inspect_health("vpn") is None
    fake.result = subprocess.CalledProcessError(1, "docker")
    assert not docker.docker_container_exists("vpn")
    assert docker.docker_inspect_health("vpn") is None


def test_networks(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeSubprocess(monkeypatch)
    docker.ensure_network_is_present("net")  # exists: nothing is created
    docker.docker_remove_network("net")
    assert fake.calls[-1] == ["docker", "network", "rm", "net"]

    calls = []

    def missing(cmd: list[str], **kwargs: Any) -> Any:
        calls.append(cmd)
        if cmd[:3] == ["docker", "network", "inspect"]:
            raise subprocess.CalledProcessError(1, "docker")
        return ""

    monkeypatch.setattr(subprocess, "run", missing)
    monkeypatch.setattr(subprocess, "check_output", missing)
    docker.ensure_network_is_present("net")
    docker.docker_remove_network("net")
    assert ["docker", "network", "create", "net"] in calls
    assert ["docker", "network", "rm", "net"] not in calls


def test_docker_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))

    with docker.docker_secrets({"vpn_password": "hunter2", "vpn_port": None}) as mounts:  # pragma: allowlist secret
        (volume,) = mounts[1::2]
        source, target = volume.removesuffix(":ro").split(":")
        assert mounts[0] == "-v"
        assert target == "/run/secrets/vpn_password"
        assert Path(source).read_text() == "hunter2"
        assert Path(source).stat().st_mode & 0o777 == 0o600
        assert Path(source).parent.stat().st_mode & 0o777 == 0o700
        assert Path(source).parent.parent == tmp_path
    assert not Path(source).parent.exists()

    with docker.docker_secrets({"ssh_password": "secret"}, keep=True) as mounts:  # pragma: allowlist secret
        kept = Path(mounts[1].split(":")[0])
    assert kept.read_text() == "secret"


def test_project_is_mounted_by_its_name() -> None:
    assert docker.docker_project_dir(Path("/home/me/projects/Hello")) == "/input/Hello"


@pytest.fixture
def clean_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """An empty HOME and no variable of the X server or of the sound server of the machine."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for name in ("XAUTHORITY", "PULSE_SERVER", "PULSE_COOKIE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DISPLAY", ":1")
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    yield home


def test_x11_args_mount_the_cookie_when_there_is_one(clean_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mounts, envs = docker.host_x11_docker_args()
    assert mounts == ["-v", "/tmp/.X11-unix:/tmp/.X11-unix"]
    assert envs == ["-e", "DISPLAY=:1"]

    (clean_env / ".Xauthority").touch()
    mounts, envs = docker.host_x11_docker_args()
    assert f"{clean_env / '.Xauthority'}:{docker.CONTAINER_XAUTHORITY}:ro" in mounts
    assert f"XAUTHORITY={docker.CONTAINER_XAUTHORITY}" in envs

    mounts, envs = docker.docker_screen_args(DockerOutputOptions.HOST)[:2]
    assert "MODE=host" in envs


def listening_socket(path: Path) -> socket.socket:
    path.parent.mkdir(parents=True, exist_ok=True)
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(str(path))
    return sock


def test_pulse_args(clean_env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert docker.host_pulse_docker_args() == ([], [])

    with listening_socket(tmp_path / "runtime" / "pulse" / "native"):
        mounts, envs = docker.host_pulse_docker_args()
        assert mounts == ["-v", f"{tmp_path / 'runtime' / 'pulse' / 'native'}:{docker.CONTAINER_PULSE_SOCKET}"]
        assert envs == ["-e", f"PULSE_SERVER=unix:{docker.CONTAINER_PULSE_SOCKET}"]

        cookie = clean_env / ".config" / "pulse" / "cookie"
        cookie.parent.mkdir(parents=True)
        cookie.touch()
        mounts, envs = docker.host_pulse_docker_args()
        assert f"{cookie}:{docker.CONTAINER_PULSE_COOKIE}:ro" in mounts

    with listening_socket(tmp_path / "other.sock"):
        monkeypatch.setenv("PULSE_SERVER", f"unix:{tmp_path / 'other.sock'}")
        assert docker.host_pulse_docker_args()[0][1].startswith(str(tmp_path / "other.sock"))
    # A TCP server cannot be mounted
    monkeypatch.setenv("PULSE_SERVER", "tcp:localhost:4713")
    assert docker.host_pulse_docker_args() == ([], [])


class FakeBackend(Backend[Any]):
    def __init__(self, available: bool, result: Any) -> None:
        self.available = available
        self.result = result

    def is_available(self) -> bool:
        return self.available

    def run(self, spec: Any, exec_opts: ExecOptions) -> Any:
        return self.result


def test_service_uses_the_first_available_backend_that_runs() -> None:
    service: Service[Any, FakeBackend] = Service(
        [BackendOptions.HOST, BackendOptions.FLATPAK, BackendOptions.DOCKER],
        {
            BackendOptions.HOST: FakeBackend(False, 1),
            # A backend that returns no exit code nor process does not count as run
            BackendOptions.FLATPAK: FakeBackend(True, None),
            BackendOptions.DOCKER: FakeBackend(True, 3),
        },
    )
    assert service.run(None, ExecOptions()) == 3
    with pytest.raises(RuntimeError, match="No suitable backend"):
        service.run(None, ExecOptions(backend=BackendOptions.HOST))


def read_log(path: Path) -> str:
    for handler in logging.getLogger().handlers:
        handler.flush()
    return path.read_text()


@pytest.fixture
def reset_logging() -> Iterator[None]:
    yield
    logging.basicConfig(handlers=[logging.NullHandler()], force=True)


def test_logging_defaults_and_secrets(tmp_path: Path, reset_logging: None) -> None:
    from bmde.config.schema import Settings
    from bmde.core.logging import configure_logging_from_settings, get_logger, setup_logging

    setup_logging(None, tmp_path / "default.log")
    get_logger("test").debug("hidden")
    get_logger("test").info("shown")
    assert read_log(tmp_path / "default.log").splitlines()[-1].endswith("shown")
    # Without a log file, only the console
    setup_logging(logging.WARNING)
    assert len(logging.getLogger().handlers) == 1

    settings = Settings()
    settings.logging.file = tmp_path / "bmde.log"
    settings.logging.level = None  # type: ignore[assignment]
    settings.logging.hide_sensibles = False
    settings.git.vpn.password = "vpn-secret"  # pragma: allowlist secret
    settings.git.ssh.username = "student-dni"
    configure_logging_from_settings(settings)
    get_logger("test").info("password %s of %s, backend None", "vpn-secret", "student-dni")
    # Only the passwords are hidden, and an unset port does not hide every None
    assert read_log(tmp_path / "bmde.log").splitlines()[-1].endswith("password ***** of student-dni, backend None")


def test_image_tag_without_installed_package(monkeypatch: pytest.MonkeyPatch) -> None:
    def not_installed(name: str) -> str:
        raise PackageNotFoundError(name)

    monkeypatch.setattr(docker, "version", not_installed)
    assert docker.default_image_tag() == "latest"
