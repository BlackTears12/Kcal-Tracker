import csv
import pathlib
from datetime import date, datetime
from kcal_tracker.data.meal import *
from kcal_tracker.states.profile_state import *
from kcal_tracker.data.recipe import Recipe, Ingredient
from collections import defaultdict
import itertools
from filelock import FileLock
from dataclasses import dataclass, field

STORAGE_DIR = "./data"

MEAL_FIELD_NAMES = ["name", "category", "calories",
                    "protein_g", "carbs_g", "fat_g", "amount", "unit", "date"]
PROFILE_FIELD_NAMES = ["target_kcal","target_protein", "target_carbs", "target_fat"]
RECIPES_FIELD_NAMES = ["name", "servings", "instructions", "ingredient_list"]

PROFILE_REPO_FIELD_NAMES = ["email", "nickname"]

@dataclass
class DataCache:
    user_id: str = ""
    meal_data: dict[date, list[Meal]] = field(
        default_factory=lambda: defaultdict(list))
    target_data: MacroProfile = field(default_factory=MacroProfile)


def _get_csv_path(user_id: str, filename: str):
    return pathlib.Path(STORAGE_DIR, user_id, filename)


data_cache: DataCache = DataCache()
recipes_csv_lock = FileLock(str(_get_csv_path("shared", "recipes.csv"))+".lock")


def load_structured(csv_path: pathlib.Path, field_names: list[str], loader) -> list:
    if not csv_path.exists():
        return []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, field_names)
        return [loader(row) for row in reader]


def save_structured(csv_path: pathlib.Path, field_names: list[str], data: list[dict]):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writerows(data)

# region data cache handling

def _save_meal_data_cache():
    if not data_cache.user_id:
        return
    csv_path = _get_csv_path(data_cache.user_id, "meals.csv")
    print(f"Saving meals to {str(csv_path.absolute())}")
    merged = list(itertools.chain.from_iterable(data_cache.meal_data.values()))
    data = [{"name": m.name,
             "category": m.category,
             "calories": m.macros.calories,
             "protein_g": m.macros.protein,
             "carbs_g": m.macros.carbs,
             "fat_g": m.macros.fat,
             "date": m.date.isoformat(),
             "amount": m.amount,
             "unit": m.unit.unit} for m in merged]
    save_structured(csv_path, MEAL_FIELD_NAMES, data)


def _load_meal_data_cache(user_id: str) -> dict[date, list[Meal]]:
    csv_path = _get_csv_path(user_id, "meals.csv")    
    print(f"Loading meals from {csv_path}")
    meal_data = defaultdict(list)
    meals = load_structured(csv_path, MEAL_FIELD_NAMES, lambda row: Meal(
        name=row["name"],
        category=MealCategory(row["category"]),
        macros=MacroProfile(float(row["calories"]), float(row["protein_g"]),
                            float(row["carbs_g"]), float(row["fat_g"])),
        date=date.fromisoformat(row["date"]),
        amount=float(row["amount"]),
        unit=Unit(row["unit"])))
    for m in meals:
        meal_data[m.date].append(m)
    return meal_data

def _save_profile_data_cache(user_id: str):
    csv_path = _get_csv_path(user_id, "profile.csv")
    targets = data_cache.target_data
    with open(csv_path, "w") as f:
        writer = csv.DictWriter(f, PROFILE_FIELD_NAMES)
        writer.writerow({
            "target_kcal": targets.calories,
            "target_protein": targets.protein,
            "target_carbs": targets.carbs,
            "target_fat": targets.fat,
        })

def _load_profile_data_cache(user_id: str) -> MacroProfile:
    csv_path = _get_csv_path(user_id, "profile.csv")
    if not csv_path.exists():
        return MacroProfile()
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, PROFILE_FIELD_NAMES)
        row = next(reader)
        target = MacroProfile(
          calories=float(row["target_kcal"]),
          protein=float(row["target_protein"]),
          carbs=float(row["target_carbs"]),
          fat=float(row["target_fat"]))
        return target

def _load_data_cache(user_id: str) -> DataCache:
    global data_cache
    if data_cache.user_id != user_id:
        target = _load_profile_data_cache(user_id)
        data_cache = DataCache(
            user_id=user_id,
            meal_data=_load_meal_data_cache(user_id),
            target_data=target
            )        
    return data_cache

#endregion

#region data handling API

def save_meals(user_id: str, meals: list[Meal], date_context: date):
    data_cache.meal_data[date_context] = meals
    _save_meal_data_cache()


def load_meals(user_id: str, date_context: date) -> list[Meal]:    
    return _load_data_cache(user_id).meal_data[date_context]

def save_recipes(recipes: list[Recipe]):
    def ingr_str(ing: Ingredient):
        return ";".join([ing.name, str(ing.macros_per_unit.calories),
                         str(ing.macros_per_unit.protein), 
                         str(ing.macros_per_unit.carbs),
                         str(ing.macros_per_unit.fat), str(ing.amount), ing.unit.unit])
    csv_path = _get_csv_path("shared", "recipes.csv")
    print(f"Saving recipes to {csv_path}")
    data = [{
        "name": r.name,
        "servings": r.servings,
        "instructions": r.instructions,
        "ingredient_list": "|".join([ingr_str(i) for i in r.ingredients])
    } for r in recipes]
    with recipes_csv_lock:
        save_structured(csv_path, RECIPES_FIELD_NAMES, data)


def load_recipes():
    def ingr_from_str(s: str):
        parts = s.split(";")
        return Ingredient(name=parts[0], macros_per_unit=MacroProfile(
                float(parts[1]), float(parts[2]),
                float(parts[3]), float(parts[4])),
            amount=float(parts[5]), unit=Unit(parts[6]))
    csv_path = _get_csv_path("shared", "recipes.csv")
    print(f"Loading recipes from {csv_path}")
    with recipes_csv_lock:
        return load_structured(csv_path, RECIPES_FIELD_NAMES,
                               lambda row: Recipe(name=row["name"],servings=int(row["servings"]),
                                                  instructions=row["instructions"],
                                                  ingredients=[ingr_from_str(s) for s in row["ingredient_list"].split("|")]))

def save_targets(user_id: str, target: MacroProfile):
    data_cache.target_data = target
    _save_profile_data_cache(user_id)

def load_targets(user_id: str) -> MacroProfile:
    return _load_data_cache(user_id).target_data

def load_registered_profiles() -> list[Profile]:
    return load_structured(_get_csv_path("shared","profiles_repo.csv"),
                           PROFILE_REPO_FIELD_NAMES, lambda row: Profile(row["email"],row["nickname"]))

def adjust_logged_recipe_meal_instances(old_name: str, serving: Meal):
    merged = list(itertools.chain.from_iterable(data_cache.meal_data.values()))
    for m in merged:
        if m.name.lower().strip() == old_name.lower().strip():
            m.macros = serving.macros
            m.name = serving.name
    _save_meal_data_cache()

#endregion