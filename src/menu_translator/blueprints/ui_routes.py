"""routes for the simple browser user interface"""

import requests

from flask import Blueprint, render_template, request, redirect, url_for
from requests.exceptions import JSONDecodeError

from menu_translator.services import translate_service


ui_bp = Blueprint("ui", __name__)


def get_api_url(path: str) -> str:
    """create a url to this application's rest api"""

    return f"http://127.0.0.1:5000{path}"


def get_error_message(response: requests.Response) -> str:
    """return a readable message from an api error response"""

    try:
        body = response.json()

        if body.get("detail"):
            return body["detail"]

        if body.get("error"):
            return body["error"]

        return f"request failed with status {response.status_code}"

    except JSONDecodeError:
        return f"request failed with status {response.status_code}"


@ui_bp.get("/")
def restaurants_page():
    """display restaurant management page"""

    message = request.args.get("message")
    action = request.args.get("action")
    restaurant_id = request.args.get("restaurant_id")

    restaurants = None
    selected_restaurant = None

    if action == "get_all":

        response = requests.get(
            get_api_url("/api/v1/restaurants")
        )

        if response.ok:
            restaurants = response.json()
        else:
            message = get_error_message(response)

    if action == "get_one" and restaurant_id:

        response = requests.get(
            get_api_url(
                f"/api/v1/restaurants/{restaurant_id}"
            )
        )

        if response.ok:
            selected_restaurant = response.json()
        else:
            message = get_error_message(response)

    live_response = requests.get(
        get_api_url("/health/live")
    )

    ready_response = requests.get(
        get_api_url("/health/ready")
    )

    live_status = "ok" if live_response.ok else "error"
    ready_status = "ok" if ready_response.ok else "error"

    return render_template(
        "restaurants.html",
        restaurants=restaurants,
        selected_restaurant=selected_restaurant,
        searched_restaurant_id=restaurant_id,
        live_status=live_status,
        ready_status=ready_status,
        message=message
    )


@ui_bp.post("/ui/restaurants/create")
def create_restaurant():
    """create a restaurant using the rest api"""

    payload = {
        "name": request.form.get("name"),
        "cuisine_type": request.form.get("cuisine_type"),
        "default_menu_language": request.form.get(
            "default_menu_language"
        )
    }

    response = requests.post(
        get_api_url("/api/v1/restaurants"),
        json=payload
    )

    if response.ok:
        message = "Restaurant created successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.restaurants_page",
            message=message
        )
    )


@ui_bp.post("/ui/restaurants/update")
def update_restaurant():
    """update a restaurant using the rest api"""

    restaurant_id = request.form.get("restaurant_id")

    payload = {
        "name": request.form.get("name"),
        "cuisine_type": request.form.get("cuisine_type"),
        "default_menu_language": request.form.get(
            "default_menu_language"
        )
    }

    response = requests.put(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Restaurant updated successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.restaurants_page",
            message=message
        )
    )


@ui_bp.post("/ui/restaurants/delete")
def delete_restaurant():
    """delete a restaurant using the rest api"""

    restaurant_id = request.form.get("restaurant_id")

    payload = {
        "restaurant_id": restaurant_id
    }

    response = requests.delete(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Restaurant deleted successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.restaurants_page",
            message=message
        )
    )


@ui_bp.get("/restaurants/<int:restaurant_id>/menu-items")
def menu_items_page(restaurant_id: int):
    """display menu item management page"""

    message = request.args.get("message")

    language = request.args.get("lang")
    category = request.args.get("category")
    name = request.args.get("name")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort = request.args.get("sort")

    restaurant_response = requests.get(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}"
        )
    )

    if restaurant_response.ok:
        restaurant = restaurant_response.json()
    else:
        restaurant = None
        message = get_error_message(restaurant_response)

    params = {}

    if category:
        params["category"] = category

    if name:
        params["name"] = name

    if min_price:
        params["min_price"] = min_price

    if max_price:
        params["max_price"] = max_price

    if sort:
        params["sort"] = sort

    original_response = requests.get(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}/menu_items"
        ),
        params=params
    )

    if original_response.ok:
        original_items = original_response.json()
    else:
        original_items = []
        message = get_error_message(original_response)

    if language:

        translated_params = params.copy()
        translated_params["lang"] = language

        translated_response = requests.get(
            get_api_url(
                f"/api/v1/restaurants/{restaurant_id}/menu_items"
            ),
            params=translated_params
        )

        if translated_response.ok:
            display_items = translated_response.json()
        else:
            display_items = original_items
            message = get_error_message(translated_response)

    else:
        display_items = original_items

    original_by_id = {
        item["id"]: item
        for item in original_items
    }

    menu_items = []

    for item in display_items:

        original_item = original_by_id.get(
            item["id"],
            item
        )

        menu_items.append(
            {
                "display": item,
                "original": original_item
            }
        )

    languages = translate_service.get_supported_languages()

    return render_template(
        "menu_items.html",
        restaurant=restaurant,
        restaurant_id=restaurant_id,
        menu_items=menu_items,
        languages=languages,
        message=message,
        selected_language=language,
        selected_category=category,
        selected_name=name,
        selected_min_price=min_price,
        selected_max_price=max_price,
        selected_sort=sort,
        candidates=None
    )


@ui_bp.post("/ui/menu-items/create")
def create_menu_item():
    """create a menu item using the rest api"""

    restaurant_id = request.form.get("restaurant_id")

    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "price": request.form.get("price"),
        "category": request.form.get("category")
    }

    response = requests.post(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}/menu_items"
        ),
        json=payload
    )

    if response.ok:
        message = "Menu item created successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.menu_items_page",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-items/update")
def update_menu_item():
    """update a menu item using the rest api"""

    restaurant_id = request.form.get("restaurant_id")
    menu_item_id = request.form.get("menu_item_id")

    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "price": request.form.get("price"),
        "category": request.form.get("category")
    }

    response = requests.put(
        get_api_url(
            f"/api/v1/restaurants/"
            f"{restaurant_id}/menu_items/{menu_item_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Menu item updated successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.menu_items_page",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-items/delete")
def delete_menu_item():
    """delete a menu item using the rest api"""

    restaurant_id = request.form.get("restaurant_id")
    menu_item_id = request.form.get("menu_item_id")

    payload = {
        "menu_item_id": menu_item_id
    }

    response = requests.delete(
        get_api_url(
            f"/api/v1/restaurants/"
            f"{restaurant_id}/menu_items/{menu_item_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Menu item deleted successfully"
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.menu_items_page",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-import")
def import_menu():
    """upload a menu image using the rest api"""

    restaurant_id = request.form.get("restaurant_id")
    uploaded_file = request.files.get("file")

    files = {
        "file": (
            uploaded_file.filename,
            uploaded_file.read(),
            uploaded_file.mimetype
        )
    }

    response = requests.post(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}/menu-import"
        ),
        files=files
    )

    restaurant_response = requests.get(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}"
        )
    )

    menu_response = requests.get(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}/menu_items"
        )
    )

    restaurant = (
        restaurant_response.json()
        if restaurant_response.ok
        else None
    )

    original_items = (
        menu_response.json()
        if menu_response.ok
        else []
    )

    menu_items = []

    for item in original_items:

        menu_items.append(
            {
                "display": item,
                "original": item
            }
        )

    languages = translate_service.get_supported_languages()

    if response.ok:

        result = response.json()

        candidates = result.get(
            "candidates",
            []
        )

        message = result.get(
            "status",
            "Menu image processed"
        )

    else:

        candidates = []
        message = get_error_message(response)

    return render_template(
        "menu_items.html",
        restaurant=restaurant,
        restaurant_id=restaurant_id,
        menu_items=menu_items,
        languages=languages,
        message=message,
        candidates=candidates,
        selected_language=None,
        selected_category=None,
        selected_name=None,
        selected_min_price=None,
        selected_max_price=None,
        selected_sort=None
    )