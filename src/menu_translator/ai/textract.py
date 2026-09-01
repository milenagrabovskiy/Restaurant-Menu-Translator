"""module for using AWS textract"""
from typing import Any

from menu_translator.ai.aws import get_client


def extract_lines(bucket_name: str, object_key: str, client: Any | None = None) -> list[str]:
    """Extract text lines from an image stored in S3 bucket"""
    client = client if client is not None else get_client("textract")

    response = client.detect_document_text(Document={"S3Object": {
                                                              "Bucket": bucket_name,
                                                             "Name": object_key}
                                                              })
    return [block["Text"] for block in response["Blocks"] if block["BlockType"] == "LINE"]