"""module for interacting with AWS S3"""
from typing import Any

from menu_translator.ai.aws import get_client


def upload_file(
    content: bytes,
    bucket_name: str,
    object_key: str,
    content_type: str,
    client: Any | None = None
) -> None:
    """uploads a file to s3 bucket"""

    s3_client = client or get_client("s3")

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=content,
        ContentType=content_type
    )