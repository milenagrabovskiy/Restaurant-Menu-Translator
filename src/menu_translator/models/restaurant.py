"""Pydantic models and dtos for Restaurant"""

from pydantic import BaseModel, Field, ConfigDict



class Restaurant(BaseModel):
    """Restaurant Pydantic model"""
    model_config = {"from_attributes": True}

    id: int
    name: str = Field(min_length=3)
    cuisine_type: str = Field()
    default_menu_language: str = Field(min_length=2)
    menu_item_count: int



class UpdateRestaurantDto(BaseModel):
    """DTO for updating a restaurant"""
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(min_length=3)
    cuisine_type: str | None = Field()
    default_menu_language: str | None = Field(default=None, min_length=2)


class CreateRestaurantDto(BaseModel):
    """DTO for creating a restaurant"""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2)
    cuisine_type: str = Field(min_length=2)
    default_menu_language: str = Field(min_length=2)


class DeleteRestaurantDto(BaseModel):
    """DTO for deleting a restaurant"""
    restaurant_id: int