"""
A module for examples in the app-schemas package.
"""

from typing import Any

from pydantic import PositiveInt

health_example: dict[PositiveInt | str, dict[str, Any]] | None = {
    200: {
        "content": {
            "application/json": {
                "example": [
                    {
                        "dynamodb": "healthy",
                        "sqs": "healthy",
                    },
                ],
            },
        },
    },
    503: {
        "content": {
            "application/json": {
                "example": [
                    {
                        "status": "unhealthy",
                        "sqs": "unhealthy",
                    },
                    {
                        "status": "healthy",
                        "sqs": "unhealthy",
                    },
                    {
                        "status": "unhealthy",
                        "sqs": "healthy",
                    },
                ],
            },
        },
    },
}
