from enum import Enum
import datetime
from dataclasses import dataclass, field

@dataclass
class MacroProfile:
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0

    def scale(self, factor: float):
        return MacroProfile(
            self.calories*factor,
            self.protein*factor,
            self.carbs*factor,
            self.fat*factor)


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
    weight: float = 0.0

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

    def scale_weight(self, new_weight: float):
        old_weight = self.weight if self.weight else 1.0
        return Meal(
            id=self.id,
            category=self.category,
            date=self.date,
            weight=new_weight,
            macros=self.macros.scale(new_weight/old_weight)
        )