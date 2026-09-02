"""Restaurant service layer for orchestrating business logic"""

from menu_translator.stores import restaurant_store
from menu_translator.models.restaurant import Restaurant, DeleteRestaurantDto
from menu_translator.errors import RestaurantManagementError

def get_all_restaurants() -> list[Restaurant]:
    """returns all restaurants"""
    return restaurant_store.get_all_restaurants()


def find_restaurant_by_id(restaurant_id: int) -> Restaurant:
    """returns a restaurant by its id"""
    restaurant = restaurant_store.find_restaurant_by_id(restaurant_id)
    if restaurant is None:
        raise RestaurantManagementError(code="Restaurant not found", status=404, detail=f"Restaurant with id:"
                                                                                        f"{restaurant_id} not found")
    return restaurant


def create_new_restaurant(restaurant_data: dict) -> Restaurant:
    """creates a new restaurant if it does not already exist"""
    if restaurant_store.restaurant_exists(restaurant_data["name"],
                                          restaurant_data["cuisine_type"],
                                          restaurant_data["default_menu_language"]):
        raise RestaurantManagementError(
            code="restaurant_already_exists",
            status=409,
            detail="Restaurant with given data already exists"
        )

    return restaurant_store.create_new_restaurant(restaurant_data)




def update_existing_restaurant(restaurant_id: int, restaurant_data: dict) -> Restaurant:
    """updates an existing restaurant"""

    restaurant = restaurant_store.find_restaurant_by_id(restaurant_id)  # first, check if restaurant exists
    if restaurant is None:
        raise RestaurantManagementError(
            code="not_found",
            status=404,
            detail=f"Restaurant with id: {restaurant_id} not found."
        )

    return restaurant_store.update_existing_restaurant(restaurant_id, restaurant_data)


def delete_restaurant(restaurant_id: int, restaurant_data: dict) -> None:
    """validates deletion confirmation and deletes a restaurant"""

    delete_dto = DeleteRestaurantDto.model_validate(restaurant_data)

    if delete_dto.restaurant_id != restaurant_id:
        raise RestaurantManagementError(code="confirmation_mismatch", status=409, detail="Restaurant id in body does not match url")

    # cascades deletions (deletes associated menus/items)
    deleted = restaurant_store.delete_restaurant(restaurant_id)
    if not deleted:
        raise RestaurantManagementError(
            code="not_found",
            status=404,
            detail=f"Restaurant with id: {restaurant_id} not found."
        )