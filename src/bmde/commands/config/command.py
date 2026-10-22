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

"""Interactive configuration of BMDE.

Asks for the value of each option of the settings, showing the current value as default, and writes the answers to a
bmde.toml file.
"""

from __future__ import annotations

import shlex
from collections.abc import Collection, Sequence
from pathlib import Path
from typing import Any, get_origin

import rtoml
import typer
from pydantic import ValidationError
from rich.console import Console
from rich.markup import escape

from bmde.config.fields import ConfigField, get_value, has_value, iter_sections, set_value
from bmde.config.loader import CONFIG_FILE_NAME, ENV_PREFIX, ConfigSource, read_toml, user_config_file
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.paths import find_git_root, find_upwards

log = logging.get_logger(__name__)
console = Console()

# Answer that removes an option from the configuration file
UNSET = "unset"


def section_names() -> list[str]:
    return [".".join(path) for path, _, _ in iter_sections(Settings) if path]


def section_prefix(section: str | None) -> tuple[str, ...]:
    """Path of the section in the settings tree, or () for every section. Fails if the section does not exist."""
    if not section:
        return ()
    if section not in section_names():
        valid = ", ".join(name for name in section_names() if "." not in name)
        raise typer.BadParameter(f"Unknown section '{section}'. Valid: {valid}", param_hint="SECTION")
    return tuple(section.split("."))


def prompt_choice(label: str, options: list[str], default: str) -> str:
    """Prompts until the answer is one of the options (case-insensitive)."""
    while True:
        answer = str(typer.prompt(f"{label} ({'/'.join(options)})", default=default)).strip().lower()
        if answer in options:
            return answer
        console.print(f"  [red]{escape(answer)} is not one of {', '.join(options)}[/]")


def resolve_target(file: Path | None) -> Path:
    """Returns the file to write: the given one or the one chosen by the user between the repo and user config."""
    if file:
        return file
    cwd = Path.cwd()
    # A new file goes to the root of the repository, the last directory where the project config is looked for
    repo = find_upwards(CONFIG_FILE_NAME, start=cwd) or (find_git_root(cwd) or cwd) / CONFIG_FILE_NAME
    user = user_config_file()
    console.print("Where do you want to save the configuration?")
    console.print(f"  [bold]repo[/]: {escape(str(repo))} (only applies to this repository)")
    console.print(f"  [bold]user[/]: {escape(str(user))} (applies to every repository of your user)")
    choice = prompt_choice("Target", ["repo", "user"], default="repo")
    return repo if choice == "repo" else user


def _show(value: Any) -> str:
    if isinstance(value, list):
        return shlex.join(str(v) for v in value)
    return "" if value is None else str(value)


def _describe(field: ConfigField, value: Any) -> str:
    if value is None:
        return "unset"
    return "***" if field.secret else repr(value)


def ask_field(field: ConfigField, current: Any) -> Any:
    """Asks for the value of an option.

    Args:
        field: Option to ask for.
        current: Current value of the option, in its JSON form, used as default answer.

    Returns:
        The answer in its JSON form, or None if the option is unset.

    """
    label = f"  {field.key}"
    if field.annotation is bool:
        return typer.confirm(label, default=bool(current))

    if field.choices:
        options = field.choices + ([UNSET] if field.nullable and UNSET not in field.choices else [])
        default = UNSET if current is None else str(current)
        answer = prompt_choice(label, options, default=default)
        return None if answer == UNSET else answer

    while True:
        if field.secret:
            state = "set" if current else "unset"
            text = typer.prompt(
                f"{label} (currently {state}, leave empty to keep it)", default="", hide_input=True, show_default=False
            )
            raw = text if text else _show(current)
        else:
            raw = typer.prompt(label, default=_show(current), show_default=current is not None)
        raw = raw.strip()
        if not raw or raw.lower() == UNSET:
            if field.nullable:
                return None
            console.print(f"  [red]{field.key} cannot be unset[/]")
            continue
        if get_origin(field.annotation) is list:
            return shlex.split(raw)
        if field.annotation is int:
            try:
                return int(raw)
            except ValueError:
                console.print(f"  [red]{escape(raw)} is not an integer[/]")
                continue
        return raw


def config_command(settings: Settings, section: str | None, file: Path | None, advanced: bool) -> None:
    """Asks interactively for the options of the configuration and writes the answers to a bmde.toml file.

    Only the options that change are written, so the rest keep being inherited from the other configuration sources.

    Args:
        settings: Current settings, which values are shown as default answers.
        section: Only ask for the options of this section (e.g. run or git.vpn). If None, ask for every section.
        file: File where the configuration is written. If None, the user chooses between the repo and user config.
        advanced: Also ask for the advanced options.

    """
    prefix = section_prefix(section)

    target = resolve_target(file)
    stored: dict[str, Any] = dict(read_toml(target))
    current = settings.model_dump(mode="json")
    defaults = Settings().model_dump(mode="json")

    console.print(
        f"\nConfiguring {escape(section or 'bmde')}. The current value of each option is shown between brackets: "
        f"press enter to keep it or type '{UNSET}' to unset an optional value.\n"
    )
    changes: list[tuple[ConfigField, Any, Any]] = []
    skipped_top: set[str] = set()
    for path, model, leaves in iter_sections(Settings):
        if path[: len(prefix)] != prefix:
            continue
        fields = [field for field in leaves if advanced or not field.advanced]
        # When configuring everything, let the user skip whole commands
        if not prefix and len(path) == 1:
            doc = f" ({escape(model.__doc__.strip())})" if model.__doc__ else ""
            if not typer.confirm(f"Configure [{path[0]}]{doc}?", default=True):
                skipped_top.add(path[0])
                continue
        if not fields or path[0] in skipped_top:
            continue

        doc = escape(model.__doc__.strip()) if model.__doc__ else ""
        console.print(f"\n[bold cyan]{escape('[' + '.'.join(path) + ']')}[/] {doc}")
        for field in fields:
            shown = get_value(current, field.path)
            # Runtime-computed defaults (e.g. the timestamped log file) are not meant to be frozen into a file
            if field.dynamic_default and shown == get_value(defaults, field.path):
                shown = None
            hint = f"  [dim]{escape(field.description)}"
            if field.dynamic_default:
                hint += f" (default: {escape(field.dynamic_default)})"
            console.print(hint + "[/]")
            answer = ask_field(field, shown)
            if answer == shown and not has_value(stored, field.path):
                continue
            previous = get_value(stored, field.path) if has_value(stored, field.path) else shown
            if answer != previous:
                changes.append((field, previous, answer))
            set_value(stored, field.path, answer)

    if not changes:
        console.print("\nNothing changed.")
        return
    _save_changes(target, stored, changes)


def _save_changes(target: Path, stored: dict[str, Any], changes: list[tuple[ConfigField, Any, Any]]) -> None:
    """Validates the configuration, shows the changes and writes them to target if the user confirms."""
    try:
        Settings.model_validate(stored)
    except ValidationError as exc:
        console.print(f"[red]The resulting configuration is not valid:[/]\n{escape(str(exc))}")
        raise typer.Exit(code=1) from exc

    console.print(f"\nChanges to {escape(str(target))}:")
    for field, old, new in changes:
        console.print(f"  {escape(field.dotted)}: {escape(_describe(field, old))} -> {escape(_describe(field, new))}")
    if target.is_file() and any(line.lstrip().startswith("#") for line in target.read_text().splitlines()):
        console.print("[yellow]The comments of the file will be lost when it is rewritten.[/]")
    if not typer.confirm("Save?", default=True):
        console.print("Discarded.")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rtoml.dumps(stored))
    log.debug(f"Configuration written to {target}")
    console.print(f"Configuration saved to {escape(str(target))}")


def value_origin(
    path: tuple[str, ...], sources: Sequence[ConfigSource], cli_overrides: Collection[tuple[str, ...]]
) -> str:
    """Describes the source that supplied the value of an option: the one with the highest priority that sets it."""
    if path in cli_overrides:
        return "command line"
    for source in reversed(sources):
        if has_value(source.data, path):
            if source.name == "environment":
                return f"environment: {ENV_PREFIX}{'__'.join(path).upper()}"
            return f"{source.name}: {source.location}"
    return "default"


def show_sources_command(
    settings: Settings,
    sources: Sequence[ConfigSource],
    cli_overrides: Collection[tuple[str, ...]],
    section: str | None,
) -> None:
    """Prints the sources of configuration and the value of each option with the source that supplied it.

    The sources are listed from lowest to highest priority.

    Args:
        settings: Current settings.
        sources: Sources the settings were loaded from, from lowest to highest priority.
        cli_overrides: Options set by command line flags.
        section: Only show the options of this section (e.g. run or git.vpn). If None, show every option.

    """
    prefix = section_prefix(section)
    console.print("Configuration sources, from lowest to highest priority:")
    for source in sources:
        state = "[green]found[/]" if source.found else "[dim]not found[/]"
        console.print(f"  [bold]{escape(source.name)}[/] {escape(source.location)} ({state})")
    console.print("  [bold]command line[/] flags")

    current = settings.model_dump(mode="json")
    console.print("\nValues:")
    for path, _, leaves in iter_sections(Settings):
        if path[: len(prefix)] != prefix:
            continue
        for field in leaves:
            value = _describe(field, get_value(current, field.path))
            origin = value_origin(field.path, sources, cli_overrides)
            console.print(f"  {escape(field.dotted)} = {escape(value)} [dim]({escape(origin)})[/]")
