from importlib.metadata import version

from typer.testing import CliRunner

from bmde.cli import app

runner = CliRunner()


def test_version_prints_the_installed_version_and_exits():
    for flag in ("--version", "-V"):
        result = runner.invoke(app, [flag])
        assert result.exit_code == 0
        assert result.output == f"bmde {version('bmde')}\n"
