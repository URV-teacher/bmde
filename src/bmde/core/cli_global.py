import typer

from bmde.config.loader import config_sources, merge_sources
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.logging import (
    configure_logging_from_settings,
    process_log_flags,
)
from bmde.core.shared_options import (
    ConfigOpt,
    LogFileOpt,
    QuietOpt,
    ShowConfigOpt,
    ShowDefaultConfigOpt,
    VerboseOpt,
    VersionOpt,
    VeryQuietOpt,
    VeryVerboseOpt,
)

log = logging.get_logger(__name__)


def cli_global_callback(
    ctx: typer.Context,
    config: ConfigOpt = None,
    verbose: VerboseOpt = False,
    very_verbose: VeryVerboseOpt = False,
    quiet: QuietOpt = False,
    very_quiet: VeryQuietOpt = False,
    log_file: LogFileOpt = None,
    show_config: ShowConfigOpt = False,
    show_default_config: ShowDefaultConfigOpt = False,
    version: VersionOpt = False,
) -> None:
    """
    Global option callback. Executed if no command is provided.
    """

    cli_log_level, more_than_one_flag = process_log_flags(
        very_verbose=very_verbose, verbose=verbose, quiet=quiet, very_quiet=very_quiet
    )

    if more_than_one_flag:
        log.warning("More than one log level arguments was provided, the log level with more verbosity will be used.")
    # Load settings
    sources = config_sources(explicit_config=config)
    settings = Settings.model_validate(merge_sources(sources))

    # CLI overrides, remembered so bmde config --show-sources can tell where each value comes from
    cli_overrides: set[tuple[str, ...]] = set()
    if cli_log_level:
        settings.logging.level = cli_log_level
        cli_overrides.add(("logging", "level"))
    if log_file:
        settings.logging.file = log_file
        cli_overrides.add(("logging", "file"))

    configure_logging_from_settings(settings=settings)

    # Load settings into global context
    ctx.obj = {"settings": settings, "sources": sources, "cli_overrides": cli_overrides}
    log.debug("Ended global callback")
