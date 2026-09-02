"""test module to test image upload and bypassing AWS Textract with mocked client"""
import io
from unittest.mock import patch
from flask import Flask

from menu_translator.models.restaurant import Restaurant


def test_import_menu_image_with_mocked_textract(app: Flask, restaurant: Restaurant) -> None:
    """asserts image import is successful"""
    client = app.test_client()
    restaurant_id = restaurant["id"]

    fake_image = io.BytesIO(b"fake image bytes")

    with patch("menu_translator.services.menu_image_service.AWS_BUCKET_NAME","test-bucket"), patch(
        "menu_translator.services.menu_image_service.s3.upload_file"
    ) as mock_s3, patch("menu_translator.services.menu_image_service.textract.extract_lines",
                                return_value=["Cheeseburger $12.99",
                                              "Caesar Salad $10.00"
                                              ]) as mock_textract:

        response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu-import",
                                data={"file": (fake_image, "menu.jpg")},
                                content_type="multipart/form-data"
                                )

    assert response.status_code == 201

    json_response = response.get_json()

    assert json_response["status"] == "success"
    assert len(json_response["candidates"]) == 2

    assert json_response["candidates"][0]["name"] == "Cheeseburger"
    assert json_response["candidates"][0]["price"] == 12.99
    assert json_response["candidates"][0]["parsed"] is True

    mock_s3.assert_called_once()
    mock_textract.assert_called_once()