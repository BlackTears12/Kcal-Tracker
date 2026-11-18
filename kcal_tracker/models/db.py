"""SQLite persistence: table definitions and session factory."""
import datetime
import pathlib
from sqlalchemy import UniqueConstraint, inspect, text
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


class WorkoutRow(SQLModel, table=True):
    __tablename__ = "workout"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    date: datetime.date = Field(index=True)
    name: str
    type: str
    duration_min: float = 0.0
    calories_burned: float = 0.0
    distance_km: float = 0.0


class ExerciseRow(SQLModel, table=True):
    __tablename__ = "exercise"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    workout_id: int = Field(foreign_key="workout.id", index=True)
    position: int = 0
    name: str
    sets: int = 0
    reps: int = 0
    weight_kg: float = 0.0


class BodyMeasurementRow(SQLModel, table=True):
    __tablename__ = "body_measurement"  # type: ignore
    # One value per body site and day
    __table_args__ = (UniqueConstraint("user_id", "date", "site"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    date: datetime.date = Field(index=True)
    site: str
    value_cm: float


class AuthSessionRow(SQLModel, table=True):
    __tablename__ = "auth_session"  # type: ignore

    # SHA-256 of the token kept by the browser, the token itself is never stored
    token_hash: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime.datetime
    last_seen_at: datetime.datetime
    expires_at: datetime.datetime
    user_agent: str = ""


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
        _add_missing_columns(_engine)
    return _engine


def _add_missing_columns(engine):
    """create_all only creates missing tables, this adds columns that were added to existing ones.

    Only handles new columns with a plain default value, anything else needs a real migration.
    """
    existing_tables = inspect(engine).get_table_names()
    with engine.begin() as conn:
        for table in SQLModel.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            existing = {c["name"] for c in inspect(conn).get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                default = column.default.arg if column.default is not None else None
                if default is None or callable(default):
                    raise RuntimeError(f"Can't add column {table.name}.{column.name} automatically, it needs a default value")
                col_type = column.type.compile(dialect=engine.dialect)
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type} NOT NULL DEFAULT {default!r}'))


def session() -> Session:
    return Session(get_engine())
