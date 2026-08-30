from unittest.mock import patch

import pytest


@pytest.fixture
def menu_item(app, restaurant):

    client = app.test_client()

    payload = {
        "name": "Cheeseburger",
        "description": "Burger with cheese",
        "price": 12.99,
        "category": "entree"
    }
    restaurant_id = restaurant["id"]

    with patch("menu_translator.services.menu_item_service.detect_language",
               return_value=("en", 0.89)):
        response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu_items", json=payload)

        assert response.status_code == 201, f"Unexpected status code. Expected 201, Actual: {response.status_code}"

        return response.get_json()


def test_get_all_menu_items(app, restaurant, menu_item):

    client = app.test_client()

    restaurant_id = restaurant["id"]

    response = client.get(f"/api/v1/restaurants/{restaurant_id}/menu_items")

    json_response = response.get_json()

    assert response.status_code == 200, f"Unexpected status code. Expected 200, Actual: {response.status_code}"
    assert len(json_response) > 0

    assert json_response[0]["name"] == menu_item["name"],  (f"Unexpected name"
                                                            f"Expected: {menu_item['name']},"
                                                            f"Actual: {json_response[0]['name']}")

    assert json_response[0]["description"] == menu_item["description"], (f"Unexpected description"
                                                            f"Expected: {menu_item['description']},"
                                                            f"Actual: {json_response[0]['description']}")

    assert json_response[0]["price"] == menu_item["price"], (f"Unexpected price"
                                                            f"Expected: {menu_item['price']},"
                                                            f"Actual: {json_response[0]['price']}")

    assert json_response[0]["category"] == menu_item["category"], (f"Unexpected category"
                                                            f"Expected: {menu_item['category']},"
                                                            f"Actual: {json_response[0]['category']}")


def test_create_menu_item(app, restaurant):

    client = app.test_client()

    restaurant_id = restaurant["id"]

    payload = {
        "name": "Cheeseburger",
        "description": "Burger with cheese",
        "price": 12.99,
        "category": "entree"
    }

    with patch(
            "menu_translator.services.menu_item_service.detect_language",
            return_value=("en", 0.99)
    ):
        response = client.post(
            f"/api/v1/restaurants/{restaurant_id}/menu_items",
            json=payload
        )

    json_response = response.get_json()

    assert response.status_code == 201,  f"Unexpected status code. Expected 201, Actual: {response.status_code}"

    assert json_response["name"] == payload["name"], (f"Unexpected name"
                                                       f"Expected: {payload['name']},"
                                                       f"Actual: {json_response['name']}")

    assert json_response["description"] == payload["description"], (f"Unexpected description"
                                                                   f"Expected: {payload['description']},"
                                                                   f"Actual: {json_response['description']}")

    assert json_response["price"] == payload["price"], (f"Unexpected price"
                                                       f"Expected: {payload['price']},"
                                                       f"Actual: {json_response['price']}")

    assert json_response["category"] == payload["category"], (f"Unexpected category"
                                                               f"Expected: {payload['category']},"
                                                               f"Actual: {json_response['category']}")

    assert json_response["detected_source_language"] == "en", (f"Unexpected detected_source_language"
                                                               f"Expected: {payload['detected_source_language']},"
                                                               f"Actual: {json_response['detected_source_language']}")


def test_update_menu_item(app, restaurant, menu_item):

    client = app.test_client()

    restaurant_id = restaurant["id"]
    menu_item_id = menu_item["id"]

    response = client.put(f"api/v1/restaurants/{restaurant_id}/menu_items/{menu_item_id}")

    payload = {
        "name": "Updated Burger",
        "description": "Updated burger description",
        "price": 15.99,
        "category": "entree"
    }

    with patch("menu_translator.services.menu_item_service.detect_language",
               return_value=("en", 0.99)):

        response = client.put(f"/api/v1/restaurants/{restaurant_id}/menu_items/{menu_item_id}",json=payload )

    json_response = response.get_json()

    assert response.status_code == 200, f"Unexpected status code. Expected 200, Actual: {response.status_code}"

    assert json_response["name"] == payload["name"], (f"Unexpected name"
                                                       f"Expected: {payload['name']},"
                                                       f"Actual: {json_response['name']}")

    assert json_response["description"] == payload["description"], (f"Unexpected description"
                                                                   f"Expected: {payload['description']},"
                                                                   f"Actual: {json_response['description']}")

    assert json_response["price"] == payload["price"], (f"Unexpected price"
                                                       f"Expected: {payload['price']},"
                                                       f"Actual: {json_response['price']}")

    assert json_response["category"] == payload["category"], (f"Unexpected category"
                                                               f"Expected: {payload['category']},"
                                                               f"Actual: {json_response['category']}")


def test_delete_menu_items(app, restaurant, menu_item):

    client = app.test_client()

    restaurant_id = restaurant["id"]
    menu_item_id = menu_item["id"]
    payload = {"menu_item_id": menu_item_id}

    response = client.delete(f"/api/v1/restaurants/{restaurant_id}/menu_items/{menu_item_id}", json=payload)

    assert response.status_code == 204,  f"Unexpected status code. Expected 204, Actual: {response.status_code}"

