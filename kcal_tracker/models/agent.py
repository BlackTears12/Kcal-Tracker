from google import genai
from pydantic import BaseModel, Field
from typing import cast
from kcal_tracker.states.nutrition_state import Meal, MealCategory, NutritionState, MacroProfile
import kcal_tracker.state_accessor as state_accessor


class MealSchema(BaseModel):
    name: str = Field(description="Name of the meal")
    calories: float = Field(description="Amount kcal of calories contained in the meal")
    protein_g: float = Field(description="grams of protein contained in the meal")
    carbs_g: float = Field(description="grams of carbs contained in the meal")
    fat_g: float = Field(description="grams of fat contained in the meal")

    @classmethod
    def from_app_meal(cls, meal: Meal):
        return cls(name=meal.name,
                   calories=meal.macros.calories,
                   protein_g=meal.macros.protein,
                   carbs_g=meal.macros.carbs,
                   fat_g=meal.macros.fat)
      
    def to_app_meal(self) -> Meal:
      return Meal(
          name=self.name,
          category=MealCategory.Breakfast,
          macros = MacroProfile(
              self.calories, self.protein_g, self.carbs_g, self.fat_g
          )
      )


async def get_meals(category: str="all") -> list[MealSchema]:
    """Returns the list of meals registered

    Args: 
        category: optional meal category to filter by by (breakfast, lunch, dinner, snack)
    """
    print("get_meals!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    return [MealSchema.from_app_meal(app_meal) for app_meal in nutrition_state.logged_meals]

async def add_meals(meals: list[MealSchema]):
    """Register a list of meals eaten by the user today"""
    print("add_meals!!!")
    nutrition_state = await state_accessor.get_nutrition_state()
    nutrition_state.add_meal_list([m.to_app_meal() for m in meals])

chat_instance = None
client = genai.Client()

SYS_PROMPT="Help the user by logging their meal if they ask, and respond kindly \
  When the user states what they ate, calculate macros and call add_meals immediately. \
  Do NOT call get_meals unless the user explicitly asks about \
  their previous meals or daily totals."

def init_agent():
    global chat_instance, client
    chat_instance = client.aio.chats.create(
        model="gemini-3.6-flash",
        config={"tools": [get_meals, add_meals],
                "system_instruction": SYS_PROMPT},
    )

async def send_prompt(prompt: str) -> str:
    global chat_instance
    response = await chat_instance.send_message(prompt)
    return response.text or ""
    