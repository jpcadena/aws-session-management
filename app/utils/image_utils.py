"""
A module for image utils in the app.utils package.
"""

import base64

from pydantic import FilePath


def convert_image_to_base64(image_path: FilePath) -> str:
    """
    Converts an image to base64 format

    :param image_path: Path to the image file
    :type image_path: FilePath
    :return: The image file in base64 format
    :rtype: str
    """
    with open(image_path, "rb") as image_file:
        encoded_string: str = base64.b64encode(image_file.read()).decode(
            "utf-8"
        )
    return f"data:image/png;base64,{encoded_string}"
