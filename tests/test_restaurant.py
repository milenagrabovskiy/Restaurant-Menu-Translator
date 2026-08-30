import pytest


@pytest.fixture
def restaurant_payload():

    return {
        "name": "Test Restaurant",
        "cuisine_type": "American",
        "default_menu_language": "en"
    }


@pytest.mark.tcid1
def test_create_restaurant(app, restaurant_payload):
    client = app.test_client()

    response = client.post(
        "/api/v1/restaurants",
        json=restaurant_payload
    )

    json_response = response.get_json()

    assert response.status_code == 201, f"Unexpected status code. Expected: 201, Actual: {response.status_code}"

    assert json_response["name"] == restaurant_payload["name"], (f"Unexpected name."
                                                       f"Expected: {restaurant_payload['name']},"
                                                       f"Actual: {json_response["name"]}")

    assert json_response["cuisine_type"] == restaurant_payload["cuisine_type"],  (f"Unexpected cuisine_type."
                                                              f"Expected: {restaurant_payload['cuisine_type']},"
                                                              f"Actual: {json_response["name"]}")

    assert json_response["default_menu_language"] == restaurant_payload["default_menu_language"],\
                                                                (f"Unexpected default_menu_language."
                                                                 f"Expected: {restaurant_payload['default_menu_language']},"
                                                                 f"Actual: {json_response["default_menu_language"]}")

@pytest.mark.tcid2
def test_get_restaurants(app, restaurant):

    client = app.test_client()

    response = client.get("api/v1/restaurants")

    json_response = response.get_json()

    assert response.status_code == 200, f"Unexpected status code. Expected: 201, Actual: {response.status_code}"
    assert len(json_response) > 0
    # [0] bc it returns list
    assert json_response[0]["name"] == restaurant["name"]


@pytest.mark.tcid3
def test_update_restaurant(app, restaurant):

    client = app.test_client()
    restaurant_id = restaurant["id"]

    payload = {
        "name": "Updated Restaurant",
        "cuisine_type": "Mexican",
        "default_menu_language": "es"
    }
    response = client.put(f"/api/v1/restaurants/{restaurant_id}",json=payload)

    json_response = response.get_json()

    assert response.status_code == 200, f"Unexpected status code. Expected: 200, Actual: {response.status_code}"
    assert json_response["name"] == payload["name"], (f"Unexpected name."
                                                       f"Expected: {payload['name']},"
                                                       f"Actual: {json_response["name"]}")

    assert json_response["cuisine_type"] == payload["cuisine_type"], (f"Unexpected cuisine_type."
                                                              f"Expected: {payload['cuisine_type']},"
                                                              f"Actual: {json_response["cuisine_type"]}")

    assert (json_response["default_menu_language"] == payload["default_menu_language"]), \
                                                                (f"Unexpected default_menu_language."
                                                                 f"Expected: {payload['default_menu_language']},"
                                                                 f"Actual: {json_response["default_menu_language"]}")

@pytest.mark.tcid4
def test_delete_restaurant(app, restaurant):

    client = app.test_client()
    restaurant_id = restaurant["id"]

    payload = {"restaurant_id": restaurant_id}

    delete_response = client.delete(
        f"/api/v1/restaurants/{restaurant_id}", json=payload)

    assert delete_response.status_code == 204, (f"Unexpected status code."
                                                f"Expected: 204, Actual: {delete_response.status_code}")

    get_response = client.get(f"/api/v1/restaurants/{restaurant_id}")
    assert get_response.status_code == 404, f"Unexpected status code. Expected: 200, Actual: {get_response.status_code}"
