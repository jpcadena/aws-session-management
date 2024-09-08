"""
The main script that initiates and runs the FastAPI application.
This module sets up the application configuration.
"""

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, UJSONResponse
from starlette.middleware.gzip import GZipMiddleware

app: FastAPI = FastAPI(
    default_response_class=UJSONResponse,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get(
    "/",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def redirect_to_docs() -> RedirectResponse:
    """
    Redirects the user to the /docs endpoint for API documentation.

    ## Response:
    - `return:` **The redirected response**
    - `rtype:` **RedirectResponse**
    """
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )
