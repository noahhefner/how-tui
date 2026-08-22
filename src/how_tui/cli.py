import argparse
import logging
import os
import platform
import sys

import questionary
from rich.console import Console

from how_tui.config import ConfigError, ConfigManager
from how_tui.providers import PROVIDERS, LLMProvider

PROMPT_TEMPLATE = """
You are a terminal command assistant.

The user is asking questions that should be answered with 
commands that can be executed in their terminal.

Rules:
- Only generate commands that will run on the users operating system.
- To not invent commands
- Do not assume software is instaled unless it is very commonly used and widely
  available for most operating systems.
- Return several command options when multiple reasonable approaches exist.
- If the operating system is unknown, assume Debian Linux.
- If the shell is unknown, assume Bash.

User request:
{prompt}

User Environment:
Operating System: {operating_system}
Shell: {shell}

Return the appropriate commands.
"""

logger = logging.getLogger(__name__)


def list_supported_providers(configurator: ConfigManager):
    """List all LLM providers that are supported by how-tui."""

    providers = configurator.get_all_supported_providers()
    if len(providers) == 0:
        print("No supported LLM providers.")
        return

    print("Supported LLM providers:")
    for provider_name in providers:
        print(f"  - {provider_name}")


def list_configured_providers(configurator: ConfigManager):
    """List all LLM providers that the user has configured."""

    providers = configurator.get_all_configured_providers()
    if len(providers) == 0:
        print("No LLM providers configured. Run 'how --setup' to configure one.")
        return

    print("Configured LLM providers:")
    for provider_name in providers:
        print(f"  - {provider_name}")


def remove_provider(configurator: ConfigManager):
    """Remove an LLM provider.

    Removes the provider from the configuration file and erases locally stored
    auth credentials.
    """

    provider_names = configurator.get_all_configured_providers()
    if len(provider_names) == 0:
        print("No providers configured. Run 'how --setup' to configure a provider.")
        return

    # Prompt user to select an LLM provider to remove
    selected_name = questionary.select(
        "Select an LLM provider to remove:", choices=provider_names
    ).ask()

    # Get provider class
    provider = configurator.get_provider_by_name(selected_name)
    assert provider is not None

    # Unauthenticate with the LLM provider
    provider.unauthenticate()

    # Remove from the config file
    configurator.remove_provider(selected_name)


def set_default_provider(configurator: ConfigManager):
    """Set a default LLM provider."""

    if not configurator.any_providers_configured():
        print("No providers configured. Run 'how --setup' to configure a provider.")
        return

    provider_names = configurator.get_all_configured_providers()
    assert len(provider_names) != 0

    # Prompt user to select a default provider
    selected_name = questionary.select(
        "Select a default LLM provider:", choices=provider_names
    ).ask()

    # Update config
    configurator.set_default_provider(selected_name)


def add_provider(configurator: ConfigManager):
    """Configure an LLM provider."""

    # List of all supported provider names
    provider_names = configurator.get_all_supported_providers()
    if len(provider_names) == 0:
        print("No supported providers. Tell the developers to add some.")
        return

    # Prompt user to select an LLM provider
    selected_name = questionary.select(
        "Select an LLM provider to configure:", choices=provider_names
    ).ask()

    # Get provider class
    provider = configurator.get_provider_by_name(selected_name)
    assert provider is not None

    # Authenticate with the LLM provider
    provider.authenticate()

    # Select a model from the provider
    models = provider.get_models()
    selected_model = questionary.select("Select a model:", choices=models).ask()

    # Write provider to config file
    configurator.add_provider(selected_name, selected_model)


def print_commands(commands: list[str]):
    """Display the commands reccommended by the AI."""

    print("Command suggestions:")
    for command in commands:
        print(f"  - {command}")


def main():

    console = Console()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--list-supported-providers",
        action="store_true",
        help="List all supported LLM providers",
    )

    parser.add_argument(
        "--list-configured-providers",
        action="store_true",
        help="List your configured LLM providers",
    )

    parser.add_argument(
        "--add-provider",
        action="store_true",
        help="Setup an LLM provider",
    )

    parser.add_argument(
        "--remove-provider",
        action="store_true",
        help="Remove an LLM provider",
    )

    parser.add_argument(
        "--set-default-provider",
        action="store_true",
        help="Set a default LLM provider",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug level logging",
    )

    parser.add_argument(
        "--provider",
        help="Specify which LLM provider to use",
    )

    parser.add_argument(
        "--model",
        help="Specify which model to use",
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question for the LLM",
    )

    args = parser.parse_args()

    # Configure log level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.basicConfig(level=logging.INFO)

    # Get environment information
    operating_system = platform.system()
    shell = os.environ.get("SHELL", "unknown")
    logger.debug(f"Detected operating system: {operating_system}")
    logger.debug(f"Detected shell: {shell}")

    # Create config manager
    try:
        configurator = ConfigManager(PROVIDERS)
    except ConfigError as e:
        logger.debug(e)
        console.print(
            "[red]An error occurred while reading the config file. Run how with the --debug flag for more info.[/red]"
        )
        sys.exit(1)

    # List all supported LLM providers
    if args.list_supported_providers:
        list_supported_providers(configurator)
        return

    # List users configured LLM providers
    if args.list_configured_providers:
        list_configured_providers(configurator)
        return

    # Remove a configured LLM provider
    if args.remove_provider:
        remove_provider(configurator)
        return

    # Set a default provider
    if args.set_default_provider:
        set_default_provider(configurator)
        return

    # Add an LLM provider
    if args.add_provider:
        add_provider(configurator)
        return

    # No prompt
    if args.prompt is None or args.prompt.strip() == "":
        parser.print_help()
        return

    # Check that at least one provider is configured
    if not configurator.any_providers_configured():
        print("No LLM providers configured. Run 'how --setup' to configure one.")
        return

    # Get provider
    provider: type[LLMProvider] | None = None
    user_specified_provider = args.provider
    if user_specified_provider is not None:
        if not configurator.provider_is_supported(user_specified_provider):
            print("Provider not supported.")
            sys.exit(1)
        if not configurator.provider_is_configured(user_specified_provider):
            print("Provider not configured.")
            sys.exit(1)
        provider = configurator.get_provider_by_name(user_specified_provider)
    else:
        try:
            provider = configurator.get_default_provider_class()
        except ConfigError as e:
            logger.debug(e)
            console.print(
                "[red]An error occurred while selecting the LLM provider. Run how with the --debug flag for more info.[/red]"
            )
            sys.exit(1)

    assert provider is not None
    logger.debug(f"Using provider class: {provider.__name__}")

    # Authenticate with the LLM provider
    provider.authenticate()

    # Get model
    model: str | None = None
    user_specified_model = args.model
    if user_specified_model is not None:
        model = user_specified_model
    else:
        try:
            model = configurator.get_default_provider_model()
        except ConfigError as e:
            logger.debug(e)
            console.print(
                "[red]An error occurred while selecting a model. Run how with the --debug flag for more info.[/red]"
            )
            sys.exit(1)
    assert model is not None
    logger.debug(f"Using model: {model}")

    # Construct full prompt
    prompt_with_context = PROMPT_TEMPLATE.format(
        operating_system=operating_system,
        shell=shell,
        prompt=args.prompt,
    )

    # Get commands from the AI
    try:
        with console.status("[bold green]Working...[/bold green]", spinner="dots"):
            response = provider.generate_commands(prompt_with_context, model)
    except Exception:  # noqa: BLE001
        console.print("[red]An error occurred while generating commands.[/red]")
        sys.exit(1)

    # Print commands to the console
    commands = [c.command for c in response.commands]
    print_commands(commands)
