"""Blueprint controller for endpoints pertaining to menu items"""
from flask import Blueprint, request, Response, jsonify

# from menu_translator.services.restaurant_service import find_restaurant_by_id
from menu_translator.responses import single_response_wrapper, list_response_wrapper
from menu_translator.services import menu_item_service
from menu_translator.services import menu_image_service

menu_item_bp = Blueprint("menu_item", __name__)



@menu_item_bp.post("/<int:restaurant_id>/menu_items")
def create_menu_item(restaurant_id: int)-> tuple[Response, int]:
    """creates a new menu item"""

    body = request.get_json() or {}
    return single_response_wrapper(menu_item_service.create_new_menu_item(restaurant_id, body)), 201



@menu_item_bp.get("/<int:restaurant_id>/menu_items")
def get_menu_items_by_restaurant(restaurant_id: int) -> Response:
    """fetches menu items for a given restaurant. Optionally filters based on given query parameters"""

    category = request.args.get("category")
    lang = request.args.get("lang")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    name = request.args.get("name")
    sort = request.args.get("sort")


    menu_items = menu_item_service.get_menu_items(restaurant_id=restaurant_id,
                                                  category=category,
                                                  lang=lang,
                                                  min_price=min_price,
                                                  max_price=max_price,
                                                  name=name,
                                                  sort=sort)

    return list_response_wrapper(menu_items)


@menu_item_bp.get("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def get_menu_item(restaurant_id: int, menu_item_id: int) -> Response:
    """fetches a menu item for a restaurant"""
    menu_item = menu_item_service.find_menu_item_by_id(restaurant_id, menu_item_id)

    return single_response_wrapper(menu_item)


@menu_item_bp.put("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def update_menu_item(restaurant_id: int, menu_item_id: int) -> Response:
    """updates an existing menu item for a restaurant"""
    body = request.get_json() or {}
    return single_response_wrapper(menu_item_service.update_existing_menu_item(restaurant_id, menu_item_id, body))


@menu_item_bp.delete("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def delete_menu_item(restaurant_id: int, menu_item_id: int)-> tuple[str, int]:
    """deletes an existing menu item"""

    body = request.get_json() or {}

    menu_item_service.remove_menu_item(restaurant_id, menu_item_id, body)
    return "", 204


@menu_item_bp.post("/<int:restaurant_id>/menu-import")
def import_menu(restaurant_id: int) -> tuple[Response, int]:
    """uploads a menu image and returns menu item candidates extracted from it"""
    file = request.files.get("file")

    result = menu_image_service.import_menu_image(restaurant_id, file)

    return jsonify(result), 201
