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
class Workout:
    id: int = 0
    name: str = ""
    type: WorkoutType = WorkoutType.Cardio
    duration_min: float = 0.0
    calories_burned: float = 0.0
    date: datetime.date = field(default_factory=datetime.date.today)

    def __post_init__(self):
        if isinstance(self.type, str):
            try:
                self.type = WorkoutType(self.type)
            except ValueError:
                self.type = WorkoutType.Other
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)
