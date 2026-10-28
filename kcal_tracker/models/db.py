"""SQLite persistence: table definitions and session factory."""
import datetime
import pathlib
from sqlmodel import Field, Session, SQLModel, create_engine

DB_PATH = pathlib.Path("data", "kcal.db")


class MealRow(SQLModel, table=True):
    __tablename__ = "meal"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    date: datetime.date = Field(index=True)
    name: str
    category: str
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    amount: float = 1.0
    unit: str = "g"
    # Set when the meal was logged from a recipe; amount is then the number of servings
    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", index=True)


class TargetRow(SQLModel, table=True):
    __tablename__ = "target"  # type: ignore

    user_id: str = Field(primary_key=True)
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0


class RecipeRow(SQLModel, table=True):
    __tablename__ = "recipe"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str
    # Lowercased, trimmed name, recipe names are unique case-insensitively
    name_key: str = Field(unique=True, index=True)
    servings: int = 1
    instructions: str = ""


class IngredientRow(SQLModel, table=True):
    __tablename__ = "ingredient"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)
    position: int = 0
    name: str
    amount: float = 1.0
    unit: str = "g"
    calories_per_unit: float = 0.0
    protein_per_unit: float = 0.0
    carbs_per_unit: float = 0.0
    fat_per_unit: float = 0.0


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(_engine)
    return _engine


def session() -> Session:
    return Session(get_engine())
