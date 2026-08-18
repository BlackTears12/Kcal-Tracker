import reflex as rx
from kcal_tracker.states.nutrition_state import NutritionState, TargetDialogState, MealDialogState
from kcal_tracker.states.recipes_state import RecipesState, RecipeDialogState
from kcal_tracker.states.chat_state import ChatState
from kcal_tracker.states.ui_state import UIState

_context = None

def init(context: rx.State):
    global _context
    _context = context

async def get_user():
    return _context

async def get_nutrition_state() -> NutritionState:
    return await _context.get_state(NutritionState)


async def get_recipes_state() -> RecipesState:
    return await _context.get_state(RecipesState)


async def get_chat_state() -> ChatState:
    return await _context.get_state(ChatState)


async def get_ui_state() -> UIState:
    return await _context.get_state(UIState)


async def get_meal_dialog_state() -> MealDialogState:
    return await _context.get_state(MealDialogState)


async def get_recipe_dialog_state() -> RecipeDialogState:
    return await _context.get_state(RecipeDialogState)


async def get_target_dialog_state() -> TargetDialogState:
    return await _context.get_state(TargetDialogState)
