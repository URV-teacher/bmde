import textwrap
from pathlib import Path
from typing import Any, get_origin

import rtoml
import typer

from bmde.config.fields import ConfigField, get_value, iter_sections
from bmde.config.loader import load_settings
from bmde.config.schema import Settings

DEFAULT_CONFIG_HEADER = (
    "# This file can be generated with the shell command 'bmde --show-default-config > bmde.toml'\n"
    "# Options that are commented out are unset by default. Uncomment them to set a value.\n"
)


def placeholder(field: ConfigField) -> str:
    """TOML-like placeholder shown for an option that has no value."""
    if field.choices:
        return '"<' + "|".join(field.choices) + '>"'
    if get_origin(field.annotation) is list:
        return '["<arg>", ...]'
    if field.annotation is int:
        return "<int>"
    if field.annotation is bool:
        return "<true|false>"
    if field.annotation is Path:
        return '"<path>"'
    return '"<str>"'


def format_value(key: str, value: Any) -> str:
    """Formats a single TOML ``key = value`` line."""
    return rtoml.dumps({key: value}).strip()


def render_config(settings: Settings, template: bool) -> str:
    """
    Renders the settings as a documented TOML file. Each option is preceded by its description and allowed values, and
    unset options are commented out with a placeholder.

    Args:
        settings: Settings to render.
        template: Render the options with a runtime-computed default (e.g. the timestamped log file) as a commented
            placeholder, so the output is the same on every execution.

    Returns:
        The TOML text.
    """
    data = settings.model_dump(mode="json", by_alias=True)
    blocks: list[str] = []
    for path, model, leaves in iter_sections(Settings):
        # Empty top-level tables are kept, so every command has its own section
        if not leaves and len(path) != 1:
            continue
        lines = [f"[{'.'.join(path)}]"]
        if model.__doc__:
            lines.insert(0, f"# {model.__doc__.strip()}")
        for field in leaves:
            if field.description:
                lines.extend(f"# {line}" for line in textwrap.wrap(field.description, width=118))
            if field.choices:
                lines.append(f"# Allowed values: {', '.join(field.choices)}")
            value = get_value(data, field.path)
            if template and field.dynamic_default:
                lines.append(f'# {field.key} = "{field.dynamic_default}"')
            elif value is None:
                lines.append(f"# {field.key} = {placeholder(field)}")
            else:
                lines.append(format_value(field.key, value))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def get_settings(default_only: bool) -> str:
    settings = Settings() if default_only else load_settings()
    return render_config(settings, template=default_only)


def get_default_config() -> str:
    """Documented TOML file with every option and its default value."""
    return DEFAULT_CONFIG_HEADER + "\n" + get_settings(default_only=True)


def show_config_callback(value: bool) -> None:
    if value:
        typer.echo(get_settings(default_only=False), nl=False)
        raise typer.Exit()


def show_default_config_callback(value: bool) -> None:
    if value:
        typer.echo(get_default_config(), nl=False)
        raise typer.Exit()
