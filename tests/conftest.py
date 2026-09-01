
import pytest

from menu_translator.app import create_app
from menu_translator.extensions import db



TEST_CONFIG = {"TESTING": True, "SQLALCHEMY_DATABASE_URI":
                                        "postgresql://postgres:root@localhost:5432/restaurant_menu_test_db"}


@pytest.fixture
def app():
    app = create_app(TEST_CONFIG)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove() # db teardown
        db.drop_all()

    return app



@pytest.fixture
def restaurant(app, restaurant_payload):

    client = app.test_client()

    response = client.post("/api/v1/restaurants", json=restaurant_payload)

    assert response.status_code == 201

    return response.get_json()


@pytest.fixture
def restaurant_payload():

    return {
        "name": "Test Restaurant",
        "cuisine_type": "American",
        "default_menu_language": "en"
        }

