from menu_translator.extensions import db
from sqlalchemy import ForeignKey, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal


class RestaurantRecord(db.Model):

    __tablename__ = "restaurant"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cuisine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    default_menu_language: Mapped[str] = mapped_column(String(20), nullable=False)

    menu_items: Mapped[list["MenuItemRecord"]] = (relationship
                                                  ("MenuItemRecord",
                                                   back_populates="restaurant",
                                                   cascade="all, delete-orphan")  # if a restaurant is deleted, all of its menu items are deleted as well
                                                  )
