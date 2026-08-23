"""
Test cases where the configuration file:

    1. Exists AND
    2. Is formatted properly AND
    3. Contains a single LLM provider
"""

import shutil
from pathlib import Path

import pytest

from how_tui.config import ConfigManager
from how_tui.providers import PROVIDERS, GeminiProvider, GroqProvider


@pytest.fixture
def standard_config(tmp_path):
    source = Path(__file__).parent / "data" / "config_standard.json"
    config_file = tmp_path / "config.json"

    shutil.copy(source, config_file)

    return ConfigManager(PROVIDERS, config_file)


def test_get_all_supported_providers(standard_config):

    providers = standard_config.get_all_supported_providers()

    expected = ["Gemini", "Groq"]

    assert providers == expected


def test_get_all_configured_providers(standard_config):

    providers = standard_config.get_all_configured_providers()

    expected = ["Gemini"]

    assert providers == expected


def test_provider_is_configured(standard_config):

    assert standard_config.provider_is_configured("Gemini") is True
    assert standard_config.provider_is_configured("Groq") is False


def test_provider_is_supported(standard_config):

    assert standard_config.provider_is_supported("Gemini") is True
    assert standard_config.provider_is_supported("Groq") is True
    assert standard_config.provider_is_supported("FakeProvider") is False


def test_get_provider_by_name(standard_config):

    assert standard_config.get_provider_by_name("Gemini") is GeminiProvider
    assert standard_config.get_provider_by_name("Groq") is GroqProvider
    assert standard_config.get_provider_by_name("FakeProvider") is None


def test_any_providers_configured(standard_config):

    assert standard_config.any_providers_configured() is True


def test_get_default_provider_class(standard_config):

    provider_class = standard_config.get_default_provider_class()

    assert provider_class is GeminiProvider


def test_get_default_provider_model(standard_config):

    model = standard_config.get_default_provider_model()

    expected = "models/gemini-flash-lite-latest"

    assert model == expected


def test_set_default_provider(standard_config):

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile")
    standard_config.set_default_provider("Groq")

    assert standard_config.config.default_provider == "Groq"


def test_set_default_provider_ignores_unsupported_name(standard_config):

    standard_config.set_default_provider("FakeProvider")

    assert standard_config.config.default_provider == "Gemini"


def test_set_default_provider_ignores_unconfigured_provider(standard_config):

    standard_config.set_default_provider("Groq")

    assert standard_config.config.default_provider == "Gemini"


def test_add_provider(standard_config):

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile")

    assert standard_config.provider_is_configured("Groq") is True
    assert standard_config.config.default_provider == "Gemini"


def test_add_provider_as_default(standard_config):

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile", default=True)

    assert standard_config.provider_is_configured("Groq") is True
    assert standard_config.config.default_provider == "Groq"


def test_add_provider_persists_to_disk(standard_config):

    config_file = standard_config.config_file

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile", default=True)

    reloaded = ConfigManager(PROVIDERS, config_file)

    assert reloaded.provider_is_configured("Groq") is True
    assert reloaded.config.default_provider == "Groq"


def test_remove_non_default_provider(standard_config):

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile")
    standard_config.remove_provider("Groq")

    assert standard_config.provider_is_configured("Groq") is False
    assert standard_config.config.default_provider == "Gemini"


def test_remove_default_provider_promotes_new_default(standard_config):

    standard_config.add_provider("Groq", "llama-3.3-70b-versatile")
    standard_config.remove_provider("Gemini")

    assert standard_config.provider_is_configured("Gemini") is False
    assert standard_config.config.default_provider == "Groq"


def test_remove_last_provider_clears_default(standard_config):

    standard_config.remove_provider("Gemini")

    assert standard_config.get_all_configured_providers() == []
    assert standard_config.config.default_provider is None


def test_remove_provider_persists_to_disk(standard_config):

    config_file = standard_config.config_file

    standard_config.remove_provider("Gemini")

    reloaded = ConfigManager(PROVIDERS, config_file)

    assert reloaded.get_all_configured_providers() == []
    assert reloaded.config.default_provider is None
