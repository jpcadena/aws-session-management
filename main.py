"""
The main script that initiates and runs the FastAPI application.
This module sets up the application configuration.
"""

import logging
from functools import partial

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware

from app.api.api_v1.api import api_router
from app.config.config import init_setting, setting
from app.core import logging_setup
from app.core.lifecycle import lifespan
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.utils.openapi_utils import custom_generate_unique_id, custom_openapi

logging_setup.setup_logging(init_setting)
logger: logging.Logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(
    openapi_url=f"{setting.API_V1_STR}{init_setting.OPENAPI_FILE_PATH}",
    default_response_class=UJSONResponse,
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
    docs_url=None,
)
app.openapi = partial(custom_openapi, app)  # type: ignore
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount(
    init_setting.ASSETS_DIR,
    StaticFiles(
        directory=init_setting.ASSETS_APP,
    ),
    name=init_setting.ASSETS_APP,
)
app.include_router(api_router, prefix=setting.API_V1_STR)


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


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    """
    Custom Swagger UI for API documentation page in HTML

    :param request: The FastAPI request from the server
    :type request: Request
    :return: The response in HTML
    :rtype: HTMLResponse
    """
    root_path = request.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"{init_setting.API_NAME} - Swagger UI",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=f"{setting.HOST}",
        port=setting.PORT,
        reload=setting.SERVER_RELOAD,
    )
