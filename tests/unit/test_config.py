import os
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from bmde.cli import app
from bmde.commands.config import command
from bmde.config import loader
from bmde.config.fields import iter_sections
from bmde.config.loader import load_settings
from bmde.config.schema import Settings
from bmde.config.show_config import get_default_config
from bmde.core.paths import find_upwards

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run in an empty directory with an empty HOME so no bmde.toml of the machine is loaded."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(loader, "system_config_file", lambda: tmp_path / "etc" / "bmde.toml")
    for name in list(os.environ):
        if name.startswith("BMDE_"):
            monkeypatch.delenv(name)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A git repository inside HOME, as the current directory."""
    path = tmp_path / "home" / "repo"
    (path / ".git").mkdir(parents=True)
    monkeypatch.chdir(path)
    return path


def write_port(path: Path, port: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"[run]\narm9_debug_port = {port}\n")


def test_sources_priority(tmp_path: Path, repo: Path, monkeypatch: pytest.MonkeyPatch):
    system = tmp_path / "etc" / "bmde.toml"
    system.parent.mkdir()
    system.write_text('[run.execution_settings]\nbackend = "docker"\n')

    write_port(tmp_path / "home" / ".config" / "bmde" / "bmde.toml", 2)
    assert load_settings().run.arm9_debug_port == 2
    write_port(repo / "bmde.toml", 3)
    assert load_settings().run.arm9_debug_port == 3
    monkeypatch.setenv("BMDE_RUN__ARM9_DEBUG_PORT", "4")
    assert load_settings().run.arm9_debug_port == 4
    write_port(tmp_path / "explicit.toml", 5)
    settings = load_settings(explicit_config=tmp_path / "explicit.toml")
    assert settings.run.arm9_debug_port == 5
    # Merged key by key: the higher sources do not erase the rest of the [run] table of the system file
    assert settings.run.execution_settings.backend is not None
    assert settings.run.execution_settings.backend.value == "docker"


def test_user_config_honours_xdg_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    write_port(tmp_path / "xdg" / "bmde" / "bmde.toml", 2)
    assert load_settings().run.arm9_debug_port == 2


def test_nested_env_vars(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BMDE_RUN__DEBUG", "true")
    monkeypatch.setenv("BMDE_RUN__EXECUTION_SETTINGS__ARGUMENTS", '["-a", "b c"]')
    settings = load_settings()
    assert settings.run.debug is True
    assert settings.run.execution_settings.arguments == ["-a", "b c"]


def test_legacy_env_vars_are_reported(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    monkeypatch.setenv("BMDE_RUN_DEBUG", "true")
    # Not a section of the settings, e.g. the install directory of the host components
    monkeypatch.setenv("BMDE_ROOT", "/opt/bmde")
    assert load_settings().run.debug is False
    assert "BMDE_RUN__DEBUG" in caplog.text
    assert "BMDE_ROOT" not in caplog.text


def test_project_config_search_stops_at_git_root(repo: Path):
    (repo.parent / "bmde.toml").touch()
    (repo / "src").mkdir()
    assert find_upwards("bmde.toml", start=repo / "src") is None
    (repo / "bmde.toml").touch()
    assert find_upwards("bmde.toml", start=repo / "src") == repo / "bmde.toml"


def test_project_config_search_skips_home(tmp_path: Path):
    """A stray ~/bmde.toml is not the project config of every directory below HOME."""
    (tmp_path / "home" / "projects" / "comp").mkdir(parents=True)
    (tmp_path / "home" / "bmde.toml").touch()
    assert find_upwards("bmde.toml", start=tmp_path / "home" / "projects" / "comp") is None


def test_show_sources(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(command.console, "width", 1000)
    write_port(repo / "bmde.toml", 3)
    monkeypatch.setenv("BMDE_GIT__VPN__PASSWORD", "hunter2")  # pragma: allowlist secret
    result = runner.invoke(app, ["-v", "config", "--show-sources"])
    assert result.exit_code == 0, result.output
    assert f"project {repo / 'bmde.toml'} (found)" in result.output
    assert f"run.arm9_debug_port = 3 (project: {repo / 'bmde.toml'})" in result.output
    assert "git.vpn.password = *** (environment: BMDE_GIT__VPN__PASSWORD)" in result.output
    assert "hunter2" not in result.output
    assert "logging.level = 'debug' (command line)" in result.output
    assert "run.debug = False (default)" in result.output
    # The log file of the execution goes to the log directory of the user, not to the project
    assert not (repo / "logs").exists()


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


def test_config_shows_current_values_and_unsets(repo: Path):
    target = repo / "bmde.toml"
    target.write_text('[git.git]\nname = "Ada"\nemail = "ada@example.com"\n')
    # name (keep), email (unset), save
    result = runner.invoke(app, ["config", "git.git", "-f", str(target)], input="\nunset\ny\n")
    assert result.exit_code == 0, result.output
    assert "[Ada]" in result.output
    assert tomllib.loads(target.read_text()) == {"git": {"git": {"name": "Ada"}}}


def test_config_rejects_unknown_section(tmp_path: Path):
    result = runner.invoke(app, ["config", "nope", "-f", str(tmp_path / "bmde.toml")])
    assert result.exit_code != 0
