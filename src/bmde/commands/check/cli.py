import typer

from bmde.commands.check.command import check_command
from bmde.config.schema import Settings


def check_controller(ctx: typer.Context) -> None:
    """Check availability of backends for all services."""
    settings: Settings = ctx.obj["settings"]
    check_command(settings)
