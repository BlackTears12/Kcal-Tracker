from enum import Enum
import datetime
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
    date: datetime.date = field(default_factory=datetime.date.today)

    def __post_init__(self):
        if isinstance(self.macros, dict):
            self.macros = MacroProfile(**self.macros)
        if isinstance(self.category, str):
            try:
                self.category = MealCategory(self.category)
            except ValueError:
                self.category = MealCategory.Breakfast
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)