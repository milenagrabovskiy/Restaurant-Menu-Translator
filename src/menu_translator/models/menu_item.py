"""pydantic models and dto definitions for menu items"""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, TypeAdapter


Category = Literal["appetizer", "entree", "dessert", "beverage"]  # should be written in restaurant's own lang, convert? call AWS Translate


CategoryAdapter = TypeAdapter(Category)

class MenuItem(BaseModel):
    """represents a menu item returned by the application"""
    id: int
    restaurant_id: int
    name: str = Field(min_length=3)
    description: str = Field(min_length=8)
    detected_source_language: str
    price: float = Field(gt=0)
    category: Category

    model_config = {"from_attributes": True}



class CreateMenuItemDto(BaseModel):
    """validates data used to create a menu item"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3)
    description: str = Field(min_length=8)
    price: float = Field(gt=0)
    category: Category



class UpdateMenuItemDto(BaseModel):
    """validates data used to update a menu item"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3)
    description: str = Field(min_length=8)
    price: float = Field(gt=0)
    category: Category



class DeleteMenuItemDto(BaseModel):
    """validates menu item deletion confirmation data"""

    model_config = ConfigDict(extra="forbid")

    menu_item_id: int