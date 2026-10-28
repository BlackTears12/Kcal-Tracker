from contextvars import ContextVar
from dataclasses import dataclass
from datetime import date
from google import genai
from pydantic import BaseModel, Field
from PIL import Image
from kcal_tracker.data.meal import *
from kcal_tracker.data.recipe import Recipe, Ingredient
from kcal_tracker.models.services import DuplicateRecipeError, NutritionService, RecipeService


@dataclass
class AgentContext:
    user_id: str
    day: date


# The user and viewed day of the prompt being answered, read by the tools below
_context: ContextVar[AgentContext] = ContextVar("agent_context")


def _nutrition() -> NutritionService:
    return NutritionService(_context.get().user_id)


class MealSchema(BaseModel):
    id: int = Field(default=0, description="The ID of the already logged meal, not used when logging a new meal")
    name: str = Field(description="Name of the meal")
    category: str = Field(default="Breakfast", description="Meal category: Breakfast, Lunch, Dinner, or Snack")
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
            category=meal.category.value,
            calories=meal.macros.calories,
            protein_g=meal.macros.protein,
            carbs_g=meal.macros.carbs,
            fat_g=meal.macros.fat,
            amount=meal.amount,
            unit=meal.unit.unit if isinstance(meal.unit, Unit) else str(meal.unit),
        )

    def to_app_meal(self) -> Meal:
        category = MealCategory.Breakfast
        try:
            category = MealCategory(self.category.strip().capitalize())
        except ValueError:
            pass
        return Meal(
            id=self.id,
            name=self.name,
            category=category,
            macros=MacroProfile(
                self.calories, self.protein_g, self.carbs_g, self.fat_g
            ),
            amount=self.amount,
            unit=Unit(self.unit),
        )


async def get_meals(category: str = "all") -> list[MealSchema]:
    """Returns the meals logged on the day the user is viewing.

    Args:
        category: optional meal category to filter by (breakfast, lunch, dinner, snack, or all)
    """
    meals = _nutrition().meals_on(_context.get().day)
    if category.strip().lower() != "all":
        meals = [m for m in meals if m.category.value.lower() == category.strip().lower()]
    return [MealSchema.from_app_meal(m) for m in meals]


async def add_meals(meals: list[MealSchema]) -> str:
    """Log a list of meals eaten by the user on the day they are viewing"""
    added = _nutrition().add_meals([m.to_app_meal() for m in meals], _context.get().day)
    return "Logged meals: " + ", ".join(f"{m.name} (id {m.id})" for m in added)


async def update_meal(meal: MealSchema) -> str:
    """Update a logged meal with the same id"""
    updated = _nutrition().update_meal(meal.to_app_meal())
    return f"Updated meal '{updated.name}'." if updated else f"Error: no logged meal with id {meal.id}."


async def remove_meal(id: int) -> str:
    """Remove the meal from the log with the specified id"""
    return "Meal removed." if _nutrition().remove_meal(id) else f"Error: no logged meal with id {id}."


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
    name: str = Field(description="Name of the recipe (unique identifier)")
    instructions: str = Field(default="", description="Detailed preparation and cooking instructions for the recipe")
    servings: int = Field(default=1, description="Amount of servings produced by the recipe")
    ingredients: list[IngredientSchema] = Field(default_factory=list, description="List of ingredients with quantities, units, and macros per 1 unit")

    @classmethod
    def from_app_recipe(cls, recipe: Recipe) -> "RecipeSchema":
        return cls(
            name=recipe.name,
            instructions=recipe.instructions,
            servings=recipe.servings,
            ingredients=[IngredientSchema.from_app_ingredient(ing) for ing in recipe.ingredients],
        )

    def to_app_recipe(self) -> Recipe:
        app_ingredients = [ing.to_app_ingredient() for ing in self.ingredients]
        return Recipe(
            name=self.name,
            instructions=self.instructions,
            servings=max(1, self.servings),
            ingredients=app_ingredients,
        )


async def get_recipes() -> list[RecipeSchema]:
    """Returns the list of saved recipes including their ingredients, servings, and instructions."""
    return [RecipeSchema.from_app_recipe(r) for r in RecipeService().list_recipes()]


async def add_recipe(recipe: RecipeSchema) -> str:
    """Create and save a new recipe with its ingredients, servings, and instructions. Recipe names must be unique."""
    try:
        RecipeService().add_recipe(recipe.to_app_recipe())
    except DuplicateRecipeError as e:
        return f"Error: {e}"
    return f"Successfully saved recipe '{recipe.name}'."


async def update_recipe(recipe: RecipeSchema, adjust_logged_meals: bool = True) -> str:
    """Update an existing saved recipe with the specified name.

    Args:
        recipe: the full new version of the recipe
        adjust_logged_meals: also update the name and macros of meals already logged from this recipe
    """
    service = RecipeService()
    existing = service.get_recipe(recipe.name)
    if existing is None:
        return f"Error: no saved recipe named '{recipe.name}'."
    app_recipe = recipe.to_app_recipe()
    app_recipe.id = existing.id
    service.update_recipe(app_recipe, adjust_logged_meals=adjust_logged_meals)
    return f"Updated recipe '{recipe.name}'."


async def remove_recipe(name: str) -> str:
    """Remove a recipe from the saved recipes collection with the specified name."""
    return "Recipe removed." if RecipeService().remove_recipe(name) else f"Error: no saved recipe named '{name}'."


async def log_recipe_as_meal(recipe_name: str, servings: float = 1.0) -> str:
    """Log servings of a saved recipe as an eaten meal on the day the user is viewing.

    Args:
        recipe_name: name of the saved recipe
        servings: number of servings eaten
    """
    recipe = RecipeService().get_recipe(recipe_name)
    if recipe is None:
        return f"Error: no saved recipe named '{recipe_name}'."
    meal = _nutrition().log_recipe(recipe, _context.get().day, servings)
    return f"Logged {servings:g} serving(s) of '{recipe.name}' (meal id {meal.id})."


class TargetMacrosSchema(BaseModel):
    calories: float | None = Field(default=None, description="Daily target calories in kcal")
    protein_g: float | None = Field(default=None, description="Daily target protein in grams")
    carbs_g: float | None = Field(default=None, description="Daily target carbohydrates in grams")
    fat_g: float | None = Field(default=None, description="Daily target fat in grams")

    @classmethod
    def from_macro_profile(cls, profile: MacroProfile) -> "TargetMacrosSchema":
        return cls(
            calories=profile.calories,
            protein_g=profile.protein,
            carbs_g=profile.carbs,
            fat_g=profile.fat,
        )


async def get_target_macros() -> TargetMacrosSchema:
    """Returns the user's daily target nutritional macros (calories in kcal, protein in grams, carbs in grams, fat in grams)."""
    return TargetMacrosSchema.from_macro_profile(_nutrition().get_targets())


async def set_target_macros(
    target: TargetMacrosSchema
) -> str:
    """Set or update the user's daily target nutritional macros. Any omitted/unspecified macro parameters will keep their current target values."""
    service = _nutrition()
    current = service.get_targets()
    saved = service.set_targets(MacroProfile(
        calories=current.calories if target.calories is None else target.calories,
        protein=current.protein if target.protein_g is None else target.protein_g,
        carbs=current.carbs if target.carbs_g is None else target.carbs_g,
        fat=current.fat if target.fat_g is None else target.fat_g,
    ))
    return (
        f"Daily target macros successfully updated (minimums: 500 kcal, 10g protein, 10g carbs, 5g fat): "
        f"Calories: {round(saved.calories)} kcal, "
        f"Protein: {round(saved.protein)}g, "
        f"Carbs: {round(saved.carbs)}g, "
        f"Fat: {round(saved.fat)}g"
    )


client = genai.Client()
# One conversation per user
_chats: dict[str, genai.chats.AsyncChat] = {}

SYS_PROMPT = """You are a helpful nutrition and fitness assistant.
- When the user states what they ate, calculate macros accurately and call add_meals immediately. Specify amount and unit (g, dkg, kg, ml, dl, l, serving).
- When the user asks to create or save a recipe, calculate all ingredients with their amounts, units, and macros per 1 unit, write clear step-by-step instructions, and call add_recipe. Recipes are uniquely identified by their name.
- When the user asks about their saved recipes or meals, call get_recipes or get_meals.
- When the user asks to update or remove meals or recipes, use update_meal, remove_meal, update_recipe, or remove_recipe (recipes are identified by name).
- When the user asks to log a saved recipe as a meal, call log_recipe_as_meal with the recipe name.
- When the user asks about their daily target macros or calorie/macro goals, call get_target_macros.
- When the user asks to set, update, or adjust their daily target macros (calories, protein, carbs, fat), call set_target_macros.
- Be concise, accurate with macros, and helpful."""

GEMINI_MODEL = "gemini-3.1-flash-lite"


def _create_chat() -> genai.chats.AsyncChat:
    return client.aio.chats.create(
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
                get_target_macros,
                set_target_macros,
            ],
            "system_instruction": SYS_PROMPT,
        },
    )


def reset_chat(user_id: str):
    _chats.pop(user_id, None)


async def send_prompt(user_id: str, day: date, prompt: str, image_path="") -> str:
    """Sends the prompt to the user's conversation, tools act on that user's data for the given day."""
    chat = _chats.get(user_id)
    if chat is None:
        chat = _chats[user_id] = _create_chat()
    content = prompt
    if image_path:
        img = Image.open(image_path)
        content = [img, prompt]
    token = _context.set(AgentContext(user_id=user_id, day=day))
    try:
        response = await chat.send_message(content)  # type: ignore
    finally:
        _context.reset(token)
    return response.text or ""
