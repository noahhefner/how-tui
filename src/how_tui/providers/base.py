from abc import ABC, abstractmethod

from rich.console import Console

from how_tui.models.command import CommandResponse


class GenerateCommandsError(Exception):
    """
    Exception raised when a problem occurs while fetching commands from the LLM.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class FetchModelsError(Exception):
    """
    Exception raised when a problem occurs while fetching models for an LLM
    provider.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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
