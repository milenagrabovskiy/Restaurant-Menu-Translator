"""Menu item service layer for orchestrating business logic."""

from menu_translator.stores import menu_item_store
from menu_translator.models.menu_item import MenuItem, CreateMenuItemDto, UpdateMenuItemDto, DeleteMenuItemDto
from menu_translator.services.responses import RestaurantManagementError


def get_menu_items(restaurant_id: int) -> list[MenuItem]:

    return menu_item_store.find_menu_items_for_restaurant(restaurant_id)



def find_menu_item_by_id(restaurant_id: int, menu_item_id: int) -> MenuItem:

    menu_item = menu_item_store.find_menu_item_by_id(restaurant_id, menu_item_id)

    if menu_item is None:
        raise RestaurantManagementError(code="not_found", status=404, detail=f"Menu item with id: {menu_item_id} not found.")

    return menu_item



def create_new_menu_item(restaurant_id: int, menu_item_data: dict) -> MenuItem:

    create_dto = CreateMenuItemDto.model_validate(menu_item_data)

    return menu_item_store.create_new_menu_item(restaurant_id, create_dto)



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