"""Menu item service layer for orchestrating business logic."""
from botocore.exceptions import BotoCoreError, ClientError

from menu_translator.ai.comprehend import detect_language
from menu_translator.models.db_models.menu_item_orm import MenuItemRecord
from menu_translator.stores import menu_item_store
from menu_translator.ai.translate import translate
from menu_translator.services import restaurant_service
from menu_translator.models.menu_item import (MenuItem, CreateMenuItemDto,
                                              UpdateMenuItemDto, DeleteMenuItemDto, CategoryAdapter)
from menu_translator.errors import RestaurantManagementError, AWSError

MIN_CONFIDENCE_SCORE = 0.70
VALID_SORT_QUERY = {"price_asc", "price_desc", "name_asc", "name_desc"}


def get_menu_items(restaurant_id: int,
                   category: str | None = None,
                   lang: str | None = None,
                   min_price: float | None = None,
                   max_price: float | None = None,
                   name: str | None = None,
                   sort: str | None = None
                   ) -> list[MenuItem]:
    """return menu items for a restaurant with optional filtering, sorting, and translation"""

    if not restaurant_service.find_restaurant_by_id(restaurant_id):
        raise RestaurantManagementError(code="Restaurant_not_found",
                                        status=404,
                                        detail=f"Restaurant with id: {restaurant_id} does not exist")

    if category is not None:
        category = CategoryAdapter.validate_python(category)


    if min_price is not None and max_price is not None and min_price > max_price:
        raise RestaurantManagementError(code="invalid_query_params",
                                        status=422,
                                        detail="min price must be lower than max price") # i should create better error class

    if sort is not None and sort not in VALID_SORT_QUERY:
        raise RestaurantManagementError(code="invalid_query_params",
                                        status=422,
                                        detail=f"sort must be one of these: {VALID_SORT_QUERY}")

    menu_items = menu_item_store.find_menu_items_for_restaurant(restaurant_id,
                                                                category,
                                                                min_price,
                                                                max_price,
                                                                name,
                                                                sort)

    if lang is None:
        return menu_items

    translated_results = []
    for item in menu_items:
        item_data = item.model_dump()
        source_lang = item.detected_source_language

        if lang.lower() == source_lang.lower():
            translated_results.append(item)
            continue

        try: # 2 calls
            name_response = translate(item.name, source_lang, lang)
            description_response = translate(item.description, source_lang, lang)

        except (BotoCoreError, ClientError) as e:
            raise AWSError(code="translation_failed", status=502, detail="menu item translation failed") from e

        item_data["name"] = name_response["translated_text"]
        item_data["translated_language"] = lang
        item_data["description"] = description_response["translated_text"]

        translated_results.append(MenuItem.model_validate(item_data))

    return translated_results



def find_menu_item_by_id(restaurant_id: int, menu_item_id: int) -> MenuItem:
    """return a menu item by its id and restaurant id"""

    menu_item = menu_item_store.find_menu_item_by_id(restaurant_id, menu_item_id)

    if menu_item is None:
        raise RestaurantManagementError(code="not_found", status=404, detail=f"Menu item with id: {menu_item_id} not found.")

    return menu_item



def create_new_menu_item(restaurant_id: int, menu_item_data: dict) -> MenuItem:
    """validate and create a new menu item with its detected source language"""
    create_dto = CreateMenuItemDto.model_validate(menu_item_data)

    restaurant = restaurant_service.find_restaurant_by_id(restaurant_id)

    text = f"{create_dto.name} {create_dto.description}"
    try:
        detected_lang, confidence_score = detect_language(text)
    except (BotoCoreError, ClientError) as e:
        raise AWSError(code="language_detection_failed",
                       status=502,
                       detail="language detection not working") from e

    if detected_lang is None or confidence_score < MIN_CONFIDENCE_SCORE:
        detected_lang = restaurant.default_menu_language


    record = MenuItemRecord(
        restaurant_id=restaurant_id,
        detected_source_language=detected_lang,
        **create_dto.model_dump()
    )

    return menu_item_store.create_new_menu_item(record)




def update_existing_menu_item(restaurant_id: int, menu_item_id: int, menu_item_data: dict) -> MenuItem:
    """validate and update an existing menu item and re-detect its source language"""

    update_dto = UpdateMenuItemDto.model_validate(menu_item_data)

    restaurant = restaurant_service.find_restaurant_by_id(restaurant_id)

    text = f"{update_dto.name} {update_dto.description}"

    try:
        detected_lang, confidence_score = detect_language(text)
    except (BotoCoreError, ClientError) as e:
        raise AWSError(code="language_detection_failed", status=502, detail="language detection not working")

    if detected_lang is None or confidence_score < MIN_CONFIDENCE_SCORE:
        detected_lang = restaurant.default_menu_language

    update_data = update_dto.model_dump()
    update_data["detected_source_language"] = detected_lang

    menu_item = menu_item_store.update_existing_menu_item(restaurant_id, menu_item_id, update_data)

    if menu_item is None:
        raise RestaurantManagementError(code="not_found", status=404, detail=f"Menu item with id: {menu_item_id} not found.")

    return menu_item



def remove_menu_item(restaurant_id: int, menu_item_id: int, menu_item_data: dict) -> None:
    """validate the deletion confirmation and remove a menu item"""


    delete_dto = DeleteMenuItemDto.model_validate(menu_item_data)

    if delete_dto.menu_item_id != menu_item_id:

        raise RestaurantManagementError(code="confirmation_mismatch", status=409, detail="Menu Item id in body does not match URL")


    deleted = menu_item_store.remove_menu_item(
        restaurant_id,
        menu_item_id
    )

    if not deleted:
        raise RestaurantManagementError(
            code="not_found",
            status=404,
            detail=f"Menu item with id: {menu_item_id} not found."
        )