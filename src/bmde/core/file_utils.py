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

from pathlib import Path

from bmde.core import logging

log = logging.get_logger(__name__)


def validate_file(p: Path, suffix: str = ".nds") -> Path:
    if not p.is_file():
        raise FileNotFoundError(f"{suffix} file not found: {p}")
    if p.suffix.lower() != suffix:
        raise ValueError(f"Expected a {suffix} file, got: {p.name}")
    return p


def discover_files_in_dir(search_dir: Path, suffix: str) -> tuple[Path, bool]:
    files = sorted(search_dir.glob(f"*{suffix}"))
    if not files:
        raise FileNotFoundError(f"No {suffix} file found in {search_dir}")
    if len(files) > 1:
        log.warning(
            "Multiple %s files found in %s; assuming '%s'.",
            suffix,
            search_dir,
            files[0].name,
        )
    log.info(f"Found {len(files)} {suffix} files in {search_dir}")
    return files[0], True


def resolve_nds(maybe_nds: Path | None, cwd: Path) -> tuple[Path, bool]:
    """Return (nds_path, assumed_flag). If maybe_nds is None, discover in cwd."""
    if maybe_nds is not None:
        return validate_file(maybe_nds), False
    return discover_files_in_dir(cwd, ".nds")


def resolve_elf(maybe_elf: Path | None, cwd: Path) -> tuple[Path, bool]:
    """Return (elf_path, assumed_flag). If maybe_elf is None, discover in cwd."""
    if maybe_elf is not None:
        return validate_file(maybe_elf, ".elf"), False
    return discover_files_in_dir(cwd, ".elf")
