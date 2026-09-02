"""Restaurant ORM"""
from menu_translator.extensions import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RestaurantRecord(db.Model):
    """Restaurant Record pydantic model representing table in the database"""
    __tablename__ = "restaurant"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cuisine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    default_menu_language: Mapped[str] = mapped_column(String(20), nullable=False)

    # this is not a column!
    menu_items: Mapped[list["MenuItemRecord"]] = (relationship
                                                  ("MenuItemRecord",
                                                   back_populates="restaurant",
                                                   cascade="all, delete-orphan")  # if a restaurant is deleted, all of its menu items are deleted as well
                                                  )
    @property
    def menu_item_count(self):
        """returns the count of menu items for a restaurant"""
        return len(self.menu_items)