import reflex as rx
from kcal_tracker.data.meal import *
from kcal_tracker.states.nutrition_state import NutritionState
from kcal_tracker.data.recipe import *
import kcal_tracker.models.data_repository as data_repository


class RecipesState(rx.State):
    recipes: list[Recipe] = data_repository.load_recipes() 

    # Computed vars
    @rx.var
    def recipe_count(self) -> int:
        return len(self.recipes)

    # Event handlers
    def add_recipe(self, recipe: Recipe):
        if self.has_recipe(recipe.name):
            return rx.window_alert(f"A recipe with the name '{recipe.name}' already exists.")
        self.recipes = self.recipes + [recipe]
        data_repository.save_recipes(self.recipes)

    def remove_recipe(self, name: str):
        self.recipes = [r for r in self.recipes if r.name.strip().lower() != name.strip().lower()]
        data_repository.save_recipes(self.recipes)

    def update_recipe(self, recipe: Recipe, old_name: str = ""):
        target = (old_name or recipe.name).strip().lower()
        self.recipes = [recipe if r.name.strip().lower() == target else r for r in self.recipes]
        data_repository.save_recipes(self.recipes)

    async def log_recipe_as_meal(self, recipe: Recipe | str):
        if isinstance(recipe, str):
            recipe = next(filter(lambda r: r.name.lower().strip() == recipe, self.recipes))
        nutrition_state = await self.get_state(NutritionState)
        new_meal = Meal(            
            name=recipe.name,
            category=MealCategory.Lunch,
            macros=recipe.macros_per_serving(),
            date=nutrition_state.date_context,
            amount=1.0,
            unit=Unit("serving"),
        )
        await nutrition_state.add_meal(new_meal)

    def has_recipe(self, name: str):
        return name.lower().strip() in [r.name.lower().strip() for r in self.recipes]

class RecipeDialogState(rx.State):
    show_modal: bool = False
    is_editing_recipe: bool = False

    # Form fields
    original_name: str = ""
    name: str = ""
    error_message: str = ""
    instructions: str = ""
    servings: int = 1
    ingredients: list[Ingredient] = []

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
        self.original_name = ""
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
        self.show_modal = True

    def open_edit_recipe(self, recipe: Recipe):
        if isinstance(recipe, dict):
            recipe = Recipe(**recipe)
        self.is_editing_recipe = True
        self.original_name = recipe.name
        self.name = recipe.name
        self.error_message = ""
        self.instructions = recipe.instructions
        self.servings = recipe.servings
        self.ingredients = recipe.ingredients
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False
        self.error_message = ""

    async def save_recipe(self):
        trimmed_name = self.name.strip()
        if not trimmed_name:
            self.error_message = "Recipe title cannot be empty."
            return

        recipes_state = await self.get_state(RecipesState)
        name_changed = trimmed_name.lower() != self.original_name.strip().lower()

        # Check for duplicate recipe name
        if (self.is_editing_recipe and name_changed and recipes_state.has_recipe(trimmed_name)) or not self.is_editing_recipe:
                self.error_message = f"A recipe with the name '{trimmed_name}' already exists."
                return rx.window_alert(f"A recipe with the name '{trimmed_name}' already exists.")

        valid_ingredients = [
            ing for ing in self.ingredients
            if ing.name.strip() or ing.amount > 0
        ]
        ingredients_text = ", ".join(f"{ing.amount:g}{ing.unit.unit} {ing.name}" for ing in valid_ingredients if ing.name.strip())

        if self.is_editing_recipe:
            updated_recipe = Recipe(
                name=trimmed_name,
                instructions=self.instructions.strip(),
                ingredients=valid_ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=ingredients_text,
            )
            recipes_state.update_recipe(updated_recipe, old_name=self.original_name)
        else:
            new_recipe = Recipe(
                name=trimmed_name,
                instructions=self.instructions.strip(),
                ingredients=valid_ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=ingredients_text,
            )
            recipes_state.add_recipe(new_recipe)

        self.show_modal = False
        self.error_message = ""