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
        self.recipes = self.recipes + [recipe]
        data_repository.save_recipes(self.recipes)

    def remove_recipe(self, id: int):
        self.recipes = [r for r in self.recipes if r.id != id]
        data_repository.save_recipes(self.recipes)

    def update_recipe(self, recipe: Recipe):
        self.recipes = [recipe if r.id == recipe.id else r for r in self.recipes]
        data_repository.save_recipes(self.recipes)

    def next_recipe_id(self) -> int:
        existing_ids = {r.id for r in self.recipes}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        return new_id

    async def log_recipe_as_meal(self, recipe: Recipe):
        if isinstance(recipe, dict):
            recipe = Recipe(**recipe)
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


class RecipeDialogState(rx.State):
    show_modal: bool = False
    is_editing_recipe: bool = False

    # Form fields
    recipe_id: int = 0
    name: str = ""
    instructions: str = ""
    servings: int = 1
    ingredients: list[Ingredient] = []

    @rx.var
    def modal_title(self) -> str:
        return "Edit Recipe" if self.is_editing_recipe else "Create New Recipe"

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_name(self, val: str):
        self.name = val

    def set_instructions(self, val: str):
        self.instructions = val

    def set_servings(self, val: str):
        try:
            self.servings = int(val)
        except (ValueError, TypeError):
            self.servings = 1

    def add_ingredient(self):
        items = self._copy_ingredients()
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
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items.pop(index)
            self.ingredients = items

    def update_ingredient_name(self, index: int, val: str):
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].name = val
            self.ingredients = items

    def update_ingredient_amount(self, index: int, val: str):
        try:
            a = float(val)
        except (ValueError, TypeError):
            a = 0.0
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].amount = a
            self.ingredients = items

    def update_ingredient_weight(self, index: int, val: str):
        self.update_ingredient_amount(index, val)

    def update_ingredient_unit(self, index: int, val: str):
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].unit = Unit(val)
            self.ingredients = items

    def update_ingredient_calories(self, index: int, val: str):
        try:
            c = float(val)
        except (ValueError, TypeError):
            c = 0.0
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].macros_per_unit.calories = c
            self.ingredients = items

    def update_ingredient_protein(self, index: int, val: str):
        try:
            p = float(val)
        except (ValueError, TypeError):
            p = 0.0
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].macros_per_unit.protein = p
            self.ingredients = items

    def update_ingredient_carbs(self, index: int, val: str):
        try:
            cb = float(val)
        except (ValueError, TypeError):
            cb = 0.0
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].macros_per_unit.carbs = cb
            self.ingredients = items

    def update_ingredient_fat(self, index: int, val: str):
        try:
            f = float(val)
        except (ValueError, TypeError):
            f = 0.0
        items = self._copy_ingredients()
        if 0 <= index < len(items):
            items[index].macros_per_unit.fat = f
            self.ingredients = items

    def open_add_recipe(self):
        self.is_editing_recipe = False
        self.recipe_id = 0
        self.name = ""
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
        self.recipe_id = recipe.id
        self.name = recipe.name
        self.instructions = recipe.instructions
        self.servings = recipe.servings
        
        ingredients_list = []
        for ing in recipe.ingredients:
            if isinstance(ing, dict):
                ingredients_list.append(Ingredient(**ing))
            else:
                macros = getattr(ing, "macros_per_unit", None)
                if macros is None:
                    macros = getattr(ing, "macros_per_100g", MacroProfile())
                if isinstance(macros, dict):
                    macros = MacroProfile(**macros)

                unit = getattr(ing, "unit", Unit("g"))
                if isinstance(unit, str):
                    unit = Unit(unit)
                elif isinstance(unit, dict):
                    unit = Unit(**unit)

                amount = getattr(ing, "amount", None)
                if amount is None:
                    amount = getattr(ing, "weight_g", 100.0)

                ingredients_list.append(Ingredient(
                    name=ing.name,
                    macros_per_unit=MacroProfile(
                        calories=macros.calories,
                        protein=macros.protein,
                        carbs=macros.carbs,
                        fat=macros.fat,
                    ),
                    amount=amount,
                    unit=unit,
                ))
        if not ingredients_list:
            ingredients_list = [
                Ingredient(
                    name="",
                    macros_per_unit=MacroProfile(calories=0.0, protein=0.0, carbs=0.0, fat=0.0),
                    amount=100.0,
                    unit=Unit("g"),
                )
            ]
        self.ingredients = ingredients_list
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_recipe(self):
        if not self.name.strip():
            return

        recipes_state = await self.get_state(RecipesState)

        valid_ingredients = [
            ing for ing in self._copy_ingredients()
            if ing.name.strip() or ing.amount > 0
        ]
        ingredients_text = ", ".join(f"{ing.amount:g}{ing.unit.unit} {ing.name}" for ing in valid_ingredients if ing.name.strip())

        if self.is_editing_recipe:
            updated_recipe = Recipe(
                id=self.recipe_id,
                name=self.name.strip(),
                instructions=self.instructions.strip(),
                ingredients=valid_ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=ingredients_text,
            )
            recipes_state.update_recipe(updated_recipe)
        else:
            new_id = recipes_state.next_recipe_id()
            new_recipe = Recipe(
                id=new_id,
                name=self.name.strip(),
                instructions=self.instructions.strip(),
                ingredients=valid_ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=ingredients_text,
            )
            recipes_state.add_recipe(new_recipe)

        self.show_modal = False