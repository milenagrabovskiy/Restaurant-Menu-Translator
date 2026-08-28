from flask import Blueprint, jsonify, request

# from menu_translator.services.restaurant_service import find_restaurant_by_id
from menu_translator.services.responses import single_response_wrapper, list_response_wrapper
from menu_translator.services import menu_item_service
from menu_translator.services import restaurant_service

menu_item_bp = Blueprint("menu_item", __name__)


"""Menu Item Management
Add Menu Item:
Restaurant staff should be able to add a menu item by specifying a name, description, price,
and category (Literal["appetizer", "entree", "dessert", "beverage"]), written in the restaurant's own language.
"""

@menu_item_bp.post("/<int:restaurant_id>/menu_items")
def create_menu_item(restaurant_id: int):

    body = request.get_json() or {}
    return single_response_wrapper(menu_item_service.create_new_menu_item(restaurant_id, body)), 201




"""View Menu:
Provide an endpoint listing all menu items for a restaurant,
**TODO: with filter support by category.
Support an optional ?lang= query parameter that returns the name/description translated into the requested language on the fly.
"""
# @menu_item_bp.get("/<int:restaurant_id>/menu_items")
# def get_menu_items_by_restaurant(restaurant_id: int):
#     return list_response_wrapper(find_menu_items_for_restaurant(restaurant_id))

@menu_item_bp.get("/<int:restaurant_id>/menu_items")
def get_menu_items_by_restaurant(restaurant_id: int):

    category = request.args.get("category")
    return list_response_wrapper(menu_item_service.get_menu_items(restaurant_id, category))


@menu_item_bp.get("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def get_menu_item(restaurant_id: int, menu_item_id: int):
    menu_item = menu_item_service.find_menu_item_by_id(restaurant_id, menu_item_id)

    return single_response_wrapper(menu_item)


"""Edit Menu Item:
Allow updating an item's name, description, price, or category.
Decide (and document in your README) whether an edited name/description re-runs language detection.
"""
@menu_item_bp.put("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def update_menu_item(restaurant_id: int, menu_item_id: int):
    body = request.get_json() or {}
    return single_response_wrapper(menu_item_service.update_existing_menu_item(restaurant_id, menu_item_id, body))


"""Delete Menu Item:
Implement deletion with a confirmation requirement (such as requiring the item id in the request body).
"""
@menu_item_bp.delete("/<int:restaurant_id>/menu_items/<int:menu_item_id>")
def delete_menu_item(restaurant_id: int, menu_item_id: int):

    body = request.get_json() or {}

    menu_item_service.remove_menu_item(restaurant_id, menu_item_id, body)
    return jsonify(status="deleted"), 204


"""Upload Menu Photo for Bulk Import:
Accept a multipart/form-data upload of a photographed menu page (JPG or PNG) tied to a restaurant.
Store the raw image in S3 and return a list of candidate menu items extracted from it for staff to review
— extracted items are not saved automatically (see AI-Assisted Feature below).
"""