"""restaurant store layer for database operations"""
from sqlalchemy import select

from menu_translator.models.db_models.restaurant_orm import RestaurantRecord
from menu_translator.models.restaurant import Restaurant, UpdateRestaurantDto, CreateRestaurantDto
from menu_translator.extensions import db

def get_all_restaurants() -> list[Restaurant]:
    """returns all restaurants from the database"""
    stmt = select(RestaurantRecord).order_by(RestaurantRecord.id)
    records = db.session.scalars(stmt).all()

    return [Restaurant.model_validate(record) for record in records]



def find_restaurant_by_id(restaurant_id: int) -> Restaurant | None:
    """returns a restaurant by its id"""
    record = db.session.get(RestaurantRecord, restaurant_id)

    return Restaurant.model_validate(record) if record else None



def find_restaurant_by_name(name: str) -> Restaurant | None:
    """returns a restaurant by its name"""

    stmt = select(RestaurantRecord).where(RestaurantRecord.name == name)
    record = db.session.scalar(stmt)

    return Restaurant.model_validate(record) if record else None



def delete_restaurant(restaurant_id: int) -> bool:
    """deletes a restaurant by its id"""
    record = db.session.get(RestaurantRecord, restaurant_id)
    if record is not None:
        db.session.delete(record)
        db.session.commit()
        return True
    return False



def update_existing_restaurant(restaurant_id: int, restaurant_data: dict) -> Restaurant | None:
    """updates an existing restaurant"""
    record = db.session.get(RestaurantRecord, restaurant_id)
    if record is None:
        return None

    updated_restaurant = UpdateRestaurantDto.model_validate(restaurant_data)

    for key, value in updated_restaurant.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    db.session.commit()

    return Restaurant.model_validate(record)


def create_new_restaurant(restaurant_data: dict) -> Restaurant:
    """creates and saves a new restaurant"""
    new_restaurant = CreateRestaurantDto.model_validate(restaurant_data)
    record = RestaurantRecord(**new_restaurant.model_dump())
    db.session.add(record)
    db.session.commit()

    return Restaurant.model_validate(record)



def restaurant_exists(name: str, cuisine_type: str, default_menu_language: str) -> bool:
    """checks if a restaurant with the given data already exists"""
    stmt = select(RestaurantRecord.id).where(
        RestaurantRecord.name==name,
        RestaurantRecord.cuisine_type == cuisine_type,
        RestaurantRecord.default_menu_language == default_menu_language
    )

    return db.session.scalar(stmt) is not None
