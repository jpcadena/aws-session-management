"""
A module for settings in the app.config package.
"""

from typing import Any

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    Field,
    HttpUrl,
    IPvAnyAddress,
    PositiveInt,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class based on Pydantic Base Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    API_V1_STR: str = "/api/v1"
    NO_CLIENT_FOUND: str = "No client found on the request"
    CERTIFICATE_TRANSPARENCY_MAX_AGE: PositiveInt = 86400  # seconds
    HOST: IPvAnyAddress
    PORT: PositiveInt
    SERVER_RELOAD: bool
    SERVER_LOG_LEVEL: str
    SERVER_URL: HttpUrl
    SERVER_DESCRIPTION: str
    SWAGGER_SHA_KEY: str
    STRICT_TRANSPORT_SECURITY_MAX_AGE: PositiveInt

    AWS_ACCESS_KEY_ID: str = Field(
        ...,
        title="AWS Access Key",
        description="AWS Access Key",
        min_length=20,
        max_length=20,
    )
    AWS_SECRET_ACCESS_KEY: str = Field(
        ...,
        title="AWS Secret Access Key",
        description="AWS Secret Access Key",
        min_length=40,
        max_length=40,
    )
    AWS_REGION: str = Field(
        ...,
        title="AWS Region",
        description="AWS Region Code",
        pattern=r"^[a-z]{2}-[a-z]{4,9}-\d$",
    )

    CONTACT_NAME: str | None = None
    CONTACT_URL: AnyHttpUrl | None = None
    CONTACT_EMAIL: EmailStr | None = None
    CONTACT: dict[str, Any] | None = None

    @field_validator("CONTACT", mode="before")
    def assemble_contact(
        cls,
        v: str | None,
        info: ValidationInfo,  # noqa: argument-unused
    ) -> dict[str, str]:
        """
        Assemble contact information

        :param v: Variables to consider
        :type v: str
        :param info: The field validation info
        :type info: ValidationInfo
        :return: The contact attribute
        :rtype: dict[str, str]
        """
        if info.config is None:
            raise ValueError("info.config cannot be None")
        contact: dict[str, Any] = {}
        if info.data.get("CONTACT_NAME"):
            contact["name"] = info.data.get("CONTACT_NAME")
        if info.data.get("CONTACT_URL"):
            contact["url"] = info.data.get("CONTACT_URL")
        if info.data.get("CONTACT_EMAIL"):
            contact["email"] = info.data.get("CONTACT_EMAIL")
        return contact
