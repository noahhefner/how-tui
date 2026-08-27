"""
Test cases where the configuration file is malformed.
"""

import shutil
from pathlib import Path

import pytest

from how_tui.config import ConfigError, ConfigManager
from how_tui.providers import PROVIDERS


@pytest.fixture
def malformed_config_1_path(tmp_path):
    source = Path(__file__).parent / "data" / "config_malformed_1.json"
    config_file = tmp_path / "config.json"

    shutil.copy(source, config_file)

    return config_file


@pytest.fixture
def malformed_config_2_path(tmp_path):
    source = Path(__file__).parent / "data" / "config_malformed_2.json"
    config_file = tmp_path / "config.json"

    shutil.copy(source, config_file)

    return config_file


@pytest.fixture
def malformed_config_3_path(tmp_path):
    source = Path(__file__).parent / "data" / "config_malformed_3.json"
    config_file = tmp_path / "config.json"

    shutil.copy(source, config_file)

    return config_file


def test_missing_providers_raises_config_error(malformed_config_1_path):

    with pytest.raises(ConfigError) as excinfo:
        ConfigManager(PROVIDERS, malformed_config_1_path)

    assert "providers" in str(excinfo.value)


def test_missing_default_provider_raises_config_error(malformed_config_2_path):

    with pytest.raises(ConfigError) as excinfo:
        ConfigManager(PROVIDERS, malformed_config_2_path)

    assert "default_provider" in str(excinfo.value)


def test_invalid_json_raises_config_error(malformed_config_3_path):

    with pytest.raises(ConfigError) as excinfo:
        ConfigManager(PROVIDERS, malformed_config_3_path)

    assert "Validation error occurred" in str(excinfo.value)
