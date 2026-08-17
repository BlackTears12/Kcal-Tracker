import reflex as rx
from enum import Enum
from datetime import datetime
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


def get_default_meals() -> list[Meal]:
    return [
        Meal(
            id=1,
            name="Oatmeal with Berries & Whey",
            category=MealCategory.Breakfast,
            macros=MacroProfile(calories=420, protein=28, carbs=58, fat=7),
            time=datetime.now(),
        ),
        Meal(
            id=2,
            name="Grilled Chicken Salad & Quinoa",
            category=MealCategory.Lunch,
            macros=MacroProfile(calories=550, protein=48, carbs=45, fat=14),
            time=datetime.now(),
        ),
    ]


class NutritionState(rx.State):
    target_calories: int = 2200
    target_protein: int = 160
    target_carbs: int = 220
    target_fat: int = 65
    logged_meals: list[Meal] = get_default_meals()

    # Computed vars
    @rx.var
    def total_calories(self) -> int:
        return round(sum(m.macros.calories for m in self.logged_meals))

    @rx.var
    def total_protein(self) -> int:
        return round(sum(m.macros.protein for m in self.logged_meals))

    @rx.var
    def total_carbs(self) -> int:
        return round(sum(m.macros.carbs for m in self.logged_meals))

    @rx.var
    def total_fat(self) -> int:
        return round(sum(m.macros.fat for m in self.logged_meals))

    @rx.var
    def remaining_calories(self) -> int:
        rem = self.target_calories - self.total_calories
        return max(0, rem)

    @rx.var
    def remaining_protein(self) -> int:
        rem = self.target_protein - self.total_protein
        return max(0, rem)

    @rx.var
    def calorie_percentage(self) -> int:
        if self.target_calories <= 0:
            return 0
        pct = int((self.total_calories / self.target_calories) * 100)
        return min(100, max(0, pct))

    @rx.var
    def protein_percentage(self) -> int:
        if self.target_protein <= 0:
            return 0
        pct = int((self.total_protein / self.target_protein) * 100)
        return min(100, max(0, pct))

    @rx.var
    def carbs_percentage(self) -> int:
        if self.target_carbs <= 0:
            return 0
        pct = int((self.total_carbs / self.target_carbs) * 100)
        return min(100, max(0, pct))

    @rx.var
    def fat_percentage(self) -> int:
        if self.target_fat <= 0:
            return 0
        pct = int((self.total_fat / self.target_fat) * 100)
        return min(100, max(0, pct))

    @rx.var
    def is_calorie_over(self) -> bool:
        return self.total_calories > self.target_calories

    @rx.var
    def meal_count(self) -> int:
        return len(self.logged_meals)

    # Event handlers
    def add_meal(self, meal: Meal):
        meal.id = self.next_meal_id()
        self.logged_meals = self.logged_meals + [meal]

    def add_meal_list(self, meals: list[Meal]):
        for m in meals:
            m.id = self.next_meal_id()
        self.logged_meals = self.logged_meals + meals

    def remove_meal(self, id: int):
        self.logged_meals = [m for m in self.logged_meals if m.id != id]

    def update_meal(self, meal: Meal):
        self.logged_meals = [meal if m.id == meal.id else m for m in self.logged_meals]

    def clear_all_meals(self):
        self.logged_meals = []

    def set_targets(self, calories: int, protein: int, carbs: int, fat: int):
        self.target_calories = max(500, int(calories))
        self.target_protein = max(10, int(protein))
        self.target_carbs = max(10, int(carbs))
        self.target_fat = max(5, int(fat))

    # Utilities
    def next_meal_id(self) -> int:
        existing_ids = {m.id for m in self.logged_meals}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        return new_id


class MealDialogState(rx.State):
    show_modal: bool = False
    is_editing_meal: bool = False

    # Form fields
    meal_id: int = 0
    name: str = ""
    category: MealCategory = MealCategory.Breakfast
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0

    @rx.var
    def modal_title(self) -> str:
        return "Edit Logged Meal" if self.is_editing_meal else "Add New Meal"

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_name(self, val: str):
        self.name = val

    def set_category(self, val: str):
        try:
            self.category = MealCategory(val)
        except ValueError:
            self.category = MealCategory.Breakfast

    def set_calories(self, val: str):
        try:
            self.calories = float(val)
        except (ValueError, TypeError):
            self.calories = 0.0

    def set_protein(self, val: str):
        try:
            self.protein = float(val)
        except (ValueError, TypeError):
            self.protein = 0.0

    def set_carbs(self, val: str):
        try:
            self.carbs = float(val)
        except (ValueError, TypeError):
            self.carbs = 0.0

    def set_fat(self, val: str):
        try:
            self.fat = float(val)
        except (ValueError, TypeError):
            self.fat = 0.0

    def open_add_meal(self):
        self.is_editing_meal = False
        self.meal_id = 0
        self.name = ""
        self.category = MealCategory.Breakfast
        self.calories = 0.0
        self.protein = 0.0
        self.carbs = 0.0
        self.fat = 0.0
        self.show_modal = True

    def open_edit_meal(self, meal: Meal):
        self.is_editing_meal = True
        self.meal_id = meal.id
        self.name = meal.name
        self.category = meal.category
        self.calories = meal.macros.calories
        self.protein = meal.macros.protein
        self.carbs = meal.macros.carbs
        self.fat = meal.macros.fat
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_meal(self):
        if not self.name.strip():
            return

        nutrition_state = await self.get_state(NutritionState)
        macros = MacroProfile(
            calories=float(self.calories),
            protein=float(self.protein),
            carbs=float(self.carbs),
            fat=float(self.fat),
        )

        if self.is_editing_meal:
            existing = next((m for m in nutrition_state.logged_meals if m.id == self.meal_id), None)
            meal_time = existing.time if existing else datetime.now()
            updated_meal = Meal(
                id=self.meal_id,
                name=self.name.strip(),
                category=self.category,
                macros=macros,
                time=meal_time,
            )
            nutrition_state.update_meal(updated_meal)
        else:
            new_id = nutrition_state.next_meal_id()
            new_meal = Meal(
                id=new_id,
                name=self.name.strip(),
                category=self.category,
                macros=macros,
                time=datetime.now(),
            )
            nutrition_state.add_meal(new_meal)

        self.show_modal = False


class TargetDialogState(rx.State):
    show_modal: bool = False
    target_calories: int = 2200
    target_protein: int = 160
    target_carbs: int = 220
    target_fat: int = 65

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_target_calories(self, val: str):
        try:
            self.target_calories = int(val)
        except (ValueError, TypeError):
            pass

    def set_target_protein(self, val: str):
        try:
            self.target_protein = int(val)
        except (ValueError, TypeError):
            pass

    def set_target_carbs(self, val: str):
        try:
            self.target_carbs = int(val)
        except (ValueError, TypeError):
            pass

    def set_target_fat(self, val: str):
        try:
            self.target_fat = int(val)
        except (ValueError, TypeError):
            pass

    async def open_modal(self):
        nutrition_state = await self.get_state(NutritionState)
        self.target_calories = nutrition_state.target_calories
        self.target_protein = nutrition_state.target_protein
        self.target_carbs = nutrition_state.target_carbs
        self.target_fat = nutrition_state.target_fat
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_targets(self):
        nutrition_state = await self.get_state(NutritionState)
        nutrition_state.set_targets(
            calories=self.target_calories,
            protein=self.target_protein,
            carbs=self.target_carbs,
            fat=self.target_fat,
        )
        self.show_modal = False