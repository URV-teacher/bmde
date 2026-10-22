"""Translates the options of the debug command into its spec.

The responsibility of this file and the similar ones under each command, is to translate the logic of the bmde interface
into the specification of the pure logic of the command, for example, translating shell into a corresponding entrypoint.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from subprocess import Popen

from bmde.core import logging
from bmde.core.exec import ExecOptions

from ...config.loader import load_settings
from ...core.docker import configure_docker_from_settings, docker_remove_network
from ...core.file_utils import resolve_elf
from ...core.logging import configure_logging_from_settings
from ...core.spec_opts import SpecExecOpts
from ...core.types import (
    BackendOptions,
    DebuggerOptions,
    DockerOutputOptions,
)
from ..run.command import create_run_spec, execute_run
from .service import DebugService
from .settings import DebugSettings
from .spec import DebugSpec, DebugSpecOpts

log = logging.get_logger(__name__)

# Seconds to wait for the emulator to exit after asking it to stop
EMULATOR_STOP_TIMEOUT = 10
# The emulator logs every packet of the debugger, which would mess the terminal of terminal debuggers
EMULATOR_LOG_FILE = Path(tempfile.gettempdir()) / "bmde-debug-emulator.log"


def create_debug_spec(
    nds: Path | None,
    elf: Path | None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    debugger: DebuggerOptions | None = None,
    docker_screen: DockerOutputOptions | None = None,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    port: int | None = None,
    settings: DebugSettings | None = None,
) -> DebugSpec:
    if settings is None:
        settings = DebugSettings()

    elf_resolved, _ = resolve_elf(elf, cwd=Path.cwd())

    # Default args are prepended to CLI args
    passed_args: list[str] = []
    if arguments is not None:
        passed_args += arguments
    if settings.execution_settings.arguments is not None:
        passed_args += settings.execution_settings.arguments

    # The emulator is run as the run command would do, but in debug mode and in the background
    run_spec = create_run_spec(
        nds_rom=nds,
        directory=Path.cwd(),
        arm9_debug_port=port,
        background=True,
        interactive=False,
        debug=True,
        dry_run=dry_run,
        graphical_output=docker_screen,
        settings=settings.run,
    )
    run_spec.SpecExecOpts.log_file = EMULATOR_LOG_FILE

    return DebugSpec(
        DebugSpecOpts=DebugSpecOpts(
            elf=elf_resolved,
            debugger=(
                debugger
                if debugger is not None
                else (settings.debugger if settings.debugger is not None else DebuggerOptions.INSIGHT)
            ),
            docker_screen=(docker_screen if docker_screen is not None else settings.docker_screen),
            RunSpec=run_spec,
        ),
        SpecExecOpts=SpecExecOpts(
            backend=(
                backend
                if backend is not None
                else (
                    settings.execution_settings.backend
                    if settings.execution_settings.backend is not None
                    else BackendOptions.DOCKER
                )
            ),
            entrypoint=(entrypoint if entrypoint is not None else settings.execution_settings.entrypoint),
            arguments=passed_args,
            dry_run=(dry_run if dry_run is not None else settings.execution_settings.dry_run),
            background=(background if background is not None else settings.execution_settings.background),
            interactive=True,
        ),
    )


def stop_emulator(spec: DebugSpec, emulator: int | Popen[bytes]) -> None:
    """Stops the emulator started by execute_debug and removes the resources created for it."""
    if isinstance(emulator, Popen) and emulator.poll() is None:
        log.info("Stopping the emulator")
        emulator.terminate()
        try:
            emulator.wait(timeout=EMULATOR_STOP_TIMEOUT)
        except subprocess.TimeoutExpired:
            emulator.kill()
            emulator.wait()

    run_spec = spec.DebugSpecOpts.RunSpec
    if run_spec.SpecExecOpts.backend == BackendOptions.DOCKER and not run_spec.SpecExecOpts.dry_run:
        try:
            docker_remove_network(run_spec.RunSpecOpts.docker_network)
        except subprocess.CalledProcessError:
            log.warning(f"Could not remove Docker network '{run_spec.RunSpecOpts.docker_network}'")


def execute_debug(spec: DebugSpec) -> int | Popen[bytes]:
    """Runs the emulator in debug mode and a debugger connected to it.

    The emulator is stopped when the debugger exits.
    """
    log.info(f"Emulator output is written to {EMULATOR_LOG_FILE}")
    emulator = execute_run(spec.DebugSpecOpts.RunSpec)

    try:
        debugger = DebugService().run(
            spec.DebugSpecOpts,
            ExecOptions(
                dry_run=spec.SpecExecOpts.dry_run,
                background=spec.SpecExecOpts.background,
                entrypoint=spec.SpecExecOpts.entrypoint,
                arguments=spec.SpecExecOpts.arguments,
                backend=spec.SpecExecOpts.backend,
                interactive=spec.SpecExecOpts.interactive,
            ),
        )
    except BaseException:
        stop_emulator(spec, emulator)
        raise

    if isinstance(debugger, Popen):
        # Debugger in the background: the emulator is left running, managed by the caller along with the debugger
        log.info("Debugger and emulator running in the background")
        return debugger

    stop_emulator(spec, emulator)
    return debugger


def debug_command(
    nds: Path | None,
    elf: Path | None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    debugger: DebuggerOptions | None = None,
    docker_screen: DockerOutputOptions | None = None,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    port: int | None = None,
    settings: DebugSettings | None = None,
) -> int | Popen[bytes]:
    if settings is None:
        full_settings = load_settings()
        configure_logging_from_settings(settings=full_settings)
        configure_docker_from_settings(settings=full_settings)
        settings = full_settings.debug

    log.debug(f"Settings for debug command:\n- {settings!s}\n")

    spec = create_debug_spec(
        nds=nds,
        elf=elf,
        arguments=arguments,
        backend=backend,
        background=background,
        debugger=debugger,
        docker_screen=docker_screen,
        dry_run=dry_run,
        entrypoint=entrypoint,
        port=port,
        settings=settings,
    )

    log.debug(f"Spec for debug command:\n- {spec!s}\n")

    return execute_debug(spec)
