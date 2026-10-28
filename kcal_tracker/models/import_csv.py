"""One-time import of the old CSV storage into the SQLite database.

Run from the project root: python -m kcal_tracker.models.import_csv
Users whose meals are already in the database and recipes with an existing name are skipped,
so running it twice is safe.
"""
import csv
import pathlib
from datetime import date
import unidecode
from sqlmodel import select
from kcal_tracker.data.meal import *
from kcal_tracker.data.recipe import Recipe, Ingredient
from kcal_tracker.models import db
from kcal_tracker.models.db import MealRow
from kcal_tracker.models.services import (DuplicateRecipeError, NutritionService, RecipeService,
                                          load_profiles)

LEGACY_DIR = pathlib.Path("data")


def _rows(path: pathlib.Path) -> list[list[str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return [row for row in csv.reader(f) if row]


def _legacy_user_dir(nickname: str) -> pathlib.Path | None:
    # The old app keyed user folders by the lowercased ascii nickname, possibly with stray whitespace
    for name in (unidecode.unidecode(nickname).lower(), unidecode.unidecode(nickname).lower().strip(),
                 " " + unidecode.unidecode(nickname).lower().strip()):
        if (LEGACY_DIR / name).is_dir():
            return LEGACY_DIR / name
    return None


def import_recipes(service: RecipeService) -> int:
    count = 0
    for name, servings, instructions, ingredient_list in _rows(LEGACY_DIR / "shared" / "recipes.csv"):
        ingredients = []
        for part in filter(None, ingredient_list.split("|")):
            n, cal, p, c, f, amount, unit = part.split(";")
            ingredients.append(Ingredient(n, MacroProfile(float(cal), float(p), float(c), float(f)),
                                          float(amount), Unit(unit)))
        try:
            service.add_recipe(Recipe(name=name, servings=int(servings), instructions=instructions,
                                      ingredients=ingredients))
            count += 1
        except DuplicateRecipeError:
            pass
    return count


def import_user(email: str, user_dir: pathlib.Path, recipes: RecipeService) -> int:
    service = NutritionService(email)
    with db.session() as s:
        if s.exec(select(MealRow).where(MealRow.user_id == email)).first():
            print(f"  {email}: already has meals in the database, skipped")
            return 0

    targets = _rows(user_dir / "profile.csv")
    if targets:
        service.set_targets(MacroProfile(*(float(v) for v in targets[0][:4])))

    by_day: dict[date, list[Meal]] = {}
    for name, category, cal, p, c, f, amount, unit, day in _rows(user_dir / "meals.csv"):
        # The old app linked recipe meals to recipes only by name
        recipe = recipes.get_recipe(name) if unit == "serving" else None
        meal = Meal(name=name, category=MealCategory(category),
                    macros=MacroProfile(float(cal), float(p), float(c), float(f)),
                    amount=float(amount), unit=Unit(unit), recipe_id=recipe.id if recipe else None)
        by_day.setdefault(date.fromisoformat(day), []).append(meal)
    for day, meals in by_day.items():
        service.add_meals(meals, day)
    return sum(len(m) for m in by_day.values())


def main():
    recipes = RecipeService()
    print(f"Imported {import_recipes(recipes)} recipes")
    for profile in load_profiles():
        user_dir = _legacy_user_dir(profile.name)
        if user_dir is None:
            print(f"  {profile.email}: no legacy data folder found")
            continue
        print(f"  {profile.email}: imported {import_user(profile.email, user_dir, recipes)} meals from {user_dir}")


if __name__ == "__main__":
    main()
