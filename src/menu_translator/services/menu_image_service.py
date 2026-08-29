import os
import re
import uuid

from werkzeug.datastructures import FileStorage

from menu_translator.services import restaurant_service
from menu_translator.ai import aws


ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def import_menu_image(
    restaurant_id: int,
    file: FileStorage | None
) -> dict:

    # 1. Make sure restaurant exists
    restaurant_service.find_restaurant_by_id(restaurant_id)

    # 2. Make sure file was provided
    if file is None:
        raise ValueError("Menu image is required.")

    # 3. Make sure file has a filename
    if not file.filename:
        raise ValueError("Menu image filename is required.")

    # 4. Validate JPG / PNG
    if file.mimetype not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Only JPG and PNG menu images are allowed."
        )

    # 5. Validate file size
    file.stream.seek(0, 2)
    file_size = file.stream.tell()
    file.stream.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            "Menu image cannot be larger than 5 MB."
        )

    # 6. Determine extension
    extension = ALLOWED_IMAGE_TYPES[file.mimetype]

    # 7. Generate unique S3 key
    object_key = (
        f"restaurants/"
        f"{restaurant_id}/"
        f"menu-imports/"
        f"{uuid.uuid4()}.{extension}"
    )

    # Get bucket name from environment configuration
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("AWS_S3_BUCKET_NAME environment variable is not set.")

    # 8. Upload raw image to S3 using boto3's upload_fileobj
    s3_client = aws.get_client("s3")
    s3_client.upload_fileobj(
        Fileobj=file.stream,
        Bucket=bucket_name,
        Key=object_key,
        ExtraArgs={"ContentType": file.mimetype}
    )

    # 9. Ask Textract to read the image
    textract_client = aws.get_client("textract")
    response = textract_client.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": object_key
            }
        }
    )

    # Extract raw text lines from Textract's block response structure
    lines = [
        block["Text"]
        for block in response.get("Blocks", [])
        if block.get("BlockType") == "LINE"
    ]

    # 10. Textract found nothing
    if not lines:
        return {
            "status": "no_text_found",
            "restaurant_id": restaurant_id,
            "object_key": object_key,
            "candidates": []
        }

    # 11. Convert OCR lines into candidate menu items
    candidates = parse_menu_lines(lines)

    # 12. Return candidates
    # DO NOT save them to PostgreSQL
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "object_key": object_key,
        "candidates": candidates
    }


def parse_menu_lines(lines: list[str]) -> list[dict]:
    candidates = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        candidate = parse_menu_line(line)

        candidates.append(candidate)

    return candidates


def parse_menu_line(line: str) -> dict:

    # Examples this attempts to understand:
    #
    # Margherita Pizza .... 14.00
    # Cheeseburger $12.99
    # Caesar Salad 11.50

    price_pattern = r"^(.*?)[\s.]*\$?(\d+(?:\.\d{1,2})?)$"

    match = re.match(price_pattern, line)

    if match:

        name = match.group(1).strip(" .")
        price = float(match.group(2))

        if name:
            return {
                "raw_text": line,
                "name": name,
                "description": None,
                "price": price,
                "category": None,
                "parsed": True
            }

    # We couldn't safely understand the line.
    # Do NOT throw it away.
    return {
        "raw_text": line,
        "name": None,
        "description": None,
        "price": None,
        "category": None,
        "parsed": False
    }