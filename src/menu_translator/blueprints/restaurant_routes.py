from flask import Blueprint, jsonify, request

from menu_translator.responses import list_response_wrapper, single_response_wrapper
from menu_translator.services import restaurant_service

restaurants_bp = Blueprint("restaurants", __name__)


@restaurants_bp.get("")
def get_restaurants():
    return list_response_wrapper(restaurant_service.get_all_restaurants())


@restaurants_bp.get("/<int:restaurant_id>")
def get_restaurant_by_id(restaurant_id):
    restaurant = restaurant_service.find_restaurant_by_id(restaurant_id)
    return single_response_wrapper(restaurant)


@restaurants_bp.post("")
def create_restaurant():
    body = request.get_json()

    return single_response_wrapper(restaurant_service.create_new_restaurant(body)), 201


@restaurants_bp.put("/<int:restaurant_id>")
def update_restaurant(restaurant_id):
    body = request.get_json()
    return single_response_wrapper(restaurant_service.update_existing_restaurant(restaurant_id, body))


@restaurants_bp.delete("/<int:restaurant_id>")
def delete_restaurant(restaurant_id):

    body = request.get_json()
    restaurant_service.delete_restaurant(restaurant_id, body)
    # return "", 204 means no content(no json)
    return "", 204
