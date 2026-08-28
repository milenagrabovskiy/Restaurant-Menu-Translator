
from typing import Literal


from pydantic import BaseModel, Field, ConfigDict

# make some kind of validation using ai to make sure language is actual language?


class Restaurant(BaseModel):

    model_config = {"from_attributes": True}

    id: int
    name: str = Field(min_length=3)
    cuisine_type: str = Field()
    default_menu_language: str = Field(min_length=2)
    menu_item_count: int



class UpdateRestaurantDto(BaseModel):

    model_config = ConfigDict(extra="forbid")
    # can send just part of payload
    name: str | None = Field(min_length=3)
    cuisine_type: str | None = Field()
    default_menu_language: str | None = Field(default=None, min_length=2)


class CreateRestaurantDto(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2)
    cuisine_type: str = Field(min_length=2)
    default_menu_language: str = Field(min_length=2)


class DeleteRestaurantDto(BaseModel):
    restaurant_id: int