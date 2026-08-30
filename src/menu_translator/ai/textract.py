"""module for using AWS textract"""
from menu_translator.ai.aws import get_client


def extract_lines(bucket_name: str, object_key: str) -> list[str]:
    """Extract text lines from an image stored in S3 bucket"""

    textract_client = get_client("textract")

    response = textract_client.detect_document_text(Document={"S3Object": {
                                                              "Bucket": bucket_name,
                                                             "Name": object_key}
                                                              })
    return [block["Text"] for block in response["Blocks"] if block["BlockType"] == "LINE"]