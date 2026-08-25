from flask import Blueprint, jsonify

# from menu_translator.services.restaurant_service import find_restaurant_by_id
from menu_translator.services.envelopes import single_envelope

menu_item_bp = Blueprint("menu_item", __name__)


"""Menu Item Management
Add Menu Item:
Restaurant staff should be able to add a menu item by specifying a name, description, price,
and category (Literal["appetizer", "entree", "dessert", "beverage"]), written in the restaurant's own language.
"""




"""View Menu:
Provide an endpoint listing all menu items for a restaurant, with filter support by category.
Support an optional ?lang= query parameter that returns the name/description translated into the requested language on the fly.
"""
# @menu_item_bp.get("/<int:restaurant_id>")
# def get_menu_items(restaurant_id):
#     if not restaurant_id:
#         return jsonify({"error": "Restaurant not found"}), 404
#
#     return single_envelope(find_restaurant_by_id(restaurant_id))



"""Edit Menu Item:
Allow updating an item's name, description, price, or category.
Decide (and document in your README) whether an edited name/description re-runs language detection.
"""

"""Delete Menu Item:
Implement deletion with a confirmation requirement (such as requiring the item id in the request body).
"""

"""Upload Menu Photo for Bulk Import:
Accept a multipart/form-data upload of a photographed menu page (JPG or PNG) tied to a restaurant.
Store the raw image in S3 and return a list of candidate menu items extracted from it for staff to review
— extracted items are not saved automatically (see AI-Assisted Feature below).
"""