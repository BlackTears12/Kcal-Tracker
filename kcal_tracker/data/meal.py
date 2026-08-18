from enum import Enum
from datetime import datetime, date
from dataclasses import dataclass, field

@dataclass
class MacroProfile:
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0


class MealCategory(str, Enum):
    Breakfast = "Breakfast"
    Lunch = "Lunch"
    Dinner = "Dinner"
    Snack = "Snack"


@dataclass
class Meal:
    id: int = 0
    name: str = ""
    category: MealCategory = MealCategory.Breakfast
    macros: MacroProfile = field(default_factory=MacroProfile)
    time: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.macros, dict):
            self.macros = MacroProfile(**self.macros)
        if isinstance(self.category, str):
            try:
                self.category = MealCategory(self.category)
            except ValueError:
                self.category = MealCategory.Breakfast
        if isinstance(self.time, str):
            try:
                self.time = datetime.fromisoformat(self.time)
            except ValueError:
                self.time = datetime.now()