# how-tui

A terminal command assistant that uses LLMs to generate shell commands from natural language questions. Ask it how to do something and it will suggest commands for your specific OS and shell.

## Features

- Ask natural-language questions and get relevant terminal command suggestions
- OS and shell aware — generates commands specific to your environment
- Pluggable LLM provider system — easily add new providers
- Authentication credentials stored securely in your OS keyring
- Selectable models for configured LLM providers

## Installation

> [!IMPORTANT]
> Headless environments may require a third party keyring backend. See keyring documentation [here](https://github.com/jaraco/keyring#third-party-backends).

Install `how-tui` with `uv`:

```sh
uv tool install how-tui
```

### Requirements

- Python >= 3.14
- An API key for a supported LLM provider

## Usage

```plaintext
$ how
usage: how [-h] [--list-supported-providers] [--list-configured-providers] [--add-provider]
           [--remove-provider] [--set-default-provider] [--set-model] [--debug] [--provider PROVIDER]
           [--model MODEL]
           [prompt]

positional arguments:
  prompt                Question for the LLM

options:
  -h, --help            show this help message and exit
  --list-supported-providers
                        List all supported LLM providers
  --list-configured-providers
                        List your configured LLM providers
  --add-provider        Setup an LLM provider
  --remove-provider     Remove an LLM provider
  --set-default-provider
                        Set a default LLM provider
  --set-model           Set a default model for a provider
  --debug               Enable debug level logging
  --provider PROVIDER   Specify an LLM provider
  --model MODEL         Specify a model
```

### First-Time Setup

```bash
how --add-provider
```

This will walk you through selecting an LLM provider and authenticating.

### Ask a question

```bash
how "compress a folder"
how "find all files larger than 100MB"
how "list all running docker containers"
how "rename multiple files at once"
```

## TODO List

- Shell-aware syntax highlighting in the displayed commands.
- Add support for more LLM providers.
- Display a short explanation alongside each suggested command.

## Supported Providers

| Provider | Status |
|----------|--------|
| Google Gemini | Supported |
| Groq | Supported |

### Adding a New LLM Provider

Create a new Python file in `src/how_tui/providers/` with a class that subclasses `LLMProvider`:

```python
class LLMProvider(ABC):
    @staticmethod
    @abstractmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse: ...

    """Send request to the LLM to generate commands based on the user question.

    Returns:
        CommandResponse: List of commands.

    Raises:
        GenerateCommandsError: When an issue occurs while generating commands.
    """

    @staticmethod
    @abstractmethod
    def authenticate(console: Console, force: bool = False) -> bool: ...

    """Authenticate the user with the LLM provider.
    
    Returns:
        bool: True for successful authentication, False otherwise.
    """

    @staticmethod
    @abstractmethod
    def unauthenticate() -> None: ...

    """Remove authentication for the LLM provider (ex. delete API key)."""

    @staticmethod
    @abstractmethod
    def get_models() -> list[str]: ...

    """
    Retrieve a list of models supported by the LLM provider.
    
    Returns: 
        list[str]: A list of models supported by the LLM provider.

    Raises:
        FetchModelsError: When an error occurs while fetching models.
    """
```

## License

MIT
