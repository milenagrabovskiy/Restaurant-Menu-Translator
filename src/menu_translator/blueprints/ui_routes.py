"""Routes for the simple browser user interface."""

import requests

from flask import Blueprint, render_template, request, redirect, url_for

from menu_translator.services import translate_service


ui_bp = Blueprint("ui", __name__)


def get_api_url(path: str) -> str:
    """Create a URL to this application's REST API."""
    return f"http://127.0.0.1:5000{path}"


def get_error_message(response: requests.Response) -> str:
    """return a readable message from an API error response."""

    try:
        body = response.json()

        if "detail" in body:
            return body["detail"]

        if "error" in body:
            return str(body["error"])

        return str(body)

    except ValueError:
        return f"Request failed with status {response.status_code}"


@ui_bp.get("/")
def home():
    """Display restaurants and optionally a restaurant menu."""

    message = request.args.get("message")

    restaurant_id = request.args.get("restaurant_id")
    language = request.args.get("language")
    category = request.args.get("category")
    sort = request.args.get("sort")

    # Get all restaurants using the REST API
    restaurant_response = requests.get(
        get_api_url("/api/v1/restaurants")
    )

    if restaurant_response.ok:
        restaurants = restaurant_response.json()
    else:
        restaurants = []

    # Get supported Amazon Translate languages
    languages = translate_service.get_supported_languages()

    menu_items = None

    if restaurant_id:

        params = {}

        if language:
            params["lang"] = language

        if category:
            params["category"] = category

        if sort:
            params["sort"] = sort

        menu_response = requests.get(
            get_api_url(
                f"/api/v1/restaurants/{restaurant_id}/menu_items"
            ),
            params=params
        )

        if menu_response.ok:
            menu_items = menu_response.json()
        else:
            message = get_error_message(menu_response)

    return render_template(
        "index.html",
        restaurants=restaurants,
        menu_items=menu_items,
        languages=languages,
        selected_restaurant_id=restaurant_id,
        selected_language=language,
        message=message,
        candidates=None
    )


@ui_bp.post("/ui/restaurants/create")
def create_restaurant():
    """Create a restaurant using the REST API."""

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
        message = "Restaurant created successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for("ui.home", message=message)
    )


@ui_bp.post("/ui/restaurants/update")
def update_restaurant():
    """Update a restaurant using the REST API."""

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
        message = "Restaurant updated successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.home",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/restaurants/delete")
def delete_restaurant():
    """Delete a restaurant using the REST API."""

    restaurant_id = request.form.get("restaurant_id")

    payload = {
        "restaurant_id": int(restaurant_id)
    }

    response = requests.delete(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Restaurant deleted successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for("ui.home", message=message)
    )


@ui_bp.post("/ui/menu-items/create")
def create_menu_item():
    """Create a menu item using the rest api."""

    restaurant_id = request.form.get("restaurant_id")

    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "price": float(request.form.get("price")),
        "category": request.form.get("category")
    }

    response = requests.post(
        get_api_url(
            f"/api/v1/restaurants/{restaurant_id}/menu_items"
        ),
        json=payload
    )

    if response.ok:
        message = "Menu item created successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.home",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-items/update")
def update_menu_item():
    """Update a menu item using the rest api."""

    restaurant_id = request.form.get("restaurant_id")
    menu_item_id = request.form.get("menu_item_id")

    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "price": float(request.form.get("price")),
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
        message = "Menu item updated successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.home",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-items/delete")
def delete_menu_item():
    """Delete a menu item using the rest api"""

    restaurant_id = request.form.get("restaurant_id")
    menu_item_id = request.form.get("menu_item_id")

    payload = {
        "menu_item_id": int(menu_item_id)
    }

    response = requests.delete(
        get_api_url(
            f"/api/v1/restaurants/"
            f"{restaurant_id}/menu_items/{menu_item_id}"
        ),
        json=payload
    )

    if response.ok:
        message = "Menu item deleted successfully."
    else:
        message = get_error_message(response)

    return redirect(
        url_for(
            "ui.home",
            restaurant_id=restaurant_id,
            message=message
        )
    )


@ui_bp.post("/ui/menu-import")
def import_menu():
    """Upload a menu image using the rest api"""

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
        get_api_url("/api/v1/restaurants")
    )

    restaurants = (
        restaurant_response.json()
        if restaurant_response.ok
        else []
    )

    languages = translate_service.get_supported_languages()

    if response.ok:
        result = response.json()
        candidates = result.get("candidates", [])
        message = result.get("status", "Menu image processed.")
    else:
        candidates = []
        message = get_error_message(response)

    return render_template(
        "index.html",
        restaurants=restaurants,
        menu_items=None,
        languages=languages,
        selected_restaurant_id=restaurant_id,
        selected_language=None,
        message=message,
        candidates=candidates
    )