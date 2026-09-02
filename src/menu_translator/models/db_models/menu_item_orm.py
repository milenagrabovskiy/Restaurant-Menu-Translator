"""ORM for menu item"""
from sqlalchemy import ForeignKey, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal


from menu_translator.extensions import db

class MenuItemRecord(db.Model):
    """ORM that represents a menu item in the DB"""
    __tablename__ = "menu_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detected_source_language: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    restaurant: Mapped["RestaurantRecord"] = relationship("RestaurantRecord", back_populates="menu_items")

