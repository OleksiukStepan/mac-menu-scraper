from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    """Product model representing McDonald's food item nutritional values"""
    name: str
    description: Optional[str]
    calories: Optional[float]
    fats: Optional[float]
    carbs: Optional[float]
    proteins: Optional[float]
    unsaturated_fats: Optional[float]
    sugar: Optional[float]
    salt: Optional[float]
    portion: Optional[float]
