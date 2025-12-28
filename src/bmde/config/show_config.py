import rtoml
import typer

from bmde.config.loader import load_settings
from bmde.config.schema import Settings


def get_settings(default_only: bool) -> str:
    if default_only:
        settings = Settings()
    else:
        settings = load_settings()

    # Convert to TOML and print
    toml_str = rtoml.dumps(settings.model_dump(mode="json", by_alias=True))

    # Post-process to comment out null values and add spacing
    lines = []
    for i, line in enumerate(toml_str.splitlines()):
        stripped = line.strip()

        # Add blank line before section headers if missing
        if stripped.startswith("[") and i > 0 and lines and lines[-1].strip() != "":
            lines.append("")

        if stripped.endswith("= null") or stripped.endswith('= "null"'):
            lines.append(f"# {line}")
        else:
            lines.append(line)
    toml_str = "\n".join(lines)

    return toml_str


def show_config_callback(value: bool) -> None:
    if value:
        toml_str = get_settings(default_only=False)
        typer.echo(toml_str)
        raise typer.Exit()


def show_default_config_callback(value: bool) -> None:
    if value:
        toml_str = get_settings(default_only=True)
        final_str = "# This file can be generated with the shell command 'bmde --show-default-config > bmde.toml'\n\n"
        final_str += toml_str
        typer.echo(final_str)
        raise typer.Exit()
