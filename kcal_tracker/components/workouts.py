import reflex as rx
from kcal_tracker.data.workout import Exercise
from kcal_tracker.states import (
    Workout,
    WorkoutType,
    NutritionState,
    WorkoutDialogState,
)

WORKOUT_TYPES = [t.value for t in WorkoutType]


def render_exercise_line(exercise: Exercise) -> rx.Component:
    """Read-only exercise line on a logged strength workout, e.g. Bench press 3 × 8 @ 60 kg."""
    return rx.hstack(
        rx.icon("dumbbell", size=12, color="var(--blue-9)"),
        rx.text(exercise.name, size="2", weight="medium"),
        rx.text(
            f"{exercise.sets} × {exercise.reps}",
            rx.cond(exercise.weight_kg > 0, f" @ {exercise.weight_kg} kg", " · bodyweight"),
            size="2",
            color_scheme="gray",
        ),
        spacing="2",
        align="center",
        wrap="wrap",
    )


def render_workout_item(workout: Workout) -> rx.Component:
    """Renders an individual logged workout row/card with responsive mobile-friendly action buttons."""
    type_colors = {
        "Cardio": "red",
        "Strength": "blue",
        "Sports": "green",
        "Mobility": "purple",
        "Other": "gray",
    }

    return rx.card(
        rx.vstack(
            # Top Row: Icon + Workout Name + Type Badge (Left) and Edit/Delete Buttons (Right)
            rx.flex(
                rx.hstack(
                    rx.box(
                        rx.icon("activity", size=18, color="var(--gray-11)"),
                        style={
                            "background": "var(--gray-3)",
                            "padding": "8px",
                            "border_radius": "10px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                            "min_width": "34px",
                        },
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                workout.name,
                                size="3",
                                weight="bold",
                                style={
                                    "overflow": "hidden",
                                    "text_overflow": "ellipsis",
                                    "white_space": "nowrap",
                                },
                            ),
                            rx.badge(
                                workout.type,
                                color_scheme=type_colors.get(workout.type, "gray"),
                                variant="soft",
                                size="1",
                                radius="full",
                            ),
                            align="center",
                            spacing="2",
                            wrap="wrap",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                    min_width="0",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("square-pen", size=14),
                        rx.text("Edit", display=rx.breakpoints(initial="none", sm="inline")),
                        size="1",
                        variant="soft",
                        color_scheme="blue",
                        on_click=lambda: WorkoutDialogState.open_edit_workout(workout),
                        style={"cursor": "pointer", "border_radius": "8px"},
                    ),
                    rx.button(
                        rx.icon("trash-2", size=14),
                        size="1",
                        variant="soft",
                        color_scheme="red",
                        on_click=lambda: NutritionState.remove_workout(workout.id),
                        style={"cursor": "pointer", "border_radius": "8px"},
                    ),
                    spacing="1",
                    align="center",
                    flex_shrink="0",
                ),
                justify="between",
                align="center",
                width="100%",
                gap="2",
            ),
            rx.flex(
                rx.badge(f"{workout.duration_min} min", color_scheme="gray", variant="surface", size="1"),
                rx.cond(
                    workout.distance_km > 0,
                    rx.badge(f"{workout.distance_km} km", color_scheme="red", variant="surface", size="1"),
                ),
                rx.cond(
                    workout.pace != "",
                    rx.badge(workout.pace, color_scheme="red", variant="surface", size="1"),
                ),
                rx.badge(f"{workout.calories_burned} kcal burned", color_scheme="cyan", variant="surface", size="1"),
                spacing="2",
                wrap="wrap",
                width="100%",
            ),
            rx.cond(
                workout.exercises.length() > 0,
                rx.vstack(
                    rx.foreach(workout.exercises, render_exercise_line),
                    spacing="1",
                    width="100%",
                    padding_top="1",
                    border_top="1px solid var(--gray-4)",
                ),
            ),
            spacing="2",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "14px",
            "padding": "12px 14px",
            "transition": "all 0.2s ease",
            "overflow": "hidden",
            "&:hover": {
                "border_color": "var(--gray-6)",
                "box_shadow": "0 2px 12px rgba(0,0,0,0.2)",
            },
        },
        width="100%",
    )


def workouts_section() -> rx.Component:
    """Logged workouts list section for the viewed date (Material Dark Style)."""
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.hstack(
                    rx.box(
                        rx.icon("activity", size=18, color="white"),
                        style={
                            "background": "linear-gradient(135deg, #22D3EE 0%, #3B82F6 100%)",
                            "padding": "6px",
                            "border_radius": "10px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                        },
                    ),
                    rx.heading(
                        rx.cond(
                            NutritionState.is_today,
                            "Today's Workouts",
                            f"Workouts ({NutritionState.short_date})",
                        ),
                        size="4",
                        weight="bold",
                    ),
                    rx.badge(
                        f"{NutritionState.total_burned} kcal · {NutritionState.total_workout_minutes} min",
                        color_scheme="cyan",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                    min_width="0",
                    wrap="wrap",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Log Workout",
                    size="2",
                    color_scheme="cyan",
                    on_click=WorkoutDialogState.open_add_workout,
                    style={
                        "cursor": "pointer",
                        "border_radius": "10px",
                        "flex_shrink": "0",
                        "margin_left": "auto",
                    },
                ),
                justify="between",
                align="center",
                width="100%",
                gap="2",
                wrap="wrap",
            ),
            rx.divider(size="4"),
            rx.cond(
                NutritionState.workout_count == 0,
                rx.vstack(
                    rx.icon("activity", size=40, color="var(--gray-8)"),
                    rx.text(
                        rx.cond(
                            NutritionState.is_today,
                            "No workouts logged yet today.",
                            "No workouts logged for this date.",
                        ),
                        size="3",
                        weight="bold",
                    ),
                    rx.text(
                        "Click '+ Log Workout' or tell the AI Assistant what you did. Burned calories are added to your daily budget.",
                        size="2",
                        color_scheme="gray",
                        text_align="center",
                    ),
                    align="center",
                    padding_y="8",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(NutritionState.logged_workouts, render_workout_item),
                    spacing="3",
                    width="100%",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "20px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
        },
        width="100%",
    )


def render_editable_exercise(exercise: Exercise, index: int) -> rx.Component:
    """Editable exercise row inside the Workout Dialog."""
    return rx.card(
        rx.flex(
            rx.hstack(
                rx.badge(f"#{index + 1}", size="1", color_scheme="blue", variant="soft"),
                rx.input(
                    placeholder="Exercise (e.g. Bench press)",
                    value=exercise.name,
                    on_change=lambda val: WorkoutDialogState.update_exercise_name(index, val),
                    size="2",
                    flex="1",
                    min_width="120px",
                ),
                spacing="2",
                align="center",
                flex="1",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Sets", size="1", color_scheme="gray"),
                    rx.input(
                        type="number",
                        value=exercise.sets,
                        on_change=lambda val: WorkoutDialogState.update_exercise_sets(index, val),
                        size="2",
                        style={"width": "58px"},
                    ),
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Reps", size="1", color_scheme="gray"),
                    rx.input(
                        type="number",
                        value=exercise.reps,
                        on_change=lambda val: WorkoutDialogState.update_exercise_reps(index, val),
                        size="2",
                        style={"width": "58px"},
                    ),
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("kg", size="1", color_scheme="gray"),
                    rx.input(
                        type="number",
                        value=exercise.weight_kg,
                        on_change=lambda val: WorkoutDialogState.update_exercise_weight(index, val),
                        size="2",
                        style={"width": "70px"},
                    ),
                    spacing="0",
                ),
                rx.button(
                    rx.icon("trash-2", size=14),
                    size="1",
                    color_scheme="red",
                    variant="soft",
                    on_click=lambda: WorkoutDialogState.remove_exercise(index),
                    style={"cursor": "pointer", "border_radius": "8px", "align_self": "flex-end", "margin_bottom": "6px"},
                ),
                spacing="2",
                align="end",
            ),
            justify="between",
            align="end",
            width="100%",
            wrap="wrap",
            gap="2",
        ),
        size="1",
        style={"background": "var(--gray-1)", "border": "1px solid var(--gray-4)", "border_radius": "12px"},
        width="100%",
    )


def workout_dialog() -> rx.Component:
    """Dialog modal for logging or editing a workout (Material Dark Style)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(WorkoutDialogState.modal_title),
            rx.dialog.description(
                "Enter the workout and an estimate of the calories it burned.",
                size="2",
                margin_bottom="4",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Workout", size="2", weight="bold"),
                    rx.input(
                        placeholder="e.g. 5k run, Upper body",
                        value=WorkoutDialogState.name,
                        on_change=WorkoutDialogState.set_name,
                        size="3",
                        width="100%",
                    ),
                    width="100%",
                    spacing="1",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Type", size="2", weight="bold"),
                        rx.select(
                            WORKOUT_TYPES,
                            value=WorkoutDialogState.type,
                            on_change=WorkoutDialogState.set_type,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.icon("timer", size=14, color="var(--gray-11)"),
                            rx.text("Duration (min)", size="2", weight="bold"),
                            spacing="1",
                            align="center",
                        ),
                        rx.input(
                            type="number",
                            value=WorkoutDialogState.duration_min,
                            on_change=WorkoutDialogState.set_duration_min,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.icon("flame", size=14, color="var(--cyan-9)"),
                            rx.text("Burned (kcal)", size="2", weight="bold"),
                            spacing="1",
                            align="center",
                        ),
                        rx.input(
                            type="number",
                            value=WorkoutDialogState.calories_burned,
                            on_change=WorkoutDialogState.set_calories_burned,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    columns=rx.breakpoints(initial="1", sm="3"),
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    WorkoutDialogState.is_cardio,
                    rx.vstack(
                        rx.hstack(
                            rx.icon("route", size=14, color="var(--red-9)"),
                            rx.text("Distance (km)", size="2", weight="bold"),
                            spacing="1",
                            align="center",
                        ),
                        rx.hstack(
                            rx.input(
                                type="number",
                                value=WorkoutDialogState.distance_km,
                                on_change=WorkoutDialogState.set_distance_km,
                                size="3",
                                flex="1",
                            ),
                            rx.cond(
                                WorkoutDialogState.pace != "",
                                rx.badge(f"Pace {WorkoutDialogState.pace}", color_scheme="red", variant="soft", size="2"),
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                ),
                rx.cond(
                    WorkoutDialogState.is_strength,
                    rx.vstack(
                        rx.hstack(
                            rx.text("Exercises", size="2", weight="bold"),
                            rx.button(
                                rx.icon("plus", size=14),
                                "Add Exercise",
                                size="1",
                                variant="soft",
                                color_scheme="blue",
                                on_click=WorkoutDialogState.add_exercise,
                                style={"cursor": "pointer", "border_radius": "8px"},
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.foreach(WorkoutDialogState.exercises, render_editable_exercise),
                            spacing="2",
                            width="100%",
                            style={"max_height": "300px", "overflow_y": "auto", "padding_right": "4px"},
                        ),
                        width="100%",
                        spacing="2",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=WorkoutDialogState.close_modal,
                    ),
                ),
                rx.button(
                    "Save Workout",
                    color_scheme="cyan",
                    on_click=WorkoutDialogState.save_workout,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={
                "max_width": "500px",
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "20px",
            },
        ),
        open=WorkoutDialogState.show_modal,
        on_open_change=WorkoutDialogState.set_show_modal,
    )
