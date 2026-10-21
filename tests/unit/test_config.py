import os
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from bmde.cli import app
from bmde.config.fields import iter_sections
from bmde.config.schema import Settings
from bmde.config.show_config import get_default_config

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run in an empty directory with an empty HOME so no bmde.toml of the machine is loaded."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    for name in list(os.environ):
        if name.startswith("BMDE_"):
            monkeypatch.delenv(name)


def test_default_config_is_valid_and_has_the_defaults():
    """The generated template parses into the default settings."""
    data = tomllib.loads(get_default_config())
    assert Settings.model_validate(data).model_dump() == Settings().model_dump()


def test_default_config_documents_every_option():
    text = get_default_config()
    for _, _, leaves in iter_sections(Settings):
        for field in leaves:
            assert field.description, f"{field.dotted} has no description"
            assert field.description.split()[0] in text


def test_example_config_is_up_to_date():
    example = Path(__file__).resolve().parents[2] / "examples" / "bmde.toml"
    assert example.read_text() == get_default_config(), "Run 'make fmt' to regenerate examples/bmde.toml"


def test_config_writes_only_changed_options(tmp_path: Path):
    target = tmp_path / "bmde.toml"
    # graphical_output, debug, arm9_debug_port, fat_image, sound, controls, backend, save
    answers = "vnc\n\n2000\n\n\n\ndocker\ny\n"
    result = runner.invoke(app, ["config", "run", "-f", str(target)], input=answers)
    assert result.exit_code == 0, result.output
    assert tomllib.loads(target.read_text()) == {
        "run": {"graphical_output": "vnc", "arm9_debug_port": 2000, "execution_settings": {"backend": "docker"}}
    }


def test_config_shows_current_values_and_unsets(tmp_path: Path):
    target = tmp_path / "bmde.toml"
    target.write_text('[git.git]\nname = "Ada"\nemail = "ada@example.com"\n')
    # name (keep), email (unset), save
    result = runner.invoke(app, ["config", "git.git", "-f", str(target)], input="\nunset\ny\n")
    assert result.exit_code == 0, result.output
    assert "[Ada]" in result.output
    assert tomllib.loads(target.read_text()) == {"git": {"git": {"name": "Ada"}}}


def test_config_rejects_unknown_section(tmp_path: Path):
    result = runner.invoke(app, ["config", "nope", "-f", str(tmp_path / "bmde.toml")])
    assert result.exit_code != 0
