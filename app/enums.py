from enum import Enum


class ProductField(str, Enum):
    description = "description"
    calories = "calories"
    fats = "fats"
    carbs = "carbs"
    proteins = "proteins"
    unsaturated_fats = "unsaturated_fats"
    sugar = "sugar"
    salt = "salt"
    portion = "portion"
