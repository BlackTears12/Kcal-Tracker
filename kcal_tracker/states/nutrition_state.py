import reflex as rx
from datetime import datetime, date, timedelta
from kcal_tracker.models.services import NutritionService
from kcal_tracker.data.meal import *
from kcal_tracker.data.unit import Unit
from kcal_tracker.data.workout import Workout, WorkoutType
from kcal_tracker.states.login_state import current_user_id

class NutritionState(rx.State):
    logged_meals: list[Meal] = []
    logged_workouts: list[Workout] = []
    date_context: date = date.today()
    targets: MacroProfile = MacroProfile()

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
    def target_calories(self) -> int:
        return round(self.targets.calories)

    @rx.var
    def target_protein(self) -> int:
        return round(self.targets.protein)

    @rx.var
    def target_carbs(self) -> int:
        return round(self.targets.carbs)

    @rx.var
    def target_fat(self) -> int:
        return round(self.targets.fat)

    @rx.var
    def total_burned(self) -> int:
        return round(sum(w.calories_burned for w in self.logged_workouts))

    @rx.var
    def total_workout_minutes(self) -> int:
        return round(sum(w.duration_min for w in self.logged_workouts))

    @rx.var
    def calorie_budget(self) -> int:
        """Calories available today: the target plus what workouts burned."""
        return round(self.targets.calories + self.total_burned)

    @rx.var
    def remaining_calories(self) -> int:
        rem = self.calorie_budget - self.total_calories
        return max(0, round(rem))

    @rx.var
    def remaining_protein(self) -> int:
        rem = self.targets.protein - self.total_protein
        return max(0, round(rem))

    @rx.var
    def remaining_carbs(self) -> int:
        rem = self.targets.carbs - self.total_carbs
        return max(0, round(rem))

    @rx.var
    def remaining_fat(self) -> int:
        rem = self.targets.fat - self.total_fat
        return max(0, round(rem))

    @rx.var
    def calorie_percentage(self) -> int:
        if self.calorie_budget <= 0:
            return 0
        pct = int((self.total_calories / self.calorie_budget) * 100)
        return min(100, max(0, pct))

    @rx.var
    def protein_percentage(self) -> int:
        if self.targets.protein <= 0:
            return 0
        pct = int((self.total_protein / self.targets.protein) * 100)
        return min(100, max(0, pct))

    @rx.var
    def carbs_percentage(self) -> int:
        if self.targets.carbs <= 0:
            return 0
        pct = int((self.total_carbs / self.targets.carbs) * 100)
        return min(100, max(0, pct))

    @rx.var
    def fat_percentage(self) -> int:
        if self.targets.fat <= 0:
            return 0
        pct = int((self.total_fat / self.targets.fat) * 100)
        return min(100, max(0, pct))

    @rx.var
    def formatted_date(self) -> str:
        today = date.today()
        if self.date_context == today:
            return f"Today, {self.date_context.strftime('%b %d')}"
        elif self.date_context == today - timedelta(days=1):
            return f"Yesterday, {self.date_context.strftime('%b %d')}"
        elif self.date_context == today + timedelta(days=1):
            return f"Tomorrow, {self.date_context.strftime('%b %d')}"
        return self.date_context.strftime("%a, %b %d, %Y")

    @rx.var
    def short_date(self) -> str:
        today = date.today()
        if self.date_context == today:
            return "Today"
        elif self.date_context == today - timedelta(days=1):
            return "Yesterday"
        elif self.date_context == today + timedelta(days=1):
            return "Tomorrow"
        return self.date_context.strftime("%b %d")

    @rx.var
    def is_today(self) -> bool:
        return self.date_context == date.today()

    @rx.var
    def is_calorie_over(self) -> bool:
        return self.total_calories > self.calorie_budget

    @rx.var
    def meal_count(self) -> int:
        return len(self.logged_meals)

    @rx.var
    def workout_count(self) -> int:
        return len(self.logged_workouts)

    # Event handlers
    async def view_next_day(self):
        await self._view_date(self.date_context + timedelta(days=1))

    async def view_previous_day(self):
        await self._view_date(self.date_context - timedelta(days=1))

    async def view_today(self):
        await self._view_date(date.today())

    async def remove_meal(self, id: int):
        user_id = await current_user_id(self)
        if user_id is None:
            return
        NutritionService(user_id).remove_meal(id)
        self._reload(user_id)

    async def remove_workout(self, id: int):
        user_id = await current_user_id(self)
        if user_id is None:
            return
        NutritionService(user_id).remove_workout(id)
        self._reload(user_id)

    def clear_all_meals(self):
        return rx.call_script(
            f"window.confirm('Delete all meals logged on {self.short_date}?')",
            callback=NutritionState.confirm_clear_all_meals,
        )

    async def confirm_clear_all_meals(self, confirmed: bool):
        user_id = await current_user_id(self)
        if user_id is None or not confirmed:
            return
        NutritionService(user_id).clear_day(self.date_context)
        self._reload(user_id)

    # Utilities, private so the client can't call them with another user's id
    async def _view_date(self, new_date: date):
        user_id = await current_user_id(self)
        if user_id is None:
            return
        self.date_context = new_date
        self._reload(user_id)

    def _reload(self, user_id: str):
        service = NutritionService(user_id)
        self.logged_meals = service.meals_on(self.date_context)
        self.logged_workouts = service.workouts_on(self.date_context)
        self.targets = service.get_targets()


class MealDialogState(rx.State):
    show_modal: bool = False
    is_editing_meal: bool = False

    # Form fields
    meal_id: int = 0
    name: str = ""
    category: MealCategory = MealCategory.Breakfast
    amount: float = 1.0
    unit: Unit = Unit()
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    scale_macros: bool = False

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

    def set_amount(self, val: str):
        try:
            self.amount = float(val)
        except (ValueError, TypeError):
            self.amount = 0.0

    def set_weight(self, val: str):
        self.set_amount(val)

    def set_unit(self, val: str):
        self.unit = Unit(val)

    def set_scale_macros(self, val: bool):
        self.scale_macros = val

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
        self.amount = 1.0
        self.unit = Unit()
        self.calories = 0.0
        self.protein = 0.0
        self.carbs = 0.0
        self.fat = 0.0
        self.scale_macros = False
        self.show_modal = True

    def open_edit_meal(self, meal: Meal):
        if isinstance(meal, dict):
            meal = Meal(**meal)
        self.is_editing_meal = True
        self.meal_id = meal.id
        self.name = meal.name
        self.category = meal.category
        self.amount = meal.amount
        self.unit = meal.unit
        self.calories = meal.macros.calories
        self.protein = meal.macros.protein
        self.carbs = meal.macros.carbs
        self.fat = meal.macros.fat
        self.scale_macros = False
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_meal(self):
        if not self.name.strip():
            return
        user_id = await current_user_id(self)
        if user_id is None:
            return

        service = NutritionService(user_id)
        nutrition_state = await self.get_state(NutritionState)
        macros = MacroProfile(
            calories=float(self.calories),
            protein=float(self.protein),
            carbs=float(self.carbs),
            fat=float(self.fat),
        )

        if self.is_editing_meal:
            existing = service.get_meal(self.meal_id)
            if existing is None:
                self.show_modal = False
                return

            updated_meal = Meal(
                id=self.meal_id,
                name=self.name.strip(),
                category=self.category,
                macros=macros,
                amount=self.amount,
                unit=self.unit
            )

            # if editing a meal with scale macros use the original amount as base for the scaling
            if self.scale_macros:
                updated_meal.amount = existing.amount
                updated_meal.unit = existing.unit
                updated_meal = updated_meal.scale_size(self.amount,self.unit)
                
            service.update_meal(updated_meal)
        else:
            new_meal = Meal(
                name=self.name.strip(),
                category=self.category,
                macros=macros,
                amount=float(self.amount),
                unit=self.unit,
            )
            service.add_meals([new_meal], nutrition_state.date_context)

        nutrition_state._reload(user_id)
        self.show_modal = False


class TargetDialogState(rx.State):
    show_modal: bool = False
    target: MacroProfile = MacroProfile()

    @rx.var
    def target_calories(self) -> int:
        return round(self.target.calories)

    @rx.var
    def target_protein(self) -> int:
        return round(self.target.protein)

    @rx.var
    def target_carbs(self) -> int:
        return round(self.target.carbs)

    @rx.var
    def target_fat(self) -> int:
        return round(self.target.fat)

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_target_calories(self, val: str):
        try:
            val_float = float(val) if val != "" else 0.0
            self.target = MacroProfile(
                calories=val_float,
                protein=self.target.protein,
                carbs=self.target.carbs,
                fat=self.target.fat,
            )
        except (ValueError, TypeError):
            pass

    def set_target_protein(self, val: str):
        try:
            val_float = float(val) if val != "" else 0.0
            self.target = MacroProfile(
                calories=self.target.calories,
                protein=val_float,
                carbs=self.target.carbs,
                fat=self.target.fat,
            )
        except (ValueError, TypeError):
            pass

    def set_target_carbs(self, val: str):
        try:
            val_float = float(val) if val != "" else 0.0
            self.target = MacroProfile(
                calories=self.target.calories,
                protein=self.target.protein,
                carbs=val_float,
                fat=self.target.fat,
            )
        except (ValueError, TypeError):
            pass

    def set_target_fat(self, val: str):
        try:
            val_float = float(val) if val != "" else 0.0
            self.target = MacroProfile(
                calories=self.target.calories,
                protein=self.target.protein,
                carbs=self.target.carbs,
                fat=val_float,
            )
        except (ValueError, TypeError):
            pass

    async def open_modal(self):
        nutrition_state = await self.get_state(NutritionState)
        self.target = MacroProfile(
            calories=nutrition_state.targets.calories,
            protein=nutrition_state.targets.protein,
            carbs=nutrition_state.targets.carbs,
            fat=nutrition_state.targets.fat,
        )
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_targets(self):
        user_id = await current_user_id(self)
        if user_id is None:
            return
        nutrition_state = await self.get_state(NutritionState)
        nutrition_state.targets = NutritionService(user_id).set_targets(self.target)
        self.show_modal = False