"""module for testing that Flask is running and SQLAlchemy and PostgreSQL DB are connected"""
from flask import Flask
from unittest.mock import patch

def test_is_live(app: Flask) -> None:
    """asserting Flask is running"""
    client = app.test_client()

    response = client.get("/health/live")
    assert response.status_code == 200, f"Unexpected status code. Expected: 200, Actual: {response.status_code}"
    assert response.get_json()["status"] == "ok", (f"Unexpected status. Expected: 'ok',"
                                                   f"Actual: {response.get_json()['status']}")

def test_db_is_ready(app: Flask) -> None:
    """asserting DB is working and connected the Flask app"""
    client = app.test_client()
    with patch("menu_translator.services.health_service.check_database_readiness", return_value=True):
        response = client.get("/health/ready")

    assert response.status_code == 200, f"Unexpected status code. Expected: 200, Actual: {response.status_code}"
    assert response.get_json()["status"] == "ready", (f"Unexpected status. Expected: 'ready',"
                                                   f"Actual: {response.get_json()['status']}")


