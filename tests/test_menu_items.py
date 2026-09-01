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
                                                               f"Expected: en,"
                                                               f"Actual: {json_response['detected_source_language']}")


def test_update_menu_item(app, restaurant, menu_item):

    client = app.test_client()

    restaurant_id = restaurant["id"]
    menu_item_id = menu_item["id"]

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



@pytest.mark.parametrize("category",
                         ["entree",
                          "dessert",
                          "appetizer",
                          "beverage"
                         ])

def test_filter_menu_items_by_category(app, restaurant, category):

    client = app.test_client()
    restaurant_id = restaurant["id"]

    payload = {
        "name": "Test Item",
        "description": "Test description",
        "price": 10.99,
        "category": category
    }

    with patch(
        "menu_translator.services.menu_item_service.detect_language",
        return_value=("en", 0.99)
        ):
        create_response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu_items", json=payload)

        assert create_response.status_code == 201, (
            f"Failed to create item: {create_response.get_json()}"
        )

    response = client.get(f"/api/v1/restaurants/{restaurant_id}/menu_items?category={category}")

    json_response = response.get_json()

    assert response.status_code == 200, f"Unexpected status code. Expected 200, Actual: {response.status_code}"

    assert len(json_response) > 0, f"Amount of menu items should be > 0, Actual: {len(json_response)}"

    assert json_response[0]["category"] == category, (f"Unexpected category"
                                                      f"Expected: {payload['category']},"
                                                      f"Actual: {json_response['category']}")


@pytest.mark.parametrize("sort",
                         ["price_asc",
                          "price_desc",
                          "name_asc",
                          "name_desc"
                         ])
def test_sort_menu_items(app, restaurant, menu_item, sort):
    """verifies that sort is a valid query param"""
    client = app.test_client()
    restaurant_id = restaurant["id"]
    # first item comes from fixture
    second_menu_item_payload = {
        "name": "chocolate cake",
        "description": "yummy cake",
        "price": 5.99,
        "category": "dessert"
    }

    with patch(
            "menu_translator.services.menu_item_service.detect_language",
            return_value=("en", 0.99)
            ):
        response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu_items", json=second_menu_item_payload)

    assert response.status_code == 201, f"Unexpected status code. Expected 201, Actual: {response.status_code}"

    response = client.get(f"/api/v1/restaurants/{restaurant_id}/menu_items?sort={sort}")
    assert response.status_code == 200, f"Unexpected status code. Expected 200, Actual: {response.status_code}"

    json_response = response.get_json()

    if sort == "price_asc":
        assert json_response[0]["price"] <= json_response[1]["price"]
    elif sort == "price_desc":
        assert json_response[0]["price"] >= json_response[1]["price"]
    elif sort == "name_asc":
        assert json_response[0]["name"].lower() <= json_response[1]["name"].lower()
    elif sort == "name_desc":
        assert json_response[0]["name"].lower() >= json_response[1]["name"].lower()



def test_get_menu_items_with_translation(app, restaurant):
    """using mocked comprehend and translate clients to assert language detected and translation workflow works """
    client = app.test_client()

    restaurant_id = restaurant["id"]

    # First create an English menu item
    payload = {"name": "Cheeseburger",
                "description": "Burger with cheese",
                "price": 12.99,
                "category": "entree"
                }

    with patch("menu_translator.services.menu_item_service.detect_language", return_value=("en", 0.99)):
        create_response = client.post(f"/api/v1/restaurants/{restaurant_id}/menu_items", json=payload)

    assert create_response.status_code == 201, f"Unexpected status code. Expected 201, Actual: {create_response.status_code}"



    with patch("menu_translator.services.menu_item_service.translate") as mock_translate:

        mock_translate.side_effect = [{"translated_text": "hamburguesa",
                                        "source_language": "en",
                                        "target_language": "es"
                                        },
                                       {"translated_text": "hamburguesa con queso",
                                        "source_language": "en",
                                        "target_language": "es"
                                        }
                                      ]

        response = client.get(f"/api/v1/restaurants/{restaurant_id}/menu_items?lang=es")

    assert response.status_code == 200, f"Unexpected status code. Expected 200, Actual: {response.status_code}"

    json_response = response.get_json()

    assert json_response[0]["name"] == "hamburguesa", (f"Error. Expected name: 'hamburguesa' "
                                                       f"Actual name: {json_response[0]['name']}")

    assert json_response[0]["description"] == "hamburguesa con queso", (f"Error. Expected description: 'hamburguesa con queso' "
                                                                        f"Actual description: {json_response[0]['description']}")

