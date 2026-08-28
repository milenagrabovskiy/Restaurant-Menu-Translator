from flask import Blueprint, jsonify
from menu_translator.services.health_service import is_live

health_bp = Blueprint("health", __name__)

@health_bp.get("/live")
def live():

    if is_live():
        return jsonify(status="ok")
    return jsonify(status="down"), 500