import csv
import pathlib
from kcal_tracker.data.meal import *

STORAGE_DIR="./data"

MEAL_FIELD_NAMES = ["name","category","calories","protein_g","carbs_g","fat_g"]

class DataRepository:
    def __init__(self, user_id: str) -> None:        
        self.csv_path = pathlib.Path(STORAGE_DIR,user_id,"meals.csv")

    def save_meals(self, meals: list[Meal]):
        print(f"Saving meals to {str(self.csv_path.absolute())}")
        with open(self.csv_path,"w") as f:
            writer = csv.DictWriter(f,MEAL_FIELD_NAMES)
            for m in meals:
                writer.writerow({
                    "name": m.name,
                    "category": m.category,
                    "calories": m.macros.calories,
                    "protein_g": m.macros.protein,
                    "carbs_g": m.macros.carbs,
                    "fat_g": m.macros.fat
                })

    def load_meals(self) -> list[Meal]:
        if not self.csv_path.exists():
            return []
        print(f"Loading meals from {self.csv_path}")
        with open(self.csv_path,"r") as f:
            reader = csv.DictReader(f, MEAL_FIELD_NAMES)
            return [Meal(
                name=row["name"],
                category=MealCategory(row["category"]),
                macros = MacroProfile(float(row["calories"]),float(row["protein_g"]),
                                      float(row["carbs_g"]),float(row["fat_g"]))
            ) for row in reader]