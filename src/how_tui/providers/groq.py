import json
import sys
from getpass import getpass

import keyring
from groq import Groq
from groq.types import ModelListResponse
from groq.types.chat.completion_create_params import (
    ResponseFormatResponseFormatJsonSchema,
)
from rich.console import Console

from how_tui.models.command import CommandResponse
from how_tui.providers.base import LLMProvider


class GroqProvider(LLMProvider):
    @staticmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse:

        client = GroqProvider._get_client()

        response_format: ResponseFormatResponseFormatJsonSchema = {
            "type": "json_schema",
            "json_schema": {
                "name": "terminal_commands",
                "strict": True,
                "schema": CommandResponse.model_json_schema(),
            },
        }

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
        )

        result = json.loads(response.choices[0].message.content or "{}")
        if not result:
            print("Empty result from Groq provider.")
            sys.exit(1)

        return CommandResponse.model_validate(result)

    @staticmethod
    def authenticate(console: Console, force: bool = False) -> bool:

        api_key = keyring.get_password("how-tui", "Groq")

        if force or api_key is None:
            api_key = getpass("Groq API key: ")

            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                return False

            keyring.set_password("how-tui", "Groq", api_key)

        return True

    @staticmethod
    def unauthenticate() -> None:

        keyring.delete_password("how-tui", "Groq")

    @staticmethod
    def get_models() -> list[str]:

        client = GroqProvider._get_client()
        models: ModelListResponse = client.models.list()

        return [m.id for m in models.data]

    @staticmethod
    def _get_client() -> Groq:

        api_key = keyring.get_password("how-tui", "Groq")
        if api_key is None:
            print("Groq not authenticated.", file=sys.stderr)
            sys.exit(1)

        return Groq(api_key=api_key)
