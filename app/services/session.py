"""
A module for session in the app.services package.
"""

import logging

from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import UpdateItemOutputTableTypeDef

from app.db.dynamodb import get_table
from app.exceptions.exceptions import DatabaseOperationError
from app.schemas.session import SessionRequest, SessionResponse

logger: logging.Logger = logging.getLogger(__name__)


def process_session(request: SessionRequest) -> SessionResponse:
    """
    Process the session request by updating or creating session data in
    DynamoDB.

    :param request: The request containing user session details.
    :type request: SessionRequest
    :return: The updated session response object.
    :rtype: SessionResponse
    :raises DatabaseOperationError: If there is an error interacting with
     DynamoDB.
    """
    table: Table = get_table()
    try:
        response: UpdateItemOutputTableTypeDef = table.update_item(
            Key={"user_id": request.user_id},
            UpdateExpression="SET last_action = :action",
            ExpressionAttributeValues={":action": request.action},
            ReturnValues="UPDATED_NEW",
        )
        updated_action: str = str(response["Attributes"]["last_action"])
        logger.info(f"Updated action into DynamoDB table: {table.name}")
        return SessionResponse(
            user_id=request.user_id, last_action=updated_action
        )
    except ClientError as e:
        logger.error(f"Error updating session: {e}")
        raise DatabaseOperationError(
            detail="Failed to update session in DynamoDB."
        ) from e
