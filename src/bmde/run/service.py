from __future__ import annotations

import logging
from pathlib import Path

from .backends.docker import DockerRunner
from .backends.flatpak import FlatpakRunner
from .backends.host import HostRunner
from .spec import RunSpec
from ..core.exec import ExecOptions

log = logging.getLogger(__name__)


def validate_nds_file(p: Path) -> Path:
    if not p.is_file():
        raise FileNotFoundError(f"NDS file not found: {p}")
    if p.suffix.lower() != ".nds":
        raise ValueError(f"Expected a .nds file, got: {p.name}")
    return p

def discover_nds_in_dir(search_dir: Path) -> tuple[Path, bool]:
    files = sorted(search_dir.glob("*.nds"))
    if not files:
        raise FileNotFoundError(f"No .nds file found in {search_dir}")
    if len(files) > 1:
        log.warning(
            "Multiple .nds files found in %s; assuming '%s'.",
            search_dir, files[0].name,
        )
    log.info(f"Found {len(files)} .nds files in {search_dir}")
    return files[0], True

def resolve_nds(maybe_nds: Path | None, cwd: Path) -> tuple[Path, bool]:
    """
    Return (nds_path, assumed_flag). If maybe_nds is None, discover in cwd.
    """
    if maybe_nds is not None:
        return validate_nds_file(maybe_nds), False
    return discover_nds_in_dir(cwd)

def choose_backend(env: str | None) -> list:
    order = ["host", "docker", "flatpak"]
    if env:
        order = [env]  # force
    mapping = {"host": HostRunner(), "docker": DockerRunner(), "flatpak": FlatpakRunner()}
    return [mapping[e] for e in order]

def run(spec: RunSpec, exec_opts: ExecOptions) -> int:
    for backend in choose_backend(spec.environment):
        if backend.is_available():
            return backend.run(spec, exec_opts)
    raise RuntimeError("No suitable backend available")
