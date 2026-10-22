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
