from enum import Enum
import datetime
from dataclasses import dataclass, field


class WorkoutType(str, Enum):
    Cardio = "Cardio"
    Strength = "Strength"
    Sports = "Sports"
    Mobility = "Mobility"
    Other = "Other"


@dataclass
class Exercise:
    """One exercise of a strength workout, e.g. bench press 3 x 8 @ 60 kg."""
    name: str = ""
    sets: int = 3
    reps: int = 10
    # 0 means bodyweight
    weight_kg: float = 0.0


@dataclass
class Workout:
    id: int = 0
    name: str = ""
    type: WorkoutType = WorkoutType.Cardio
    duration_min: float = 0.0
    calories_burned: float = 0.0
    date: datetime.date = field(default_factory=datetime.date.today)
    # Cardio only
    distance_km: float = 0.0
    # Strength only
    exercises: list[Exercise] = field(default_factory=list)
    # Cardio pace like "5:30 /km", calculated from distance and duration
    pace: str = ""

    def __post_init__(self):
        if isinstance(self.type, str):
            try:
                self.type = WorkoutType(self.type)
            except ValueError:
                self.type = WorkoutType.Other
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)
        self.exercises = [Exercise(**e) if isinstance(e, dict) else e for e in self.exercises]
        self.pace = pace_text(self.duration_min, self.distance_km)


def pace_text(duration_min: float, distance_km: float) -> str:
    if distance_km <= 0 or duration_min <= 0:
        return ""
    seconds = round(duration_min * 60 / distance_km)
    return f"{seconds // 60}:{seconds % 60:02d} /km"
