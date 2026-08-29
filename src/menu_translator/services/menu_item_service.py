"""Menu item service layer for orchestrating business logic."""
from botocore.exceptions import BotoCoreError

from menu_translator.ai.comprehend import detect_language
from menu_translator.models.db_models.menu_item_orm import MenuItemRecord
from menu_translator.stores import menu_item_store
from menu_translator.ai.translate import translate
from menu_translator.services import restaurant_service
from menu_translator.models.menu_item import (MenuItem, CreateMenuItemDto,
                                              UpdateMenuItemDto, DeleteMenuItemDto, CategoryAdapter)
from menu_translator.errors import RestaurantManagementError, AWSError

MIN_CONFIDENCE_SCORE = 0.70


def get_menu_items(restaurant_id: int,
                   category: str | None,
                   lang: str | None,
                   min_price: float | None,
                   max_price: float | None
                   ) -> list[dict|MenuItem]:

    if category is not None:
        category = CategoryAdapter.validate_python(category)


    if min_price is not None and max_price is not None and min_price > max_price:
        raise RestaurantManagementError("invalid_query_params",
                                        422,
                                        "min price must be lower than max price")

    menu_items = menu_item_store.find_menu_items_for_restaurant(restaurant_id,
                                                                category,
                                                                min_price,
                                                                max_price)

    if lang is None:
        return menu_items

    translated_results = []
    for item in menu_items:
        item_data = item.model_dump()
        source_lang = item.detected_source_language

        if lang.lower() == source_lang.lower():
            translated_results.append(item)
            continue

        try:
            name_response = translate(item.name, source_lang, lang)
            description_response = translate(item.description, source_lang, lang)

        except BotoCoreError as e:
            raise AWSError(code="translation_failed", status=502, detail="menu item translation failed") from e

        item_data["name"] = name_response["translated_text"]
        item_data["translated_language"] = lang
        item_data["description"] = description_response["translated_text"]

        translated_results.append(MenuItem.model_validate(item_data))

    return translated_results



def find_menu_item_by_id(restaurant_id: int, menu_item_id: int) -> MenuItem:

    menu_item = menu_item_store.find_menu_item_by_id(restaurant_id, menu_item_id)

    if menu_item is None:
        raise RestaurantManagementError(code="not_found", status=404, detail=f"Menu item with id: {menu_item_id} not found.")

    return menu_item



def create_new_menu_item(restaurant_id: int, menu_item_data: dict) -> MenuItem:

    create_dto = CreateMenuItemDto.model_validate(menu_item_data)

    restaurant = restaurant_service.find_restaurant_by_id(restaurant_id)

    text = f"{create_dto.name} {create_dto.description}"

    detected_lang, confidence_score = detect_language(text)

    if detected_lang is None or confidence_score < MIN_CONFIDENCE_SCORE:
        detected_lang = restaurant.default_menu_language


    record = MenuItemRecord(
        restaurant_id=restaurant_id,
        detected_source_language=detected_lang,
        **create_dto.model_dump()
    )

    return menu_item_store.create_new_menu_item(record)




def update_existing_menu_item(restaurant_id: int, menu_item_id: int, menu_item_data: dict) -> MenuItem:

    update_dto = UpdateMenuItemDto.model_validate(menu_item_data)

    menu_item = menu_item_store.update_existing_menu_item(restaurant_id, menu_item_id, update_dto)

    if menu_item is None:
        raise RestaurantManagementError(code="not_found", status=404, detail=f"Menu item with id: {menu_item_id} not found.")

    return menu_item



def remove_menu_item(restaurant_id: int, menu_item_id: int, menu_item_data: dict) -> None:

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