import reflex as rx
from kcal_tracker.data.workout import Workout, WorkoutType
from kcal_tracker.models.services import NutritionService
from kcal_tracker.states.login_state import current_user_id
from kcal_tracker.states.nutrition_state import NutritionState


class WorkoutDialogState(rx.State):
    show_modal: bool = False
    is_editing_workout: bool = False

    # Form fields
    workout_id: int = 0
    name: str = ""
    type: WorkoutType = WorkoutType.Cardio
    duration_min: float = 30.0
    calories_burned: float = 0.0

    @rx.var
    def modal_title(self) -> str:
        return "Edit Workout" if self.is_editing_workout else "Log Workout"

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_name(self, val: str):
        self.name = val

    def set_type(self, val: str):
        try:
            self.type = WorkoutType(val)
        except ValueError:
            self.type = WorkoutType.Other

    def set_duration_min(self, val: str):
        try:
            self.duration_min = float(val)
        except (ValueError, TypeError):
            self.duration_min = 0.0

    def set_calories_burned(self, val: str):
        try:
            self.calories_burned = float(val)
        except (ValueError, TypeError):
            self.calories_burned = 0.0

    def open_add_workout(self):
        self.is_editing_workout = False
        self.workout_id = 0
        self.name = ""
        self.type = WorkoutType.Cardio
        self.duration_min = 30.0
        self.calories_burned = 0.0
        self.show_modal = True

    def open_edit_workout(self, workout: Workout):
        if isinstance(workout, dict):
            workout = Workout(**workout)
        self.is_editing_workout = True
        self.workout_id = workout.id
        self.name = workout.name
        self.type = workout.type
        self.duration_min = workout.duration_min
        self.calories_burned = workout.calories_burned
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save_workout(self):
        if not self.name.strip():
            return
        user_id = await current_user_id(self)
        if user_id is None:
            return

        service = NutritionService(user_id)
        nutrition_state = await self.get_state(NutritionState)
        workout = Workout(
            id=self.workout_id,
            name=self.name.strip(),
            type=self.type,
            duration_min=self.duration_min,
            calories_burned=self.calories_burned,
        )
        if self.is_editing_workout:
            service.update_workout(workout)
        else:
            service.add_workouts([workout], nutrition_state.date_context)

        nutrition_state._reload(user_id)
        self.show_modal = False
