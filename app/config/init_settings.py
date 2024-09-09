"""
A module for init settings in the app.config package.
"""

from datetime import date
from pathlib import Path

from fastapi.openapi.models import Example
from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.image_utils import convert_image_to_base64


class InitSettings(BaseSettings):
    """Init Settings class based on Pydantic Base Settings"""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="allow",
    )

    ASSETS_APP: str = "static"
    ASSETS_DIR: str = f"/{ASSETS_APP}"
    IMAGES_SUBDIR: str = "images"
    IMAGES_DIRECTORY: DirectoryPath = Path(ASSETS_APP) / IMAGES_SUBDIR
    API_NAME: str = "AWS Session Management"
    PROJECT_NAME: str = "aws-session-management"
    VERSION: str = "1.0"
    ENCODING: str = "UTF-8"
    OPENAPI_FILE_PATH: str = "/openapi.json"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FILE_DATE_FORMAT: str = "%d-%b-%Y-%H-%M-%S"
    LOG_FORMAT: str = (
        "[%(name)s][%(asctime)s][%(levelname)s][%(module)s]"
        "[%(funcName)s][%(lineno)d]: %(message)s"
    )
    SUMMARY: str = """This backend project is a RESTful API developed with
     FastAPI. This API provides a backend service for managing user sessions
      using AWS DynamoDB and designed to handle session-related operations
       such as creating, updating, and retrieving user session information"""
    img_b64: str = convert_image_to_base64(
        IMAGES_DIRECTORY.resolve() / "project.png"
    )
    DESCRIPTION: str = f"""**FastAPI** helps you do awesome stuff.🚀
    \n\n<img src="{img_b64}" width="800px" height="600px"/>"""
    LICENSE_INFO: dict[str, str] = {
        "name": "MIT",
        "identifier": "MIT",
    }
    session_b64: str = convert_image_to_base64(
        IMAGES_DIRECTORY.resolve() / "session.png"
    )
    TAGS_METADATA: list[dict[str, str]] = [
        {
            "name": "session",
            "description": f"""Session management.\n\n<img src="{session_b64}"
             width="150" height="100"/>""",
        },
    ]
    SESSION_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** user create object that works "
            "correctly.",
            "value": {
                "user_id": "some_uuid",
                "action": "some_action",
            },
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert `integers` to actual `strings`"
            " automatically",
            "value": {
                "user_id": 1,
                "action": "converted_action",
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "user_id": date(2004, 12, 31),
                "action": True,
            },
        },
    }
