#!/usr/bin/env python3
import re
from pathlib import Path

INCLUDE_RE = re.compile(
    r'^\s*--8<--\s+"([^":]+)(?::(\d+)?:(\d+)?)?"\s*$'
)

def expand_include(line: str, base_dir: Path) -> list[str]:
    """
    Expands a MkDocs-style include directive into file contents.
    Supports optional :start:end line ranges.
    """
    match = INCLUDE_RE.match(line)
    if not match:
        return [line]

    path, start, end = match.groups()
    #print(f"start {str(start)} end {str(end)} path {str(path)}")
    file_path = (base_dir / path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"Included file not found: {file_path}")

    lines = open(file_path).readlines()

    # Apply line slicing if specified (1-based, inclusive)
    if start or end:
        s = int(start) - 1 if start else 0
        e = int(end) if end else len(lines)
        lines = lines[s:e]

    lines.append("\n")
    return lines


def render_file(src: Path, dst: Path):
    base_dir = src.parent.parent.parent
    output = []

    for line in open(src).readlines():
        expanded = expand_include(line, base_dir)
        #print(expanded)
        output.extend(expanded)

    dst.write_text("".join(output))


def main():
    SRC = "docs/getting-started/host_components_installation.md"
    DST = "docs/getting-started/host_components_installation_substituted.md"

    src = Path(SRC)
    dst = Path(DST)

    render_file(src, dst)
    print(f"Generated {dst} from {src}")


if __name__ == "__main__":
    main()
