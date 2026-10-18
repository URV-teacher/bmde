from pathlib import Path

import pytest
from bmde.commands.debug.command import EMULATOR_LOG_FILE, create_debug_spec
from bmde.commands.debug.settings import DebugSettings
from bmde.commands.run.settings import RunSettings
from bmde.core.docker import docker_screen_args
from bmde.core.types import DebuggerOptions, DockerOutputOptions


def make_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Creates a project folder with the ROM and the ELF of a program, as the current directory."""
    (tmp_path / "Game.nds").touch()
    (tmp_path / "Game.elf").touch()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_debug_runs_emulator_with_run_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The emulator is run in debug mode, with the settings of run, in the background and logging to a file."""
    project = make_project(tmp_path, monkeypatch)
    settings = DebugSettings(run=RunSettings(sound=False, arm9_debug_port=1000))

    spec = create_debug_spec(nds=None, elf=None, settings=settings)

    run_opts = spec.DebugSpecOpts.RunSpec.RunSpecOpts
    assert run_opts.nds_rom == project / "Game.nds"
    assert run_opts.debug
    assert not run_opts.sound
    assert run_opts.arm9_debug_port == 1000
    run_exec = spec.DebugSpecOpts.RunSpec.SpecExecOpts
    assert run_exec.background
    assert run_exec.log_file == EMULATOR_LOG_FILE
    assert spec.DebugSpecOpts.elf == project / "Game.elf"
    assert spec.DebugSpecOpts.debugger == DebuggerOptions.INSIGHT


def test_debug_cli_options_override_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Port and screen given to debug apply to the emulator too."""
    make_project(tmp_path, monkeypatch)
    spec = create_debug_spec(
        nds=None,
        elf=None,
        port=2000,
        debugger=DebuggerOptions.GDB_MULTIARCH,
        docker_screen=DockerOutputOptions.VNC,
    )

    assert spec.DebugSpecOpts.RunSpec.RunSpecOpts.arm9_debug_port == 2000
    assert spec.DebugSpecOpts.RunSpec.RunSpecOpts.graphical_output == DockerOutputOptions.VNC
    assert spec.DebugSpecOpts.docker_screen == DockerOutputOptions.VNC
    assert spec.DebugSpecOpts.debugger == DebuggerOptions.GDB_MULTIARCH


def test_docker_screen_args_vnc_publishes_port() -> None:
    mounts, envs, ports = docker_screen_args(DockerOutputOptions.VNC, vnc_host_port=5901)

    assert mounts == []
    assert envs == ["-e", "MODE=vnc"]
    assert ports == ["-p", "5901:5900"]


def test_docker_screen_args_none() -> None:
    assert docker_screen_args(DockerOutputOptions.NONE) == ([], ["-e", "MODE=none"], [])
