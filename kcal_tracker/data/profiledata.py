from dataclasses import dataclass, field
from kcal_tracker.data.meal import MacroProfile

@dataclass 
class ProfileData:
    targets: MacroProfile = field(
        default_factory=lambda: MacroProfile(
            calories=2200.0,
            protein=160.0,
            carbs=220.0,
            fat=65.0,
        )
    )

    def __post_init__(self):
        if isinstance(self.targets, dict):
            self.targets = MacroProfile(**self.targets)

    