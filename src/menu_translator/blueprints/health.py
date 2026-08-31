
from flask import Blueprint, jsonify
from menu_translator.services import health_service
from menu_translator.responses import error_response

health_bp = Blueprint("health", __name__)

@health_bp.get("/live")
def live():
    """Confirms Flask is running"""
    if health_service.is_live():
        return jsonify(status="ok")
    return jsonify(status="down"), 500


@health_bp.get("/ready")
def readiness_check():
    """Confirms downstream database dependency is reachable."""
    is_ready = health_service.check_database_readiness()

    if is_ready:
        return jsonify({"status": "ready", "database": "connected"}), 200

    return error_response(code="database_unavailable", status=503, detail="Database not reachable")