import reflex as rx
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from kcal_tracker.data.meal import *
from kcal_tracker.states.nutrition_state import NutritionState


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
            if self.calories == 0.0:
                self.calories = round(sum(ing.calories() for ing in self.ingredients), 1)
            if self.protein == 0.0:
                self.protein = round(sum(ing.protein() for ing in self.ingredients), 1)
            if self.carbs == 0.0:
                self.carbs = round(sum(ing.carbs() for ing in self.ingredients), 1)
            if self.fat == 0.0:
                self.fat = round(sum(ing.fat() for ing in self.ingredients), 1)

    def total_calories(self) -> float:
        return self.calories

    def total_protein(self) -> float:
        return self.protein

    def total_carbs(self) -> float:
        return self.carbs

    def total_fat(self) -> float:
        return self.fat

    def calories_per_serving(self) -> float:
        if self.servings <= 0:
            return 0.0
        return round(self.calories / self.servings, 1)

    def protein_per_serving(self) -> float:
        if self.servings <= 0:
            return 0.0
        return round(self.protein / self.servings, 1)

    def carbs_per_serving(self) -> float:
        if self.servings <= 0:
            return 0.0
        return round(self.carbs / self.servings, 1)

    def fat_per_serving(self) -> float:
        if self.servings <= 0:
            return 0.0
        return round(self.fat / self.servings, 1)

    def macros_per_serving(self) -> MacroProfile:
        return MacroProfile(
            calories=self.calories_per_serving(),
            protein=self.protein_per_serving(),
            carbs=self.carbs_per_serving(),
            fat=self.fat_per_serving(),
        )

    def ingredients_summary(self) -> str:
        return self.ingredients_text or "No ingredients specified"


def get_default_recipes() -> list[Recipe]:
    return [
        Recipe(
            id=1,
            name="High-Protein Salmon & Rice Bowl",
            servings=1,
            ingredients=[
                Ingredient(
                    name="Salmon fillet",
                    macros_per_100g=MacroProfile(calories=208, protein=20, carbs=0, fat=13),
                    weight_g=180,
                ),
                Ingredient(
                    name="Cooked Jasmine Rice",
                    macros_per_100g=MacroProfile(calories=130, protein=2.7, carbs=28, fat=0.3),
                    weight_g=150,
                ),
                Ingredient(
                    name="Steamed Broccoli",
                    macros_per_100g=MacroProfile(calories=34, protein=2.8, carbs=7, fat=0.4),
                    weight_g=100,
                ),
            ],
        ),
        Recipe(
            id=2,
            name="Post-Workout Whey Smoothie",
            servings=1,
            ingredients=[
                Ingredient(
                    name="Whey Isolate",
                    macros_per_100g=MacroProfile(calories=370, protein=80, carbs=3, fat=2),
                    weight_g=30,
                ),
                Ingredient(
                    name="Banana",
                    macros_per_100g=MacroProfile(calories=89, protein=1.1, carbs=23, fat=0.3),
                    weight_g=120,
                ),
                Ingredient(
                    name="Almond Milk",
                    macros_per_100g=MacroProfile(calories=15, protein=0.5, carbs=0.3, fat=1.1),
                    weight_g=250,
                ),
                Ingredient(
                    name="Peanut Butter",
                    macros_per_100g=MacroProfile(calories=588, protein=25, carbs=20, fat=50),
                    weight_g=15,
                ),
            ],
        ),
    ]


class RecipesState(rx.State):
    recipes: list[Recipe] = get_default_recipes()

    # Computed vars
    @rx.var
    def recipe_count(self) -> int:
        return len(self.recipes)

    # Event handlers
    def add_recipe(self, recipe: Recipe):
        self.recipes = self.recipes + [recipe]

    def remove_recipe(self, id: int):
        self.recipes = [r for r in self.recipes if r.id != id]

    def update_recipe(self, recipe: Recipe):
        self.recipes = [recipe if r.id == recipe.id else r for r in self.recipes]

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
        )
        await nutrition_state.add_meal(new_meal)


class RecipeDialogState(rx.State):
    show_modal: bool = False
    is_editing_recipe: bool = False

    # Form fields
    recipe_id: int = 0
    name: str = ""
    servings: int = 1
    ingredients_text: str = ""

    # Direct macros (for quick manual input)
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0

    @rx.var
    def modal_title(self) -> str:
        return "Edit Recipe" if self.is_editing_recipe else "Create New Recipe"

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_name(self, val: str):
        self.name = val

    def set_ingredients_text(self, val: str):
        self.ingredients_text = val

    def set_servings(self, val: str):
        try:
            self.servings = int(val)
        except (ValueError, TypeError):
            self.servings = 1

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

    def open_add_recipe(self):
        self.is_editing_recipe = False
        self.recipe_id = 0
        self.name = ""
        self.servings = 1
        self.ingredients_text = ""
        self.calories = 0.0
        self.protein = 0.0
        self.carbs = 0.0
        self.fat = 0.0
        self.show_modal = True

    def open_edit_recipe(self, recipe: Recipe):
        if isinstance(recipe, dict):
            recipe = Recipe(**recipe)
        self.is_editing_recipe = True
        self.recipe_id = recipe.id
        self.name = recipe.name
        self.servings = recipe.servings
        self.ingredients_text = recipe.ingredients_text or recipe.ingredients_summary()
        self.calories = recipe.calories
        self.protein = recipe.protein
        self.carbs = recipe.carbs
        self.fat = recipe.fat
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_recipe(self):
        if not self.name.strip():
            return

        recipes_state = await self.get_state(RecipesState)

        # Create ingredient wrapper with total macros
        ingredients = [
            Ingredient(
                name=self.ingredients_text.strip() or "Ingredients",
                macros_per_100g=MacroProfile(
                    calories=float(self.calories),
                    protein=float(self.protein),
                    carbs=float(self.carbs),
                    fat=float(self.fat),
                ),
                weight_g=100.0,
            )
        ]

        if self.is_editing_recipe:
            updated_recipe = Recipe(
                id=self.recipe_id,
                name=self.name.strip(),
                ingredients=ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=self.ingredients_text.strip(),
                calories=float(self.calories),
                protein=float(self.protein),
                carbs=float(self.carbs),
                fat=float(self.fat),
            )
            recipes_state.update_recipe(updated_recipe)
        else:
            new_id = recipes_state.next_recipe_id()
            new_recipe = Recipe(
                id=new_id,
                name=self.name.strip(),
                ingredients=ingredients,
                servings=max(1, int(self.servings)),
                ingredients_text=self.ingredients_text.strip(),
                calories=float(self.calories),
                protein=float(self.protein),
                carbs=float(self.carbs),
                fat=float(self.fat),
            )
            recipes_state.add_recipe(new_recipe)

        self.show_modal = False