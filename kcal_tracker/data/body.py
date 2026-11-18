import datetime
from dataclasses import dataclass, field

# Shown in the log dialog in this order, custom sites the user added follow after them
STANDARD_SITES = [
    "Neck",
    "Shoulders",
    "Chest",
    "Waist",
    "Belly",
    "Hips",
    "Upper arm (L)",
    "Upper arm (R)",
    "Forearm (L)",
    "Forearm (R)",
    "Thigh (L)",
    "Thigh (R)",
    "Calf (L)",
    "Calf (R)",
]


def normalize_site(site: str) -> str:
    """Trims the name and maps it to the standard spelling if it is one, e.g. 'hips ' -> 'Hips'.
    Other names get a capital first letter, e.g. 'wrist' -> 'Wrist'."""
    site = " ".join(site.split())
    standard = next((s for s in STANDARD_SITES if s.lower() == site.lower()), None)
    return standard or site[:1].upper() + site[1:]


@dataclass
class Measurement:
    site: str = ""
    date: datetime.date = field(default_factory=datetime.date.today)
    value_cm: float = 0.0
    # ISO date, for the frontend to pass back when deleting
    date_iso: str = ""
    date_text: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)
        self.date_iso = self.date.isoformat()
        self.date_text = self.date.strftime("%b %d, %Y")


@dataclass
class SiteSummary:
    """The latest measurement of a body site and how it changed since the one before."""
    site: str = ""
    latest_cm: float = 0.0
    latest_date_text: str = ""
    # Change since the previous measurement, 0 when there is only one
    change_cm: float = 0.0
    change_text: str = ""
    # Newest first
    history: list[Measurement] = field(default_factory=list)

    def __post_init__(self):
        self.history = [Measurement(**m) if isinstance(m, dict) else m for m in self.history]


@dataclass
class MeasurementInput:
    """A row of the log dialog, value is text so it can be left blank."""
    site: str = ""
    value: str = ""
