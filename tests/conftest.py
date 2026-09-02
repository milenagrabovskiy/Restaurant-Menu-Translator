"""module for shared pytest fixtures used across multiple test files"""
import pytest
from flask import Flask
from menu_translator.app import create_app
from menu_translator.extensions import db
from menu_translator.models.restaurant import Restaurant

TEST_CONFIG = {"TESTING": True, "SQLALCHEMY_DATABASE_URI":
                                        "postgresql://postgres:root@localhost:5432/restaurant_menu_test_db"}


@pytest.fixture
def app() -> Flask:
    """configures and returns a Flask app instance for testing"""
    app = create_app(TEST_CONFIG)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove() # db teardown
        db.drop_all()

    return app



@pytest.fixture
def restaurant(app: Flask, restaurant_payload: dict) -> dict:
    """fixture that returns a created restaurant"""

    client = app.test_client()

    response = client.post("/api/v1/restaurants", json=restaurant_payload)

    assert response.status_code == 201

    return response.get_json()


@pytest.fixture
def restaurant_payload() -> dict:
    """fixture that returns a sample restaurant payload"""

    return {
        "name": "Test Restaurant",
        "cuisine_type": "American",
        "default_menu_language": "en"
        }

