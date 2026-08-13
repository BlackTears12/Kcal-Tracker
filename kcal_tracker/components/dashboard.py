import reflex as rx
from kcal_tracker.state import State
from kcal_tracker.components.gauge import calorie_gauge, protein_gauge, macro_progress_cards

def dashboard_summary() -> rx.Component:
    """Dashboard summary section containing gauges and macro progress."""
    return rx.vstack(
        # Gauges Grid (Calories & Protein)
        rx.grid(
            calorie_gauge(),
            protein_gauge(),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="4",
            width="100%",
        ),
        # Carbs & Fat Linear Progress Bars
        macro_progress_cards(),
        spacing="4",
        width="100%",
    )


def target_dialog() -> rx.Component:
    """Dialog modal for adjusting daily target goals."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Set Daily Macro Goals"),
            rx.dialog.description(
                "Customize your target daily intake for Calories, Protein, Carbs, and Fat.",
                size="2",
                margin_bottom="4",
            ),
            rx.flex(
                rx.vstack(
                    rx.grid(
                        rx.vstack(
                            rx.text("Target Calories (kcal)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.target_form_calories,
                                on_change=State.set_target_form_calories,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Protein (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.target_form_protein,
                                on_change=State.set_target_form_protein,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Carbs (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.target_form_carbs,
                                on_change=State.set_target_form_carbs,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Fat (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.target_form_fat,
                                on_change=State.set_target_form_fat,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        columns=rx.breakpoints(initial="1", sm="2"),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                direction="column",
                spacing="4",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.close_target_modal,
                    ),
                ),
                rx.button(
                    "Save Targets",
                    color_scheme="orange",
                    on_click=State.save_targets,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={"max_width": "460px"},
        ),
        open=State.show_target_modal,
        on_open_change=State.set_show_target_modal,
    )
