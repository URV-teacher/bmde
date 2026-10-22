#!/usr/bin/env python3
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

"""Puts the text of LICENSE_HEADER as a comment at the top of each Python file given.

The header is the first block of comment lines of a file (after a shebang or encoding line) that mentions the word
"license". When LICENSE_HEADER changes, that block is replaced instead of a second header being inserted, which is what
the hooks that only look for the current text do. Empty files, such as most __init__.py, are left empty.

When LICENSE_HEADER itself is among the files given (it changed in a commit), every tracked Python file is updated.

Exits with 1 if it changed a file, so pre-commit reports it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HEADER_FILE = Path("LICENSE_HEADER")
MARKER = "license"


def render_header(text: str) -> list[str]:
    return [f"# {line}".rstrip() + "\n" for line in text.strip("\n").splitlines()]


def apply_header(source: str, header: list[str]) -> str:
    lines = source.splitlines(keepends=True)
    if not "".join(lines).strip():
        return source

    # A shebang and an encoding declaration only work on the first lines, so the header goes after them
    preamble: list[str] = []
    while lines and (lines[0].startswith("#!") or ("coding" in lines[0] and lines[0].startswith("#"))):
        preamble.append(lines.pop(0))

    block_end = 0
    while block_end < len(lines) and lines[block_end].startswith("#"):
        block_end += 1
    if MARKER in "".join(lines[:block_end]).lower():
        lines = lines[block_end:]
    while lines and not lines[0].strip():
        lines.pop(0)

    return "".join([*preamble, *header, "\n", *lines])


def tracked_python_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.py"], capture_output=True, text=True, check=True).stdout
    return [Path(name) for name in out.splitlines()]


def main(args: list[str]) -> int:
    text = HEADER_FILE.read_text(encoding="utf-8")
    if MARKER not in text.lower():
        # Otherwise the header could not be found again to be replaced when it changes
        print(f'{HEADER_FILE} must contain the word "{MARKER}"', file=sys.stderr)
        return 2
    header = render_header(text)

    files = [Path(arg) for arg in args if Path(arg) != HEADER_FILE]
    if len(files) < len(args):
        files = tracked_python_files()

    changed = False
    for path in files:
        source = path.read_text(encoding="utf-8")
        result = apply_header(source, header)
        if result != source:
            path.write_text(result, encoding="utf-8")
            print(f"Updated the license header of {path}")
            changed = True
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
