
from typing import Literal
from pydantic import BaseModel, Field

# make some kind of validation using ai to make sure language is actual language?


class Restaurant(BaseModel):

    id: int
    name: str = Field(min_length=3)
    cuisine_type: str = Field()
    default_menu_language: str
