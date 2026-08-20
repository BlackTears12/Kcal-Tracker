from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from kcal_tracker.data.meal import *

@dataclass
class Ingredient:
    name: str = ""
    macros_per_100g: MacroProfile = field(default_factory=MacroProfile)
    weight_g: float = 0.0

    def __post_init__(self):
        if isinstance(self.macros_per_100g, dict):
            self.macros_per_100g = MacroProfile(**self.macros_per_100g)

    def calories(self) -> float:
        return round(self.macros_per_100g.calories * (self.weight_g / 100.0), 1)

    def protein(self) -> float:
        return round(self.macros_per_100g.protein * (self.weight_g / 100.0), 1)

    def carbs(self) -> float:
        return round(self.macros_per_100g.carbs * (self.weight_g / 100.0), 1)

    def fat(self) -> float:
        return round(self.macros_per_100g.fat * (self.weight_g / 100.0), 1)

    def total_macros(self) -> MacroProfile:
        return MacroProfile(
            calories=self.calories(),
            protein=self.protein(),
            carbs=self.carbs(),
            fat=self.fat(),
        )


@dataclass
class Recipe:
    id: int = 0
    name: str = ""
    ingredients: list[Ingredient] = field(default_factory=list)
    servings: int = 1
    ingredients_text: str = ""
    instructions: str = ""
    # Per-serving macros (calculated from ingredients and servings)
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0

    def __post_init__(self):
        if self.ingredients:
            self.ingredients = [
                Ingredient(**ing) if isinstance(ing, dict) else ing
                for ing in self.ingredients
            ]
            if not self.ingredients_text:
                self.ingredients_text = ", ".join(f"{ing.weight_g:g}g {ing.name}" for ing in self.ingredients)

        self.recalculate_macros()

    def recalculate_macros(self):
        """Calculates and stores the per-serving macros from ingredients and servings."""
        if not self.ingredients or self.servings <= 0:
            self.calories = 0.0
            self.protein = 0.0
            self.carbs = 0.0
            self.fat = 0.0
            return

        total_cal = sum(ing.calories() for ing in self.ingredients)
        total_p = sum(ing.protein() for ing in self.ingredients)
        total_c = sum(ing.carbs() for ing in self.ingredients)
        total_f = sum(ing.fat() for ing in self.ingredients)

        self.calories = round(total_cal / self.servings, 1)
        self.protein = round(total_p / self.servings, 1)
        self.carbs = round(total_c / self.servings, 1)
        self.fat = round(total_f / self.servings, 1)

    def total_calories(self) -> float:
        return round(sum(i.calories() for i in self.ingredients), 1)

    def total_protein(self) -> float:
        return round(sum(i.protein() for i in self.ingredients), 1)

    def total_carbs(self) -> float:
        return round(sum(i.carbs() for i in self.ingredients), 1)

    def total_fat(self) -> float:
        return round(sum(i.fat() for i in self.ingredients), 1)

    def total_macros(self) -> MacroProfile:
        return MacroProfile(
            calories=self.total_calories(),
            protein=self.total_protein(),
            carbs=self.total_carbs(),
            fat=self.total_fat(),
        )

    def calories_per_serving(self) -> float:
        return self.calories

    def protein_per_serving(self) -> float:
        return self.protein

    def carbs_per_serving(self) -> float:
        return self.carbs

    def fat_per_serving(self) -> float:
        return self.fat

    def macros_per_serving(self) -> MacroProfile:
        return MacroProfile(
            calories=self.calories,
            protein=self.protein,
            carbs=self.carbs,
            fat=self.fat,
        )

    def ingredients_summary(self) -> str:
        return self.ingredients_text or "No ingredients specified"