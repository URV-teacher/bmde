"""Introspection of the settings schema.

Walks the pydantic models of the settings to obtain each configurable option with its metadata, so the documented TOML
template and the interactive ``bmde config`` command are always in sync with the schema.
"""

from __future__ import annotations

import types
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo


@dataclass(frozen=True)
class ConfigField:
    """A leaf option of the settings, e.g. ``run.execution_settings.backend``."""

    path: tuple[str, ...]
    info: FieldInfo
    # Annotation without the ``| None``
    annotation: Any
    nullable: bool

    @property
    def key(self) -> str:
        return self.path[-1]

    @property
    def dotted(self) -> str:
        return ".".join(self.path)

    @property
    def description(self) -> str:
        return self.info.description or ""

    def _extra(self, name: str) -> Any:
        extra = self.info.json_schema_extra
        return extra.get(name) if isinstance(extra, dict) else None

    @property
    def advanced(self) -> bool:
        return bool(self._extra("advanced"))

    @property
    def secret(self) -> bool:
        return bool(self._extra("secret"))

    @property
    def dynamic_default(self) -> str | None:
        """Placeholder of a default that is computed at runtime, so it cannot be written in a static template."""
        value = self._extra("dynamic_default")
        return str(value) if value is not None else None

    @property
    def choices(self) -> list[str] | None:
        if isinstance(self.annotation, type) and issubclass(self.annotation, Enum):
            return [str(member.value) for member in self.annotation]
        return None


def unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    """Returns the annotation without ``None`` and whether ``None`` was part of it."""
    if get_origin(annotation) in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        nullable = len(args) != len(get_args(annotation))
        if len(args) == 1:
            return args[0], nullable
        return Union[tuple(args)], nullable  # noqa: UP007
    return annotation, False


def is_model(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def iter_sections(
    model: type[BaseModel], path: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], type[BaseModel], list[ConfigField]]]:
    """Yields every model of the settings tree in TOML order: first the leaf options of a model and then its sub-models.

    Args:
        model: Model to walk.
        path: Path of the model inside the settings tree.

    Yields:
        The path of the model, the model and its leaf options.

    """
    leaves: list[ConfigField] = []
    children: list[tuple[str, type[BaseModel]]] = []
    for name, info in model.model_fields.items():
        inner, nullable = unwrap_optional(info.annotation)
        if is_model(inner):
            children.append((name, inner))
        else:
            leaves.append(ConfigField(path=(*path, name), info=info, annotation=inner, nullable=nullable))
    yield path, model, leaves
    for name, child in children:
        yield from iter_sections(child, (*path, name))


def get_value(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    """Returns the value of a nested dict at ``path`` or ``None`` if it is missing."""
    current: Any = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def has_value(data: dict[str, Any], path: tuple[str, ...]) -> bool:
    current: Any = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def set_value(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    """Sets ``value`` at ``path`` of a nested dict, removing the key (and empty parents) if ``value`` is ``None``."""
    if value is None:
        _remove_value(data, path)
        return
    current = data
    for part in path[:-1]:
        current = current.setdefault(part, {})
    current[path[-1]] = value


def _remove_value(data: dict[str, Any], path: tuple[str, ...]) -> None:
    parent = data
    for part in path[:-1]:
        if not isinstance(parent.get(part), dict):
            return
        parent = parent[part]
    parent.pop(path[-1], None)
    if len(path) > 1 and not parent:
        _remove_value(data, path[:-1])
