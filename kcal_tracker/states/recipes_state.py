import reflex as rx
from kcal_tracker.data.meal import *
from kcal_tracker.states.nutrition_state import NutritionState
from kcal_tracker.data.recipe import *
from kcal_tracker.models.services import DuplicateRecipeError, NutritionService, RecipeService
from kcal_tracker.states.login_state import current_user_id


class RecipesState(rx.State):
    recipes: list[Recipe] = []

    # Computed vars
    @rx.var
    def recipe_count(self) -> int:
        return len(self.recipes)

    # Event handlers
    async def load(self):
        if await current_user_id(self) is None:
            return
        self._reload()

    async def remove_recipe(self, name: str):
        if await current_user_id(self) is None:
            return
        RecipeService().remove_recipe(name)
        self._reload()

    async def log_recipe_as_meal(self, recipe: Recipe):
        user_id = await current_user_id(self)
        if user_id is None:
            return
        if isinstance(recipe, dict):
            recipe = Recipe(**recipe)
        stored = RecipeService().get_recipe_by_id(recipe.id)
        if stored is None:
            return rx.window_alert(f"The recipe '{recipe.name}' no longer exists.")
        nutrition_state = await self.get_state(NutritionState)
        NutritionService(user_id).log_recipe(stored, nutrition_state.date_context)
        nutrition_state._reload(user_id)

    # Utilities
    def _reload(self):
        self.recipes = RecipeService().list_recipes()

class RecipeDialogState(rx.State):
    show_modal: bool = False
    is_editing_recipe: bool = False

    # Form fields
    recipe_id: int = 0
    name: str = ""
    error_message: str = ""
    instructions: str = ""
    servings: int = 1
    ingredients: list[Ingredient] = []
    scale_macros: bool = True
    adjust_logged_meals: bool = False

    @rx.var
    def modal_title(self) -> str:
        return "Edit Recipe" if self.is_editing_recipe else "Create New Recipe"

    def set_show_modal(self, val: bool):
        self.show_modal = val
        if not val:
            self.error_message = ""

    def set_name(self, val: str):
        self.name = val
        self.error_message = ""

    def set_instructions(self, val: str):
        self.instructions = val

    def set_servings(self, val: str):
        try:
            self.servings = int(val)
        except (ValueError, TypeError):
            self.servings = 1

    def set_scale_macros(self, val: bool):
        self.scale_macros = val

    def set_adjust_logged_meals(self, val: bool):
        self.adjust_logged_meals = val

    def add_ingredient(self):
        items = self.ingredients
        items.append(
            Ingredient(
                name="",
                macros_per_unit=MacroProfile(calories=0.0, protein=0.0, carbs=0.0, fat=0.0),
                amount=100.0,
                unit=Unit("g"),
            )
        )
        self.ingredients = items

    def remove_ingredient(self, index: int):
        items = self.ingredients
        if 0 <= index < len(items):
            items.pop(index)
            self.ingredients = items

    def update_ingredient_name(self, index: int, val: str):
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].name = val
            self.ingredients = items

    def update_ingredient_amount(self, index: int, val: str):
        try:
            a = float(val)
        except (ValueError, TypeError):
            a = 0.0
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].amount = a
            self.ingredients = items

    def update_ingredient_weight(self, index: int, val: str):
        self.update_ingredient_amount(index, val)

    def update_ingredient_unit(self, index: int, val: str):
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].unit = Unit(val)
            self.ingredients = items

    def update_ingredient_calories(self, index: int, val: str):
        try:
            c = float(val)
        except (ValueError, TypeError):
            c = 0.0
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].macros_per_unit.calories = c
            self.ingredients = items

    def update_ingredient_protein(self, index: int, val: str):
        try:
            p = float(val)
        except (ValueError, TypeError):
            p = 0.0
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].macros_per_unit.protein = p
            self.ingredients = items

    def update_ingredient_carbs(self, index: int, val: str):
        try:
            cb = float(val)
        except (ValueError, TypeError):
            cb = 0.0
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].macros_per_unit.carbs = cb
            self.ingredients = items

    def update_ingredient_fat(self, index: int, val: str):
        try:
            f = float(val)
        except (ValueError, TypeError):
            f = 0.0
        items = self.ingredients
        if 0 <= index < len(items):
            items[index].macros_per_unit.fat = f
            self.ingredients = items

    def open_add_recipe(self):
        self.is_editing_recipe = False
        self.recipe_id = 0
        self.name = ""
        self.error_message = ""
        self.instructions = ""
        self.servings = 1
        self.ingredients = [
            Ingredient(
                name="",
                macros_per_unit=MacroProfile(calories=0.0, protein=0.0, carbs=0.0, fat=0.0),
                amount=100.0,
                unit=Unit("g"),
            )
        ]
        self.scale_macros = False
        self.adjust_logged_meals = True
        self.show_modal = True

    def open_edit_recipe(self, recipe: Recipe):
        if isinstance(recipe, dict):
            recipe = Recipe(**recipe)
        self.is_editing_recipe = True
        self.recipe_id = recipe.id
        self.name = recipe.name
        self.error_message = ""
        self.instructions = recipe.instructions
        self.servings = recipe.servings
        self.ingredients = recipe.ingredients
        self.scale_macros = False
        self.adjust_logged_meals = True
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False
        self.error_message = ""
        self.adjust_logged_meals = True

    async def save_recipe(self):
        trimmed_name = self.name.strip()
        if not trimmed_name:
            self.error_message = "Recipe title cannot be empty."
            return
        user_id = await current_user_id(self)
        if user_id is None:
            return

        service = RecipeService()
        recipe = Recipe(
            id=self.recipe_id,
            name=trimmed_name,
            instructions=self.instructions.strip(),
            ingredients=self._ingredients_to_save(service),
            servings=max(1, int(self.servings)),
        )
        try:
            if self.is_editing_recipe:
                service.update_recipe(recipe, adjust_logged_meals=self.adjust_logged_meals)
            else:
                service.add_recipe(recipe)
        except DuplicateRecipeError as e:
            self.error_message = str(e)
            return rx.window_alert(str(e))

        recipes_state = await self.get_state(RecipesState)
        recipes_state._reload()
        nutrition_state = await self.get_state(NutritionState)
        nutrition_state._reload(user_id)
        self.show_modal = False
        self.error_message = ""

    def _ingredients_to_save(self, service: RecipeService) -> list[Ingredient]:
        ingredients = [ing for ing in self.ingredients if ing.name.strip()]
        original = service.get_recipe_by_id(self.recipe_id) if self.is_editing_recipe else None
        if not self.scale_macros or original is None:
            return ingredients

        # Macros are per unit: convert them for ingredients whose unit changed since the recipe was saved
        originals = {ing.name.strip().lower(): ing for ing in original.ingredients}
        converted = []
        for ing in ingredients:
            old = originals.get(ing.name.strip().lower())
            if old is not None and old.unit.unit != ing.unit.unit:
                ing = Ingredient(ing.name, ing.macros_per_unit, old.amount, old.unit).scale_size(ing.amount, ing.unit)
            converted.append(ing)
        return converted
