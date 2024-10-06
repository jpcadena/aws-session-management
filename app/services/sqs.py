"""
A module for Simple Queue Service in the app.services package.
"""

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_sqs.client import SQSClient
from mypy_boto3_sqs.type_defs import SendMessageResultTypeDef

from app.config.config import setting
from app.exceptions.exceptions import SQSConnectionError

logger: logging.Logger = logging.getLogger(__name__)
sqs_client: SQSClient = boto3.client(
    "sqs",
    region_name=setting.AWS_REGION,
    aws_access_key_id=setting.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=setting.AWS_SECRET_ACCESS_KEY,
)


def check_sqs_health() -> bool:
    """
    Check the health of the SQS queue by sending a test message to validate
     connectivity.

    :returns: True if SQS is healthy, False otherwise.
    :rtype: bool
    """
    try:
        queue_url: str = sqs_client.get_queue_url(
            QueueName=setting.AWS_QUEUE_NAME
        )["QueueUrl"]
        logger.info(f"Successfully accessed SQS queue: {queue_url}")
        return True
    except ClientError as e:
        logger.error(f"SQS connection error: {e}")
        raise SQSConnectionError(
            detail="Failed to check SQS queue health."
        ) from e


def send_sqs_message(message_body: dict[str, Any]) -> None:
    """
    Send a message to the SQS queue.

    :param message_body: The body of the message to be sent to SQS.
    :type message_body: dict[str, Any]
    :return: None
    :rtype: NoneType
    """
    try:
        if queue_url := setting.SQS_QUEUE_URL:
            response: SendMessageResultTypeDef = sqs_client.send_message(
                QueueUrl=str(queue_url),
                MessageBody=json.dumps(message_body),
                DelaySeconds=0,
            )
            logger.info(f"Message sent to SQS: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"Failed to send message to SQS: {e}")
        raise e
