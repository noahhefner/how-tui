"""
Test cases where the configuration file does not exist.
"""

import pytest

from how_tui.config import ConfigError, ConfigManager
from how_tui.providers import PROVIDERS


@pytest.fixture
def default_config_path(tmp_path, monkeypatch):
    class FakeConfigDir:
        def __init__(self, *args, **kwargs):
            pass

        @property
        def user_config_path(self):
            return tmp_path

    monkeypatch.setattr("how_tui.config.PlatformDirs", FakeConfigDir)

    return tmp_path / "config.json"


def test_user_provided_config_missing_raises_error(tmp_path):

    config_file = tmp_path / "does_not_exist.json"

    with pytest.raises(ConfigError):
        ConfigManager(PROVIDERS, config_file)


def test_default_config_missing_raises_error(default_config_path):

    with pytest.raises(ConfigError):
        ConfigManager(PROVIDERS)


def test_default_config_missing_error_message(default_config_path):

    with pytest.raises(ConfigError, match="Config file does not exist."):
        ConfigManager(PROVIDERS)


def test_no_config_file_created_when_missing(default_config_path):

    with pytest.raises(ConfigError):
        ConfigManager(PROVIDERS)

    assert default_config_path.exists() is False
