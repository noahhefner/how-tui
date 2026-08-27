import logging
from pathlib import Path

from platformdirs import PlatformDirs
from pydantic import ValidationError

from how_tui.models.config_file import ConfigFile, ProviderConfig
from how_tui.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised when an invalid state in the config file is detected."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConfigManager:
    def __init__(
        self,
        provider_index: dict[str, type[LLMProvider]],
        config_file_path: Path | None = None,
    ):
        """Create a new config manager object.

        This init function checks for an existing configuration file and loads
        the data from it if one is found.

        Raises:
            ConfigError: If there is no config file, or if the config file is
                malformed.
        """

        self.provider_index = provider_index

        config_file: Path | None = None
        if config_file_path is not None:
            # User-specified config file
            if not config_file_path.exists():
                raise ConfigError("User-provided config file does not exist.")
            if not config_file_path.is_file():
                raise ConfigError("User-provided config file is not a file.")
            config_file = config_file_path
        else:
            # Default config file
            config_dir = PlatformDirs("how-tui", "NoahHefner").user_config_path
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"
            if not config_file.exists():
                logger.debug("Config file does not exist.")
                raise ConfigError("Config file does not exist.")
            if not config_file.is_file():
                raise ConfigError("Config file is not a file.")
        assert config_file is not None

        # Load the config file
        try:
            self.config = ConfigFile.model_validate_json(config_file.read_text())
        except ValidationError as e:
            raise ConfigError(
                f"Validation error occurred while reading config file: {e}"
            )

        # Save reference to config file
        self.config_file = config_file

    def add_provider(
        self,
        provider_name: str,
        model: str,
        default: bool = False,
    ) -> None:
        """Write LLM provider data to config file."""

        provider_config = ProviderConfig(
            model=model,
        )

        # Update internal state
        self.config.providers[provider_name] = provider_config

        # Set as default, if neccessary
        if default or self.config.default_provider is None:
            logger.debug(f"Setting {provider_name} as default...")
            self.config.default_provider = provider_name

        # Write in-memory config data to disk
        self._write_config()

    def remove_provider(
        self,
        provider_name: str,
    ) -> None:
        """Remove an LLM provider from the config file."""

        # Remove provider from in-memory config
        del self.config.providers[provider_name]

        # If another provider is configured as the default, we do not need to set
        # a new default. Write out new config to disk and return.
        if self.config.default_provider != provider_name:
            self._write_config()
            return

        # Set a new default provider if another one is available. Otherwise, clear
        # the default and send a warning message.
        if len(self.config.providers) > 0:
            new_default = next(iter(self.config.providers))
            logger.debug(f"Setting {new_default} as default provider...")
            self.config.default_provider = new_default
        else:
            self.config.default_provider = None

        # Write config to disk
        self._write_config()

    def set_default_provider(
        self,
        provider_name: str,
    ) -> None:
        """Set a provider as the default."""

        if not provider_name in self.provider_index:
            logger.debug("Invalid provider name.")
            return

        if not provider_name in self.config.providers:
            logger.debug("Provider not configured.")
            return

        # Update internal state
        self.config.default_provider = provider_name

        # Write to disk
        self._write_config()

    def get_all_configured_providers(self) -> list[str]:
        """Lists all configured providers by name."""

        return list(self.config.providers.keys())

    def get_all_supported_providers(self) -> list[str]:
        """Lists all supported providers by name."""

        return list(self.provider_index.keys())

    def provider_is_configured(self, provider_name: str) -> bool:
        """True if a provider is configured, False otherwise."""

        return provider_name in self.config.providers

    def provider_is_supported(self, provider_name: str) -> bool:
        """True if a provider is supported, False otherwise."""

        return provider_name in self.provider_index

    def get_provider_by_name(self, provider_name: str) -> type[LLMProvider] | None:
        """Get provider class by name.

        Assumptions:
            - The provider is supported and the provider is configured. Exits otherwise.
        """

        if provider_name in self.provider_index:
            return self.provider_index[provider_name]
        return None

    def any_providers_configured(self) -> bool:
        """Returns True if at least one provider is configured. False otherwise."""

        return (
            self.config.default_provider is not None and len(self.config.providers) > 0
        )

    def get_default_provider_class(self) -> type[LLMProvider] | None:
        """Get the default provider class.

        Raises:
            ConfigError: If the default provider does not match any configured
                provider name.
        """

        if self.config.default_provider is None:
            return None

        default_provider_class = self.provider_index[self.config.default_provider]
        if default_provider_class is None:
            raise ConfigError(
                "Default provider does not match any configured provider name."
            )

        return default_provider_class

    def get_default_provider_model(self) -> str | None:
        """Get the model for the default provider.

        Raises:
            ConfigError: If the default provider does not match any configured
                provider name.
        """

        if self.config.default_provider is None:
            return None

        default_provider = self.config.providers[self.config.default_provider]
        if default_provider is None:
            raise ConfigError(
                "Default provider does not match any configured provider name."
            )

        return default_provider.model

    def _write_config(self):
        """Write in-memory config to config file on disk."""

        self.config_file.write_text(self.config.model_dump_json(indent=2))
