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


def test_loading_does_not_log_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    # Logged before the SecretsFilter knows the credentials, e.g. under the logging of a program using bmde.api
    caplog.set_level(1)
    config = tmp_path / "home" / ".config" / "bmde" / "bmde.toml"
    config.parent.mkdir(parents=True)
    config.write_text('[git.ssh]\npassword = "file-secret"\n')  # pragma: allowlist secret
    monkeypatch.setenv("BMDE_GIT__VPN__PASSWORD", "env-secret")
    load_settings()
    assert "git.ssh.password" in caplog.text
    assert "file-secret" not in caplog.text
    assert "env-secret" not in caplog.text


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


def test_config_asks_where_to_save(tmp_path: Path, repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(command.console, "width", 1000)
    # target (wrong answer, then user), image_tag, save
    result = runner.invoke(app, ["config", "docker"], input="nowhere\nuser\nsha-0123abc\ny\n")
    assert result.exit_code == 0, result.output
    assert "nowhere is not one of repo, user" in result.output
    # The tag computed at runtime is offered as unset, not frozen into the file
    assert "(default: <version of bmde>)" in result.output
    user_file = tmp_path / "home" / ".config" / "bmde" / "bmde.toml"
    assert tomllib.loads(user_file.read_text()) == {"docker": {"image_tag": "sha-0123abc"}}
    assert not (repo / "bmde.toml").exists()


def test_config_secrets_numbers_and_discarding(tmp_path: Path):
    target = tmp_path / "bmde.toml"
    # enabled, username, password, host, port (wrong, then right), cert, realm, test_dns, test_ip, save
    answers = "\nstudent\nhunter2\n\nabc\n443\n\n\n\n\nn\n"  # pragma: allowlist secret
    result = runner.invoke(app, ["config", "git.vpn", "-f", str(target)], input=answers)
    assert result.exit_code == 0, result.output
    assert "currently unset, leave empty to keep it" in result.output
    assert "abc is not an integer" in result.output
    assert "vpn.password: unset -> ***" in result.output
    assert "hunter2" not in result.output
    assert "Discarded." in result.output
    assert not target.exists()


def test_config_advanced_list_options(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    target = tmp_path / "bmde.toml"
    # entrypoint, arguments, background, dry_run, interactive, backend, save
    result = runner.invoke(app, ["config", "build", "-a", "-f", str(target)], input="\n-j 4\n\n\n\n\ny\n")
    assert result.exit_code == 0, result.output
    assert tomllib.loads(target.read_text()) == {"build": {"execution_settings": {"arguments": ["-j", "4"]}}}

    # The current list is offered as default answer, so keeping it changes nothing
    monkeypatch.setenv("BMDE_BUILD__EXECUTION_SETTINGS__ARGUMENTS", '["-j", "4"]')
    result = runner.invoke(app, ["config", "build", "-a", "-f", str(tmp_path / "other.toml")], input="\n" * 6)
    assert "[-j 4]" in result.output
    assert "Nothing changed." in result.output


def test_config_lets_skip_whole_commands(tmp_path: Path):
    sections = [path for path, _, _ in iter_sections(Settings) if len(path) == 1]
    result = runner.invoke(app, ["config", "-f", str(tmp_path / "bmde.toml")], input="n\n" * len(sections))
    assert result.exit_code == 0, result.output
    assert "Nothing changed." in result.output


def test_config_refuses_to_save_an_invalid_file(tmp_path: Path):
    target = tmp_path / "bmde.toml"
    target.write_text('[run]\narm9_debug_port = "not a port"\n')
    result = runner.invoke(app, ["config", "docker", "-f", str(target)], input="sha-0123abc\n")
    assert result.exit_code == 1
    assert "The resulting configuration is not valid" in result.output
    assert "image_tag" not in target.read_text()


def test_config_warns_that_comments_are_lost(tmp_path: Path):
    target = tmp_path / "bmde.toml"
    target.write_text('# my notes\n[docker]\nimage_tag = "1.14.0"\n')
    result = runner.invoke(app, ["config", "docker", "-f", str(target)], input="1.15.0\ny\n")
    assert result.exit_code == 0, result.output
    assert "The comments of the file will be lost" in result.output
    assert tomllib.loads(target.read_text()) == {"docker": {"image_tag": "1.15.0"}}


def test_show_sources_of_a_section(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(command.console, "width", 1000)
    result = runner.invoke(app, ["config", "--show-sources", "patch"])
    assert result.exit_code == 0, result.output
    assert "patch.execution_settings.backend = unset (default)" in result.output
    assert "run.debug" not in result.output


def test_show_config_flags(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BMDE_RUN__ARM9_DEBUG_PORT", "4242")
    current = runner.invoke(app, ["--show-config"])
    assert current.exit_code == 0
    assert "arm9_debug_port = 4242" in current.output
    default = runner.invoke(app, ["--show-default-config"])
    assert default.output == get_default_config()


def test_unset_options_are_shown_with_a_placeholder():
    from bmde.config.show_config import render_config

    settings = Settings()
    settings.logging.hide_sensibles = None
    assert "# hide_sensibles = <true|false>" in render_config(settings, template=True)


def test_nested_value_helpers():
    from bmde.config.fields import get_value, has_value, set_value, unwrap_optional

    data: dict = {"git": {"vpn": {"port": 443}}, "run": 1}
    assert get_value(data, ("git", "vpn", "port")) == 443
    assert get_value(data, ("run", "debug")) is None
    assert not has_value(data, ("git", "ssh", "host"))
    # Removing the last option of a table removes the empty tables too, and missing paths are ignored
    set_value(data, ("run", "debug", "port"), None)
    set_value(data, ("git", "vpn", "port"), None)
    assert data == {"run": 1}

    annotation, nullable = unwrap_optional(int | str | None)
    assert nullable
    assert set(annotation.__args__) == {int, str}


def test_system_config_outside_posix(monkeypatch: pytest.MonkeyPatch):
    import types

    monkeypatch.undo()  # the autouse fixture replaces system_config_file
    monkeypatch.setattr(loader, "os", types.SimpleNamespace(name="nt", environ={}))
    path = loader.system_config_file()
    assert path.name == "bmde.toml"
    assert path.parent.name == "bmde"
    assert not str(path).startswith("/etc/bmde")


def test_config_asks_again_for_an_option_that_cannot_be_unset(monkeypatch: pytest.MonkeyPatch):
    from pydantic.fields import FieldInfo

    from bmde.config.fields import ConfigField

    answers = iter(["", "unset", "value"])
    monkeypatch.setattr(command.typer, "prompt", lambda *args, **kwargs: next(answers))
    field = ConfigField(path=("section", "name"), info=FieldInfo(description="A name"), annotation=str, nullable=False)

    assert command.ask_field(field, None) == "value"


def test_config_of_everything_asks_section_by_section(tmp_path: Path):
    sections = [path for path, _, _ in iter_sections(Settings) if len(path) == 1]
    # Configure [logging] keeping its 3 options, skip the rest
    answers = "y\n" + "\n" * 3 + "n\n" * (len(sections) - 1)
    result = runner.invoke(app, ["config", "-f", str(tmp_path / "bmde.toml")], input=answers)
    assert result.exit_code == 0, result.output
    assert "[logging]" in result.output
    assert "Nothing changed." in result.output


def test_render_config_without_documentation(monkeypatch: pytest.MonkeyPatch):
    from pydantic import BaseModel

    from bmde.config import show_config

    class Undocumented(BaseModel):
        value: int = 1

    monkeypatch.setattr(show_config, "iter_sections", lambda model: iter_sections(Undocumented, ("section",)))
    # No comment line for the missing docstring nor for the missing description
    assert show_config.render_config(Settings(), template=False) == "[section]\n# value = <int>\n"


def test_user_config_falls_back_to_the_legacy_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    legacy = tmp_path / "home" / ".config" / "bmde" / "bmde.toml"
    write_port(legacy, 7)
    assert loader.user_config_file() == legacy
    assert "where previous versions kept it" in caplog.text
