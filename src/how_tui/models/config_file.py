"""
Expected layout of the configuration file.
"""

from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    default_provider: str | None = Field(...)
    # Key: Provider Name, Value: Provider Details
    providers: dict[str, ProviderConfig] = Field(...)


class ProviderConfig(BaseModel):
    model: str
