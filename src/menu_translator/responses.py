from flask import jsonify, g

from menu_translator.models.restaurant import Restaurant


def single_response_wrapper(restaurant: Restaurant):
    return jsonify(restaurant.model_dump(mode="json"))


def list_response_wrapper(restaurants: list[Restaurant]):
    return jsonify([restaurant.model_dump(mode="json") for restaurant in restaurants])

#
def error_response(code: str, status: int, detail: str | None):
    return jsonify(error=code, detail=detail, request_id=g.request_id), status