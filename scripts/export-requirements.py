#!/usr/bin/env python3
"""
Write requirements/<group>.in for every dependency group of pyproject.toml, which `make lock` compiles into the pinned
requirements/<group>.txt.

pip-compile cannot read PEP 735 dependency groups, so each .in holds the runtime dependencies of the package plus the
group (with its `include-group` entries resolved). Dependabot then sees a plain .in/.txt pair of pip-compile, which is
the layout it knows how to update.

With --check nothing is written: it fails if a .in is out of date with pyproject.toml, or if a .txt misses a package of
its .in (a dependency added without running `make lock`).
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_DIR = ROOT / "requirements"
HEADER = "# GENERATED from pyproject.toml by `make lock`, edit the dependencies there instead\n"
NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def canonical_name(requirement: str) -> str:
    match = NAME_RE.match(requirement)
    if match is None:
        raise ValueError(f"Cannot parse the name of requirement {requirement!r}")
    return re.sub(r"[-_.]+", "-", match.group(1)).lower()


def resolve_group(groups: dict[str, list[str | dict[str, str]]], name: str, seen: tuple[str, ...] = ()) -> list[str]:
    if name in seen:
        raise ValueError(f"Dependency group {name!r} includes itself through {' -> '.join(seen)}")
    requirements: list[str] = []
    for entry in groups[name]:
        if isinstance(entry, str):
            requirements.append(entry)
        else:
            requirements += resolve_group(groups, entry["include-group"], (*seen, name))
    return requirements


def render_in_files() -> dict[Path, str]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    runtime: list[str] = pyproject["project"]["dependencies"]
    groups: dict[str, list[str | dict[str, str]]] = pyproject["dependency-groups"]
    files: dict[Path, str] = {}
    for group in groups:
        lines = [HEADER, "\n# Runtime dependencies of bmde\n", *(f"{r}\n" for r in runtime)]
        lines += [f"\n# Dependency group {group}\n", *(f"{r}\n" for r in resolve_group(groups, group))]
        files[REQUIREMENTS_DIR / f"{group}.in"] = "".join(lines)
    return files


def pinned_names(lock: Path) -> set[str]:
    # Package lines start at column 0; the indented lines and the rest are comments of pip-compile
    return {canonical_name(line) for line in lock.read_text(encoding="utf-8").splitlines() if line[:1].isalnum()}


def check(files: dict[Path, str]) -> int:
    status = 0
    for path, content in files.items():
        relative = path.relative_to(ROOT)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            print(f"{relative} is outdated, run 'make lock'")
            status = 1
            continue
        lock = path.with_suffix(".txt")
        if not lock.exists():
            print(f"{lock.relative_to(ROOT)} is missing, run 'make lock'")
            status = 1
            continue
        wanted = {canonical_name(line) for line in content.splitlines() if line[:1].isalnum()}
        missing = sorted(wanted - pinned_names(lock))
        if missing:
            print(f"{lock.relative_to(ROOT)} does not pin {', '.join(missing)}, run 'make lock'")
            status = 1
    return status


def main() -> int:
    files = render_in_files()
    if "--check" in sys.argv[1:]:
        return check(files)
    REQUIREMENTS_DIR.mkdir(exist_ok=True)
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
