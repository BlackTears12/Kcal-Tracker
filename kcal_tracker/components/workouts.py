import reflex as rx
from kcal_tracker.states import (
    Workout,
    WorkoutType,
    NutritionState,
    WorkoutDialogState,
)

WORKOUT_TYPES = [t.value for t in WorkoutType]


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
                rx.badge(f"{workout.calories_burned} kcal burned", color_scheme="cyan", variant="surface", size="1"),
                spacing="2",
                wrap="wrap",
                width="100%",
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
