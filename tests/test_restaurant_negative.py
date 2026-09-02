"""test module for testing negative cases and asserting proper error response is received"""
from flask import Flask

def test_create_restaurant_invalid_payload(app: Flask) -> None:
    """asserting create restaurant with invalid data fails and returns 422 status code"""
    client = app.test_client()

    restaurant_payload = {"name": "",
                          "cuisine_type": "",
                          "default_menu_language": "e"
                          }



    response = client.post("/api/v1/restaurants", json=restaurant_payload)

    assert response.status_code == 422, f"Unexpected status code. Expected: 422, Actual: {response.status_code}"

