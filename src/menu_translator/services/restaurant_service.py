# from menu_translator.models.restaurant import Restaurant


# def _restaurants():
#     restaurants = []
#     for r in RESTAURANTS:
#         Restaurant.model_validate(r)
#         restaurants.append(r)
#     return restaurants
#
# def find_restaurant_by_id(restaurant_id: int) -> Restaurant | None:
#     for r in RESTAURANTS:
#         if r.get("id") == restaurant_id:
#             return Restaurant(**r)  # Convert matching dict to Pydantic model
#     return None
#
