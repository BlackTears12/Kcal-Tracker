import csv
import pathlib
from datetime import date, datetime
from kcal_tracker.data.meal import *
from kcal_tracker.data.profiledata import *
from collections import defaultdict
import itertools
from dataclasses import dataclass, field

STORAGE_DIR="./data"

MEAL_FIELD_NAMES = ["name","category","calories","protein_g","carbs_g","fat_g","date"]
PROFILE_FIELD_NAMES = ["target_kcal","target_protein","target_carbs", "target_fat"]

@dataclass
class DataCache:
    user_id: str = ""
    meal_data: dict[date, list[Meal]] = field(default_factory=lambda: defaultdict(list))

data_cache: DataCache = DataCache()

def _get_csv_path(user_id: str, filename: str):
    return pathlib.Path(STORAGE_DIR, user_id, filename)

def save_data_cache():
    if not data_cache.user_id:
        return
    csv_path = _get_csv_path(data_cache.user_id, "meals.csv")
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
                "date": m.date.isoformat()
            })

def load_data_cache(user_id: str) -> DataCache:
    csv_path = _get_csv_path(user_id, "meals.csv")
    cache = DataCache(user_id=user_id)
    if not csv_path.exists():
        return cache
    print(f"Loading meals from {csv_path}")
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, MEAL_FIELD_NAMES)
        for row in reader:
            date_val = date.fromisoformat(row["date"])
            meal = Meal(
                name=row["name"],
                category=MealCategory(row["category"]),
                macros=MacroProfile(float(row["calories"]), float(row["protein_g"]),
                                    float(row["carbs_g"]), float(row["fat_g"])),
                date=date_val
            )
            cache.meal_data[date_val].append(meal)
    return cache


def save_meals(user_id: str, meals: list[Meal], date_context: date):
    data_cache.meal_data[date_context] = meals
    save_data_cache()

def load_meals(user_id: str, date_context: date) -> list[Meal]:
    global data_cache
    if data_cache.user_id != user_id:
        data_cache = load_data_cache(user_id)
    return data_cache.meal_data[date_context]

def load_profile_data(user_id: str) -> ProfileData:
    csv_path = _get_csv_path(user_id, "profile.csv")
    if not csv_path.exists():
        return ProfileData()
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, PROFILE_FIELD_NAMES)
        row = next(reader)
        return ProfileData(
            targets=MacroProfile(
                calories=float(row["target_kcal"]),
                protein=float(row["target_protein"]),
                carbs=float(row["target_carbs"]),
                fat=float(row["target_fat"])
            )
        )

def save_profile_data(user_id: str, data: ProfileData):
    csv_path = _get_csv_path(user_id, "profile.csv")
    with open(csv_path, "w") as f:
        writer = csv.DictWriter(f, PROFILE_FIELD_NAMES)
        writer.writerow({
            "target_kcal": data.targets.calories,
            "target_protein": data.targets.protein,
            "target_carbs": data.targets.carbs,
            "target_fat": data.targets.fat,
        })