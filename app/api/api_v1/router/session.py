"""
A module for session in the app.api.api_v1.router package.
"""

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from app.config.config import init_setting
from app.exceptions.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
)
from app.schemas.session import SessionRequest, SessionResponse
from app.services.session import process_session

router: APIRouter = APIRouter(prefix="/session", tags=["session"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def handle_session(
    request: Annotated[
        SessionRequest,
        Body(
            ...,
            title="Session data",
            description="Session data to create",
            openapi_examples=init_setting.SESSION_EXAMPLES,
        ),
    ],
) -> SessionResponse:
    """
    Handle session request by updating user session information.

    ## Parameters
    - `:param request:` **The request payload containing user session data**
    - `:type request:` **SessionRequest**

    ## Response:
    - `return:` **The updated session response**
    - `rtype:` **SessionResponse**
    """
    try:
        response: SessionResponse = process_session(request)
        return response
    except DatabaseConnectionError as db_conn_err:
        raise HTTPException(
            status_code=db_conn_err.status_code, detail=db_conn_err.detail
        ) from db_conn_err
    except DatabaseOperationError as db_op_err:
        raise HTTPException(
            status_code=db_op_err.status_code, detail=db_op_err.detail
        ) from db_op_err
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        ) from e
