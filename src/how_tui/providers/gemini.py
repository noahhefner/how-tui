from getpass import getpass

import keyring
from google import genai
from google.genai.pagers import Pager
from pydantic import ValidationError
from rich.console import Console

from how_tui.models.command import CommandResponse
from how_tui.providers.base import FetchModelsError, GenerateCommandsError, LLMProvider


class GeminiProvider(LLMProvider):
    @staticmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse:
        """Send request to Gemini.

        Response format is specified in the request.

        Assumptions:
            - User is authenticated.

        Raises:
            GenerateCommandsError: If an error occurs while interacting with
                Gemini API.
        """

        client = GeminiProvider._get_client()

        try:
            interaction = client.interactions.create(
                model=model,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": CommandResponse.model_json_schema(),
                },
            )
        except Exception as e:
            raise GenerateCommandsError(
                "Error while generating commands with Gemini"
            ) from e

        try:
            return CommandResponse.model_validate_json(interaction.output_text)  # ty: ignore[invalid-argument-type, unresolved-attribute]
        except ValidationError as e:
            raise GenerateCommandsError(
                "Gemini response failed model validation"
            ) from e

    @staticmethod
    def authenticate(console: Console, force: bool = False) -> bool:
        """Authenticate with Google Gemini via API key.

        API key is securely stored via keyring.

        Use the force argument to overwrite existing API key.

        Returns:
            bool: True for successful authentication, False otherwise.
        """

        api_key = keyring.get_password("how-tui", "Gemini")

        if force or api_key is None:
            api_key = getpass("Gemini API key: ")
            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                return False

            keyring.set_password("how-tui", "Gemini", api_key)
        return True

    @staticmethod
    def unauthenticate() -> None:
        """Clear local credentials."""

        keyring.delete_password("how-tui", "Gemini")

    @staticmethod
    def get_models() -> list[str]:
        """Get all Gemini models via the API.

        Requires authentication to list models.

        Raises:
            FetchModelsError: If an error occurs while communicating with the
                Gemini API.
        """

        client = GeminiProvider._get_client()

        try:
            models: Pager = client.models.list()
        except Exception as e:
            raise FetchModelsError("Error while fetching Gemini models") from e

        return [m.name for m in list(models)]

    @staticmethod
    def _get_client() -> genai.Client:
        """Create and return a Gemini client.

        Assumptions:
            - User is authenticated.
        """

        api_key = keyring.get_password("how-tui", "Gemini")
        assert api_key is not None
        return genai.Client(api_key=api_key)
