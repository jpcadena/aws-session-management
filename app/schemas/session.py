"""
A module for session in the app-schemas package.
"""

from pydantic import BaseModel, Field


class SessionRequest(BaseModel):
    """Model for session request data."""

    user_id: str = Field(
        ...,
        title="User ID",
        description="The unique identifier of the user.",
    )
    action: str = Field(
        ...,
        title="Action",
        description="The action performed by the user.",
    )


class SessionResponse(BaseModel):
    """Model for session response data."""

    user_id: str = Field(
        ...,
        title="User ID",
        description="The unique identifier of the user.",
    )
    last_action: str = Field(
        ...,
        title="Last Action",
        description="The last action performed by the user.",
    )
