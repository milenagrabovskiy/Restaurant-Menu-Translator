from typing import Literal
from pydantic import BaseModel, Field


Category = Literal["appetizer", "entree", "dessert", "beverage"]  # should be written in restaurant's own lang, convert? call AWS Translate




class MenuItem(BaseModel):

    id: int
    restaurant_id: int
    name: str = Field(min_length=3)
    description: str = Field(min_length=8)
    detected_source_language: str
    price: float = Field(gt=0)
    category: Category
