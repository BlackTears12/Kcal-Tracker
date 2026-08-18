import csv
import pathlib
from datetime import date, datetime
from kcal_tracker.data.meal import *
from collections import defaultdict
import itertools
from dataclasses import dataclass, field

STORAGE_DIR="./data"

MEAL_FIELD_NAMES = ["name","category","calories","protein_g","carbs_g","fat_g","time"]

@dataclass
class DataCache:
    user_id: str = ""
    meal_data: dict[date, list[Meal]] = field(default_factory=lambda: defaultdict(list))

data_cache: DataCache = DataCache()

def _get_csv_path(user_id: str):
    return pathlib.Path(STORAGE_DIR, user_id, "meals.csv")

def save_data_cache():
    if not data_cache.user_id:
        return
    csv_path = _get_csv_path(data_cache.user_id)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving meals to {str(csv_path.absolute())}")
    with open(csv_path, "w") as f:
        writer = csv.DictWriter(f, MEAL_FIELD_NAMES)
        merged = list(itertools.chain.from_iterable(data_cache.meal_data.values()))
        for m in merged:
            writer.writerow({
                "name": m.name,
                "category": m.category,
                "calories": m.macros.calories,
                "protein_g": m.macros.protein,
                "carbs_g": m.macros.carbs,
                "fat_g": m.macros.fat,
                "time": m.time.isoformat()
            })

def load_data_cache(user_id: str) -> DataCache:
    csv_path = _get_csv_path(user_id)
    cache = DataCache(user_id=user_id)
    if not csv_path.exists():
        return cache
    print(f"Loading meals from {csv_path}")
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, MEAL_FIELD_NAMES)
        for row in reader:
            time_val = datetime.now()
            if row.get("time"):
                try:
                    time_val = datetime.fromisoformat(row["time"])
                except ValueError:
                    time_val = datetime.now()
            meal = Meal(
                name=row["name"],
                category=MealCategory(row["category"]),
                macros=MacroProfile(float(row["calories"]), float(row["protein_g"]),
                                    float(row["carbs_g"]), float(row["fat_g"])),
                time=time_val
            )
            cache.meal_data[time_val.date()].append(meal)
    return cache


def save_meals(user_id: str, meals: list[Meal], date_context: date):
    global data_cache
    if data_cache.user_id != user_id:
        data_cache = load_data_cache(user_id)
    data_cache.meal_data[date_context] = meals
    save_data_cache()

def load_meals(user_id: str, date_context: date) -> list[Meal]:
    global data_cache
    if data_cache.user_id != user_id:
        data_cache = load_data_cache(user_id)
    return data_cache.meal_data[date_context]