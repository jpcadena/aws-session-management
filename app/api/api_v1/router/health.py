"""
A module for health in the app.api.api v1.router package.
"""

import logging

from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse
from pydantic import PositiveInt

from app.db.dynamodb import check_db_health, get_table
from app.schemas.examples import health_example

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    responses=health_example,
)
async def check_health() -> ORJSONResponse:
    """
    Check the health of the application backend.

    ## Response:
    - `return:` **The ORJSON response**
    - `rtype:` **ORJSONResponse**
    \f
    """
    health_status: dict[str, str] = {
        "status": "healthy",
    }
    status_code: PositiveInt = status.HTTP_200_OK
    if not check_db_health(get_table()):
        health_status["status"] = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ORJSONResponse(health_status, status_code=status_code)
