"""test module for menu items endpoints to ensure failures occur when they are expected"""
import pytest

def test_create_menu_item_negative_price(app, restaurant):

    client = app.test_client()

    restaurant_id = restaurant["data"]["id"]

    payload = {
        "name": "Burger",
        "description": "Burger with cheese",
        "price": -10.00,
        "category": "entree"
    }

    response = client.post(
        f"/api/v1/restaurants/{restaurant_id}/menu_items",
        json=payload
    )

    assert response.status_code == 422, f"Unexpected status code. Expected: 422 Actual: {response.status_code}"


def test_create_menu_item_invalid_category(app, restaurant):

    client = app.test_client()

    restaurant_id = restaurant["data"]["id"]

    payload = {"name": "Burger",
                "description": "Burger with cheese",
                "price": 12.99,
                "category": "pizza"
                }

    response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu_items", json=payload)

    assert response.status_code == 422, f"Unexpected status code. Expected: 422 Actual: {response.status_code}"