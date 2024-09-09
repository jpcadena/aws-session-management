"""
A module for DynamoDB in the app.db package.
"""

import logging

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from app.config.config import setting
from app.exceptions.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
)

logger: logging.Logger = logging.getLogger(__name__)

dynamodb: DynamoDBServiceResource = boto3.resource(
    "dynamodb",
    region_name=setting.AWS_REGION,
    aws_access_key_id=setting.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=setting.AWS_SECRET_ACCESS_KEY,
)


def get_table() -> Table:
    """
    Retrieve the existing DynamoDB table instance.

    :return: The DynamoDB table object.
    :rtype: Table
    """
    try:
        table: Table = dynamodb.Table("UserSessions")
        table.load()
        return table
    except ClientError as e:
        logger.error("Error accessing table: %s", e)
        raise DatabaseConnectionError(
            detail="Failed to access the DynamoDB table."
        ) from e


def check_db_health(table: Table) -> bool:
    """
    Check the health of the DynamoDB table connection.

    :param table: The DynamoDB table object used to interact with the database.
    :type table: Table
    :returns: True if the database connection is healthy, False otherwise.
    :rtype: bool
    """
    try:
        item_count = table.item_count
        logger.info(f"Item count for table '{table.name}': {item_count}")
        return True
    except ClientError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseOperationError(
            detail="Failed to check DynamoDB table health."
        ) from e
