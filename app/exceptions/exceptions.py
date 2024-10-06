"""
A module for custom exceptions in the app-exceptions package.
"""

from fastapi import HTTPException, status


class DatabaseConnectionError(HTTPException):
    """
    Custom exception for database connection errors.
    """

    def __init__(self, detail: str = "Database connection error."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail
        )


class DatabaseOperationError(HTTPException):
    """
    Custom exception for database operation errors.
    """

    def __init__(
        self,
        detail: str = "An error occurred during the database" " operation.",
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class SQSConnectionError(Exception):
    """Raised when the SQS connection fails."""

    def __init__(self, detail: str):
        self.detail: str = detail
        super().__init__(self.detail)


class SQSSendMessageError(Exception):
    """Raised when sending a message to SQS fails."""

    def __init__(self, detail: str):
        self.detail: str = detail
        super().__init__(self.detail)
