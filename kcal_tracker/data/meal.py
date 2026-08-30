from enum import Enum
import datetime
from dataclasses import dataclass, field
from kcal_tracker.data.unit import Unit

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
    amount: float = 1.0
    unit: Unit = field(default_factory=Unit)

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
        if isinstance(self.unit, str):
            self.unit = Unit(self.unit)
        elif isinstance(self.unit, dict):
            self.unit = Unit(**self.unit)

    def scale_size(self, new_amount: float, new_unit: Unit):
        old_amount = self.amount if self.amount else 1.0
        factor = new_amount * new_unit.conversion_factor(self.unit) / old_amount
        return Meal(
            id=self.id,
            name=self.name,
            category=self.category,
            date=self.date,
            amount=new_amount,
            unit=new_unit,
            macros=self.macros.scale(factor)
        )