"""menu item service layer for orchestrating business logic"""
from decimal import Decimal

from sqlalchemy import select, func

from menu_translator.models.db_models.menu_item_orm import MenuItemRecord
from menu_translator.models.menu_item import MenuItem, UpdateMenuItemDto, CreateMenuItemDto
from menu_translator.extensions import db


def find_menu_items_for_restaurant(restaurant_id: int,
                                   category:str | None=None,
                                   min_price: float | None=None,
                                   max_price: float | None=None,
                                   name: str | None=None,
                                   sort: str | None=None
                                   ) -> list[MenuItem]:
    """returns menu items for a restaurant with optional filtering sorting and translation"""

    stmt = select(MenuItemRecord).where(MenuItemRecord.restaurant_id == restaurant_id)

    if category is not None:
        stmt = stmt.where(MenuItemRecord.category == category)

    if min_price is not None:
        stmt = stmt.where(MenuItemRecord.price >= Decimal(str(min_price)))

    if max_price is not None:
        stmt = stmt.where(MenuItemRecord.price <= Decimal(str(max_price)))

    if name is not None:
        stmt = stmt.where(MenuItemRecord.name.ilike(f"%{name}%")) # not case sensitve with ilike

    if sort is not None:
        if sort == "name_asc":
            stmt = stmt.order_by(func.lower(MenuItemRecord.name).asc())
        elif sort == "name_desc":
            stmt = stmt.order_by(func.lower(MenuItemRecord.name).desc())
        elif sort == "price_asc":
            stmt = stmt.order_by(MenuItemRecord.price.asc())
        elif sort == "price_desc":
            stmt = stmt.order_by(MenuItemRecord.price.desc())


    records = db.session.scalars(stmt).all()

    return [MenuItem.model_validate(record) for record in records]



def find_menu_item_by_id(restaurant_id: int, menu_item_id: int) -> MenuItem | None:
    """returns a menu item by its id and restaurant id"""
    stmt = select(MenuItemRecord).where(MenuItemRecord.id == menu_item_id,
                                        MenuItemRecord.restaurant_id == restaurant_id)
    record = db.session.scalar(stmt)
    return MenuItem.model_validate(record) if record else None


def create_new_menu_item(record: MenuItemRecord) -> MenuItem:
    """validates and creates a new menu item with its detected source language"""

    db.session.add(record)
    db.session.commit()

    return MenuItem.model_validate(record)


def update_existing_menu_item(restaurant_id: int, menu_item_id: int, update_data: dict) -> MenuItem | None:
    """validates and updates an existing menu item and re-detects its source language"""
    record = db.session.get(MenuItemRecord, menu_item_id)
    if record is None:
        return None

    if record.restaurant_id != restaurant_id:
        return None

    for key, value in update_data.items():
        setattr(record, key, value)

    db.session.commit()
    return MenuItem.model_validate(record)



def remove_menu_item(restaurant_id: int, menu_item_id: int) -> bool:
    """validates deletion confirmation and removes a menu item"""
    record = db.session.get(MenuItemRecord, menu_item_id)

    if record is None:
        return False

    if record.restaurant_id != restaurant_id:
        return False

    db.session.delete(record)
    db.session.commit()

    return True

