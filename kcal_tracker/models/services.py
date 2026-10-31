"""Business logic for meals, workouts, targets, recipes, profiles and login sessions.

Plain Python with no Reflex dependency: the UI states and the AI agent both go through here.
"""
import csv
import hashlib
import pathlib
import secrets
import datetime as dt
from datetime import date
from sqlmodel import Session, col, select
from kcal_tracker.data.meal import *
from kcal_tracker.data.profile import Profile
from kcal_tracker.data.recipe import Recipe, Ingredient
from kcal_tracker.data.workout import Workout, WorkoutType
from kcal_tracker.models import db
from kcal_tracker.models.db import AuthSessionRow, IngredientRow, MealRow, RecipeRow, TargetRow, WorkoutRow

PROFILES_PATH = pathlib.Path("data", "shared", "profiles_repo.csv")


class DuplicateRecipeError(ValueError):
    pass


class RecipeNotFoundError(LookupError):
    pass


def _name_key(name: str) -> str:
    return name.strip().lower()


# region profiles

def load_profiles() -> list[Profile]:
    """Returns the allowed users, listed as `email, nickname` rows in profiles_repo.csv."""
    if not PROFILES_PATH.exists():
        return []
    with open(PROFILES_PATH, "r", encoding="utf-8", newline="") as f:
        return [Profile(email=row[0].strip().lower(), name=row[1].strip() if len(row) > 1 else "")
                for row in csv.reader(f) if row and row[0].strip()]


def find_profile(email: str) -> Profile | None:
    email = email.strip().lower()
    return next((p for p in load_profiles() if p.email == email), None)

# endregion

# region login sessions

SESSION_LIFETIME = dt.timedelta(days=90)
# Sliding expiry: a used session is extended, but at most this often to avoid a write on every event
SESSION_RENEW_AFTER = dt.timedelta(days=1)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class SessionService:
    """Long-lived logins: the browser keeps a random token, the database only its hash."""

    def create(self, user_id: str, user_agent: str = "") -> str:
        """Starts a session for an already authenticated user and returns its token."""
        token = secrets.token_urlsafe(32)
        now = _now()
        with db.session() as s:
            for expired in s.exec(select(AuthSessionRow).where(AuthSessionRow.expires_at <= now)).all():
                s.delete(expired)
            s.add(AuthSessionRow(token_hash=_hash_token(token), user_id=user_id, created_at=now,
                                 last_seen_at=now, expires_at=now + SESSION_LIFETIME, user_agent=user_agent[:200]))
            s.commit()
        return token

    def validate(self, token: str) -> str | None:
        """Returns the user id of a live session, or None. Sessions of users no longer allowed are revoked."""
        if not token:
            return None
        now = _now()
        with db.session() as s:
            row = s.get(AuthSessionRow, _hash_token(token))
            if row is None:
                return None
            if row.expires_at <= now or find_profile(row.user_id) is None:
                s.delete(row)
                s.commit()
                return None
            if now - row.last_seen_at >= SESSION_RENEW_AFTER:
                row.last_seen_at, row.expires_at = now, now + SESSION_LIFETIME
                s.add(row)
                s.commit()
            return row.user_id

    def revoke(self, token: str) -> bool:
        if not token:
            return False
        with db.session() as s:
            row = s.get(AuthSessionRow, _hash_token(token))
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def revoke_all(self, user_id: str) -> int:
        with db.session() as s:
            rows = s.exec(select(AuthSessionRow).where(AuthSessionRow.user_id == user_id)).all()
            for r in rows:
                s.delete(r)
            s.commit()
            return len(rows)

# endregion

# region meals & targets

def _meal_from_row(row: MealRow) -> Meal:
    return Meal(
        id=row.id or 0,
        name=row.name,
        category=MealCategory(row.category),
        macros=MacroProfile(row.calories, row.protein, row.carbs, row.fat),
        date=row.date,
        amount=row.amount,
        unit=Unit(row.unit),
        recipe_id=row.recipe_id,
    )


def _editable_meal_fields(meal: Meal) -> dict:
    """Fields a meal edit may change, its owner, date and recipe link stay fixed."""
    return {
        "name": meal.name.strip(),
        "category": MealCategory(meal.category).value,
        "calories": meal.macros.calories,
        "protein": meal.macros.protein,
        "carbs": meal.macros.carbs,
        "fat": meal.macros.fat,
        "amount": meal.amount,
        "unit": meal.unit.unit,
    }


def _workout_from_row(row: WorkoutRow) -> Workout:
    return Workout(
        id=row.id or 0,
        name=row.name,
        type=WorkoutType(row.type),
        duration_min=row.duration_min,
        calories_burned=row.calories_burned,
        date=row.date,
    )


def _editable_workout_fields(workout: Workout) -> dict:
    """Fields a workout edit may change, its owner and date stay fixed."""
    return {
        "name": workout.name.strip(),
        "type": WorkoutType(workout.type).value,
        "duration_min": max(0.0, float(workout.duration_min)),
        "calories_burned": max(0.0, float(workout.calories_burned)),
    }


class NutritionService:
    """Meals, workouts and daily targets of a single user."""

    def __init__(self, user_id: str):
        if not user_id:
            raise ValueError("user_id is required")
        self.user_id = user_id

    def meals_on(self, day: date) -> list[Meal]:
        with db.session() as s:
            rows = s.exec(select(MealRow)
                          .where(MealRow.user_id == self.user_id, MealRow.date == day)
                          .order_by(col(MealRow.id))).all()
            return [_meal_from_row(r) for r in rows]

    def get_meal(self, meal_id: int) -> Meal | None:
        with db.session() as s:
            row = self._own_meal_row(s, meal_id)
            return _meal_from_row(row) if row else None

    def add_meals(self, meals: list[Meal], day: date) -> list[Meal]:
        with db.session() as s:
            rows = [MealRow(user_id=self.user_id, date=day, recipe_id=m.recipe_id, **_editable_meal_fields(m))
                    for m in meals]
            s.add_all(rows)
            s.commit()
            for r in rows:
                s.refresh(r)
            return [_meal_from_row(r) for r in rows]

    def update_meal(self, meal: Meal) -> Meal | None:
        """Updates the logged meal with the same id, returns None if the user has no such meal."""
        with db.session() as s:
            row = self._own_meal_row(s, meal.id)
            if row is None:
                return None
            for key, value in _editable_meal_fields(meal).items():
                setattr(row, key, value)
            s.add(row)
            s.commit()
            s.refresh(row)
            return _meal_from_row(row)

    def remove_meal(self, meal_id: int) -> bool:
        with db.session() as s:
            row = self._own_meal_row(s, meal_id)
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def clear_day(self, day: date) -> int:
        with db.session() as s:
            rows = s.exec(select(MealRow).where(MealRow.user_id == self.user_id, MealRow.date == day)).all()
            for r in rows:
                s.delete(r)
            s.commit()
            return len(rows)

    def log_recipe(self, recipe: Recipe, day: date, servings: float = 1.0,
                   category: MealCategory = MealCategory.Lunch) -> Meal:
        meal = Meal(
            name=recipe.name,
            category=category,
            macros=recipe.macros_per_serving().scale(servings),
            amount=servings,
            unit=Unit("serving"),
            recipe_id=recipe.id or None,
        )
        return self.add_meals([meal], day)[0]

    def workouts_on(self, day: date) -> list[Workout]:
        with db.session() as s:
            rows = s.exec(select(WorkoutRow)
                          .where(WorkoutRow.user_id == self.user_id, WorkoutRow.date == day)
                          .order_by(col(WorkoutRow.id))).all()
            return [_workout_from_row(r) for r in rows]

    def get_workout(self, workout_id: int) -> Workout | None:
        with db.session() as s:
            row = self._own_workout_row(s, workout_id)
            return _workout_from_row(row) if row else None

    def add_workouts(self, workouts: list[Workout], day: date) -> list[Workout]:
        with db.session() as s:
            rows = [WorkoutRow(user_id=self.user_id, date=day, **_editable_workout_fields(w)) for w in workouts]
            s.add_all(rows)
            s.commit()
            for r in rows:
                s.refresh(r)
            return [_workout_from_row(r) for r in rows]

    def update_workout(self, workout: Workout) -> Workout | None:
        """Updates the logged workout with the same id, returns None if the user has no such workout."""
        with db.session() as s:
            row = self._own_workout_row(s, workout.id)
            if row is None:
                return None
            for key, value in _editable_workout_fields(workout).items():
                setattr(row, key, value)
            s.add(row)
            s.commit()
            s.refresh(row)
            return _workout_from_row(row)

    def remove_workout(self, workout_id: int) -> bool:
        with db.session() as s:
            row = self._own_workout_row(s, workout_id)
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def get_targets(self) -> MacroProfile:
        with db.session() as s:
            row = s.get(TargetRow, self.user_id)
            return MacroProfile(row.calories, row.protein, row.carbs, row.fat) if row else MacroProfile()

    def set_targets(self, targets: MacroProfile) -> MacroProfile:
        targets = MacroProfile(
            calories=max(500.0, float(targets.calories)),
            protein=max(10.0, float(targets.protein)),
            carbs=max(10.0, float(targets.carbs)),
            fat=max(5.0, float(targets.fat)),
        )
        with db.session() as s:
            row = s.get(TargetRow, self.user_id) or TargetRow(user_id=self.user_id)
            row.calories, row.protein, row.carbs, row.fat = targets.calories, targets.protein, targets.carbs, targets.fat
            s.add(row)
            s.commit()
        return targets

    def _own_meal_row(self, s: Session, meal_id: int) -> MealRow | None:
        row = s.get(MealRow, meal_id)
        return row if row is not None and row.user_id == self.user_id else None

    def _own_workout_row(self, s: Session, workout_id: int) -> WorkoutRow | None:
        row = s.get(WorkoutRow, workout_id)
        return row if row is not None and row.user_id == self.user_id else None

# endregion

# region recipes

def _ingredient_rows(recipe_id: int, ingredients: list[Ingredient]) -> list[IngredientRow]:
    return [IngredientRow(
        recipe_id=recipe_id,
        position=i,
        name=ing.name.strip(),
        amount=ing.amount,
        unit=ing.unit.unit,
        calories_per_unit=ing.macros_per_unit.calories,
        protein_per_unit=ing.macros_per_unit.protein,
        carbs_per_unit=ing.macros_per_unit.carbs,
        fat_per_unit=ing.macros_per_unit.fat,
    ) for i, ing in enumerate(ingredients)]


def _recipe_from_rows(row: RecipeRow, ingredient_rows: list[IngredientRow]) -> Recipe:
    return Recipe(
        id=row.id or 0,
        name=row.name,
        servings=row.servings,
        instructions=row.instructions,
        ingredients=[Ingredient(
            name=i.name,
            macros_per_unit=MacroProfile(i.calories_per_unit, i.protein_per_unit, i.carbs_per_unit, i.fat_per_unit),
            amount=i.amount,
            unit=Unit(i.unit),
        ) for i in sorted(ingredient_rows, key=lambda i: i.position)],
    )


class RecipeService:
    """Recipes are shared between all users."""

    def list_recipes(self) -> list[Recipe]:
        with db.session() as s:
            rows = s.exec(select(RecipeRow).order_by(col(RecipeRow.id))).all()
            ingredients: dict[int, list[IngredientRow]] = {}
            for ing in s.exec(select(IngredientRow)).all():
                ingredients.setdefault(ing.recipe_id, []).append(ing)
            return [_recipe_from_rows(r, ingredients.get(r.id or 0, [])) for r in rows]

    def get_recipe(self, name: str) -> Recipe | None:
        with db.session() as s:
            row = self._row_by_name(s, name)
            return self._load(s, row) if row else None

    def get_recipe_by_id(self, recipe_id: int) -> Recipe | None:
        with db.session() as s:
            row = s.get(RecipeRow, recipe_id)
            return self._load(s, row) if row else None

    def add_recipe(self, recipe: Recipe) -> Recipe:
        with db.session() as s:
            if self._row_by_name(s, recipe.name):
                raise DuplicateRecipeError(f"A recipe with the name '{recipe.name.strip()}' already exists.")
            row = RecipeRow(name=recipe.name.strip(), name_key=_name_key(recipe.name),
                            servings=max(1, int(recipe.servings)), instructions=recipe.instructions.strip())
            s.add(row)
            s.flush()
            s.add_all(_ingredient_rows(row.id or 0, recipe.ingredients))
            s.commit()
            return self._load(s, row)

    def update_recipe(self, recipe: Recipe, adjust_logged_meals: bool = True) -> Recipe:
        """Replaces the recipe with the same id. When adjust_logged_meals is set, every meal logged
        from this recipe (by any user) gets the new name and macros for its number of servings."""
        with db.session() as s:
            row = s.get(RecipeRow, recipe.id)
            if row is None:
                raise RecipeNotFoundError(f"No recipe with id {recipe.id}.")
            other = self._row_by_name(s, recipe.name)
            if other is not None and other.id != row.id:
                raise DuplicateRecipeError(f"A recipe with the name '{recipe.name.strip()}' already exists.")
            row.name, row.name_key = recipe.name.strip(), _name_key(recipe.name)
            row.servings = max(1, int(recipe.servings))
            row.instructions = recipe.instructions.strip()
            s.add(row)
            for old in s.exec(select(IngredientRow).where(IngredientRow.recipe_id == row.id)).all():
                s.delete(old)
            s.add_all(_ingredient_rows(row.id or 0, recipe.ingredients))
            s.flush()
            updated = self._load(s, row)

            if adjust_logged_meals:
                per_serving = updated.macros_per_serving()
                for meal in s.exec(select(MealRow).where(MealRow.recipe_id == row.id)).all():
                    meal.name = updated.name
                    # Meals switched to a weight/volume unit can't be mapped to servings, keep their macros
                    if meal.unit == "serving":
                        scaled = per_serving.scale(meal.amount)
                        meal.calories, meal.protein, meal.carbs, meal.fat = scaled.calories, scaled.protein, scaled.carbs, scaled.fat
                    s.add(meal)
            s.commit()
            return updated

    def remove_recipe(self, name: str) -> bool:
        """Deletes the recipe, meals logged from it keep their macros."""
        with db.session() as s:
            row = self._row_by_name(s, name)
            if row is None:
                return False
            for meal in s.exec(select(MealRow).where(MealRow.recipe_id == row.id)).all():
                meal.recipe_id = None
                s.add(meal)
            for ing in s.exec(select(IngredientRow).where(IngredientRow.recipe_id == row.id)).all():
                s.delete(ing)
            s.delete(row)
            s.commit()
            return True

    def _row_by_name(self, s: Session, name: str) -> RecipeRow | None:
        return s.exec(select(RecipeRow).where(RecipeRow.name_key == _name_key(name))).first()

    def _load(self, s: Session, row: RecipeRow) -> Recipe:
        ingredients = s.exec(select(IngredientRow).where(IngredientRow.recipe_id == row.id)).all()
        return _recipe_from_rows(row, list(ingredients))

# endregion
