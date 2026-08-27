"""
Test cases where the configuration file:

    1. Exists AND
    2. Is completely empty
"""

import pytest

from how_tui.config import ConfigError, ConfigManager
from how_tui.providers import PROVIDERS


@pytest.fixture
def empty_config_path(tmp_path):
    config_file = tmp_path / "config.json"

    config_file.write_text("")

    return config_file


@pytest.fixture
def whitespace_only_config_path(tmp_path):
    config_file = tmp_path / "config.json"

    config_file.write_text("\n\n\t  ")

    return config_file


def test_empty_config_file_raises_config_error(empty_config_path):

    with pytest.raises(ConfigError):
        ConfigManager(PROVIDERS, empty_config_path)


def test_empty_config_file_validation_error(empty_config_path):

    with pytest.raises(ConfigError) as excinfo:
        ConfigManager(PROVIDERS, empty_config_path)

    assert "Validation error occurred" in str(excinfo.value)


def test_whitespace_only_config_file_raises_config_error(whitespace_only_config_path):

    with pytest.raises(ConfigError):
        ConfigManager(PROVIDERS, whitespace_only_config_path)
