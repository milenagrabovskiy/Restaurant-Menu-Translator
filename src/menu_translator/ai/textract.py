from typing import Any

from menu_translator.ai.aws import get_client


def extract_lines(bucket_name: str,
                  object_key: str,
                  client: Any | None = None
                  ) -> list[str]:
    """Extract text lines from an image stored in S3 bucket"""

    textract_client = client or get_client("textract")

    response = textract_client.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": object_key
            }
        }
    )

    lines = []

    for block in response.get("Blocks", []):
        if block.get("BlockType") == "LINE" and block.get("Text"):
            lines.append(block["Text"])

    return lines