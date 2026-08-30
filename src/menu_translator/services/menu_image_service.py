"""Service module for importing menu images and extracting menu item candidates"""
import re
import uuid

from werkzeug.datastructures import FileStorage
from botocore.exceptions import BotoCoreError, ClientError

from menu_translator.config import AWS_BUCKET_NAME
from menu_translator.errors import RestaurantManagementError, AWSError
from menu_translator.services import restaurant_service
from menu_translator.ai import s3, textract


ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png"}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def read_upload(file: FileStorage | None,
                allowed_extensions: set[str],
                max_bytes: int) -> tuple[bytes, str]:

    if file is None or not file.filename:
        raise RestaurantManagementError("validation_failed", 422, "no file uploaded")

    extension = file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        raise RestaurantManagementError("unallowed_file_type", 422, f"{list(allowed_extensions)}")

    content = file.read()
    if len(content) > max_bytes:
        raise RestaurantManagementError("file_too_large", 413, f"file exceeds {MAX_FILE_SIZE} bytes.")

    if not content:
        raise RestaurantManagementError("validation_failed", 422, "empty file uploaded")


    return content, file.filename



def import_menu_image(restaurant_id: int,
                      file: FileStorage | None) -> dict:

    restaurant_service.find_restaurant_by_id(restaurant_id)

    content, filename = read_upload(file, ALLOWED_IMAGE_TYPES, MAX_FILE_SIZE)

    extension = filename.rsplit(".", 1)[1].lower()
    if extension == "png":
        content_type = "image/png"
    else:
        content_type  = "image/jpeg"


    object_key = (
        f"restaurants/"
        f"{restaurant_id}/"
        f"menu-imports/"
        f"{uuid.uuid4()}.{extension}"
    )

    if not AWS_BUCKET_NAME:
        raise AWSError("no_s3_bucket_configured", 500, "AWS s3 bucket not configured")

    try:
        s3.upload_file(content, AWS_BUCKET_NAME, object_key, content_type)
    except (BotoCoreError, ClientError) as e:
        raise AWSError("s3_upload_failed", 500, "unable to upload menu image file") from e

    try:
        lines = textract.extract_lines(AWS_BUCKET_NAME, object_key)
    except (BotoCoreError, ClientError):



    if not lines:
        return {
            "status": "no_text_found",
            "restaurant_id": restaurant_id,
            "object_key": object_key,
            "candidates": []
        }

    candidates = parse_menu_lines(lines)


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

    return {
        "raw_text": line,
        "name": None,
        "description": None,
        "price": None,
        "category": None,
        "parsed": False
    }