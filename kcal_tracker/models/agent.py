from google import genai
from pydantic import BaseModel, Field
from typing import cast
from kcal_tracker.data.meal import *
from kcal_tracker.data.recipe import Recipe, Ingredient
import kcal_tracker.state_accessor as state_accessor


class MealSchema(BaseModel):
    id: int = Field(default=0, description="The ID of the already logged meal, not used when logging a new meal")
    name: str = Field(description="Name of the meal")
    calories: float = Field(description="Amount kcal of calories contained in the meal")
    protein_g: float = Field(description="grams of protein contained in the meal")
    carbs_g: float = Field(description="grams of carbs contained in the meal")
    fat_g: float = Field(description="grams of fat contained in the meal")
    amount: float = Field(default=1.0, description="Quantity / amount of the meal")
    unit: str = Field(default="g", description="Unit of measurement: g, dkg, kg, ml, dl, l, or serving")

    @classmethod
    def from_app_meal(cls, meal: Meal):
        return cls(
            id=meal.id,
            name=meal.name,
            calories=meal.macros.calories,
            protein_g=meal.macros.protein,
            carbs_g=meal.macros.carbs,
            fat_g=meal.macros.fat,
            amount=meal.amount,
            unit=meal.unit.unit if isinstance(meal.unit, Unit) else str(meal.unit),
        )

    def to_app_meal(self) -> Meal:
        return Meal(
            id=self.id,
            name=self.name,
            category=MealCategory.Breakfast,
            macros=MacroProfile(
                self.calories, self.protein_g, self.carbs_g, self.fat_g
            ),
            amount=self.amount,
            unit=Unit(self.unit),
        )


async def get_meals(category: str = "all") -> list[MealSchema]:
    """Returns the list of meals registered today.

    Args: 
        category: optional meal category to filter by (breakfast, lunch, dinner, snack, or all)
    """
    print("get_meals!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    return [MealSchema.from_app_meal(app_meal) for app_meal in nutrition_state.logged_meals]


async def add_meals(meals: list[MealSchema]):
    """Register a list of meals eaten by the user today"""
    print("add_meals!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    await nutrition_state.add_meal_list([m.to_app_meal() for m in meals])


async def update_meal(meal: MealSchema):
    """Update a logged meal with the same id"""
    print("update_meal!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    await nutrition_state.update_meal(meal.to_app_meal())


async def remove_meal(id: int):
    """Remove the meal from the log with the specified id"""
    print("remove_meal!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    await nutrition_state.remove_meal(id)


class IngredientSchema(BaseModel):
    name: str = Field(description="Name of the ingredient (e.g. Oats, Chicken Breast, Almond Milk)")
    amount: float = Field(default=1.0, description="Quantity / amount of the ingredient")
    unit: str = Field(default="g", description="Unit of measurement: g, dkg, kg, ml, dl, l, or serving")
    calories_per_unit: float = Field(default=0.0, description="Calories in kcal per 1 unit of the ingredient")
    protein_per_unit: float = Field(default=0.0, description="Protein in grams per 1 unit of the ingredient")
    carbs_per_unit: float = Field(default=0.0, description="Carbs in grams per 1 unit of the ingredient")
    fat_per_unit: float = Field(default=0.0, description="Fat in grams per 1 unit of the ingredient")

    @classmethod
    def from_app_ingredient(cls, ingredient: Ingredient) -> "IngredientSchema":
        return cls(
            name=ingredient.name,
            amount=ingredient.amount,
            unit=ingredient.unit.unit if isinstance(ingredient.unit, Unit) else str(ingredient.unit),
            calories_per_unit=ingredient.macros_per_unit.calories,
            protein_per_unit=ingredient.macros_per_unit.protein,
            carbs_per_unit=ingredient.macros_per_unit.carbs,
            fat_per_unit=ingredient.macros_per_unit.fat,
        )

    def to_app_ingredient(self) -> Ingredient:
        return Ingredient(
            name=self.name,
            macros_per_unit=MacroProfile(
                calories=self.calories_per_unit,
                protein=self.protein_per_unit,
                carbs=self.carbs_per_unit,
                fat=self.fat_per_unit,
            ),
            amount=self.amount,
            unit=Unit(self.unit),
        )


class RecipeSchema(BaseModel):
    id: int = Field(default=0, description="The ID of the recipe, not used when creating a new recipe")
    name: str = Field(description="Name of the Recipe")
    instructions: str = Field(default="", description="Detailed preparation and cooking instructions for the recipe")
    servings: int = Field(default=1, description="Amount of servings produced by the recipe")
    ingredients: list[IngredientSchema] = Field(default_factory=list, description="List of ingredients with quantities, units, and macros per 1 unit")

    @classmethod
    def from_app_recipe(cls, recipe: Recipe) -> "RecipeSchema":
        return cls(
            id=recipe.id,
            name=recipe.name,
            instructions=recipe.instructions,
            servings=recipe.servings,
            ingredients=[IngredientSchema.from_app_ingredient(ing) for ing in recipe.ingredients],
        )

    def to_app_recipe(self) -> Recipe:
        app_ingredients = [ing.to_app_ingredient() for ing in self.ingredients]
        return Recipe(
            id=self.id,
            name=self.name,
            instructions=self.instructions,
            servings=max(1, self.servings),
            ingredients=app_ingredients,
        )


async def get_recipes() -> list[RecipeSchema]:
    """Returns the list of saved recipes including their ingredients, servings, and instructions."""
    print("get_recipes!!!")
    recipes_state = await state_accessor.get_recipes_state()
    return [RecipeSchema.from_app_recipe(r) for r in recipes_state.recipes]


async def add_recipe(recipe: RecipeSchema):
    """Create and save a new recipe with its ingredients, servings, and instructions."""
    print("add_recipe!!!")
    recipes_state = await state_accessor.get_recipes_state()
    app_recipe = recipe.to_app_recipe()
    if app_recipe.id <= 0:
        app_recipe.id = recipes_state.next_recipe_id()
    recipes_state.add_recipe(app_recipe)


async def update_recipe(recipe: RecipeSchema):
    """Update an existing saved recipe with the specified id."""
    print("update_recipe!!!")
    recipes_state = await state_accessor.get_recipes_state()
    recipes_state.update_recipe(recipe.to_app_recipe())


async def remove_recipe(id: int):
    """Remove a recipe from the saved recipes collection with the specified id."""
    print("remove_recipe!!!")
    recipes_state = await state_accessor.get_recipes_state()
    recipes_state.remove_recipe(id)


async def log_recipe_as_meal(recipe_id: int):
    """Log one serving of a saved recipe as an eaten meal for today."""
    print("log_recipe_as_meal!!!")
    recipes_state = await state_accessor.get_recipes_state()
    recipe = next((r for r in recipes_state.recipes if r.id == recipe_id), None)
    if recipe:
        await recipes_state.log_recipe_as_meal(recipe)


chat_instance = None
client = genai.Client()

SYS_PROMPT = """You are a helpful nutrition and fitness assistant.
- When the user states what they ate, calculate macros accurately and call add_meals immediately. Specify amount and unit (g, dkg, kg, ml, dl, l, serving).
- When the user asks to create or save a recipe, calculate all ingredients with their amounts, units, and macros per 1 unit, write clear step-by-step instructions, and call add_recipe.
- When the user asks about their saved recipes or meals, call get_recipes or get_meals.
- When the user asks to update or remove meals or recipes, use update_meal, remove_meal, update_recipe, or remove_recipe.
- When the user asks to log a saved recipe as a meal, call log_recipe_as_meal.
- Be concise, accurate with macros, and helpful."""

GEMINI_MODEL = "gemini-3.1-flash-lite"


def init_agent():
    global chat_instance, client
    chat_instance = client.aio.chats.create(
        model=GEMINI_MODEL,
        config={
            "tools": [
                get_meals,
                add_meals,
                update_meal,
                remove_meal,
                get_recipes,
                add_recipe,
                update_recipe,
                remove_recipe,
                log_recipe_as_meal,
            ],
            "system_instruction": SYS_PROMPT,
        },
    )


async def send_prompt(prompt: str) -> str:
    global chat_instance
    if chat_instance is None:
        init_agent()
    response = await chat_instance.send_message(prompt)
    return response.text or ""
    