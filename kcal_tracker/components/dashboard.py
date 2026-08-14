import reflex as rx
from kcal_tracker.states import (
    TargetDialogState,
    MealDialogState,
    UIState,
)
from kcal_tracker.components.gauge import (
    calorie_gauge,
    protein_gauge,
    macro_progress_cards,
    mobile_calorie_gauge,
    mobile_protein_gauge,
    mobile_macro_progress_cards,
)


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


def mobile_macro_summary() -> rx.Component:
    """Compact macro dashboard summary for mobile screens with smaller Kcal & Protein gauges."""
    return rx.card(
        rx.vstack(
            # Card Header with quick stats & actions
            rx.hstack(
                rx.hstack(
                    rx.icon("activity", color="var(--orange-9)", size=18),
                    rx.heading("Daily Summary", size="3", weight="bold"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("target", size=13),
                        "Goals",
                        size="1",
                        variant="soft",
                        color_scheme="gray",
                        on_click=TargetDialogState.open_modal,
                        style={"cursor": "pointer", "border_radius": "6px"},
                    ),
                    rx.button(
                        rx.icon("plus", size=13),
                        "Log",
                        size="1",
                        color_scheme="orange",
                        on_click=MealDialogState.open_add_meal,
                        style={"cursor": "pointer", "border_radius": "6px"},
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            # Side-by-side Mini Gauges for Calories and Protein
            rx.grid(
                mobile_calorie_gauge(),
                mobile_protein_gauge(),
                columns="2",
                spacing="2",
                width="100%",
            ),
            # Compact Carbs & Fat Mini Progress Bars
            mobile_macro_progress_cards(),
            spacing="3",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "box_shadow": "0 4px 16px rgba(0,0,0,0.04)",
        },
        width="100%",
    )


def mobile_nav_pills() -> rx.Component:
    """Android app style quick navigation chips for switching views on mobile."""
    return rx.hstack(
        rx.button(
            rx.icon("bot", size=14),
            "AI Assistant",
            size="2",
            variant=rx.cond(UIState.active_tab == "chat", "solid", "soft"),
            color_scheme="purple",
            on_click=lambda: UIState.set_active_tab("chat"),
            style={"cursor": "pointer", "border_radius": "20px", "flex": "1"},
        ),
        rx.button(
            rx.icon("utensils", size=14),
            "Meals",
            size="2",
            variant=rx.cond(UIState.active_tab == "meals", "solid", "soft"),
            color_scheme="orange",
            on_click=lambda: UIState.set_active_tab("meals"),
            style={"cursor": "pointer", "border_radius": "20px", "flex": "1"},
        ),
        rx.button(
            rx.icon("chef-hat", size=14),
            "Recipes",
            size="2",
            variant=rx.cond(UIState.active_tab == "recipes", "solid", "soft"),
            color_scheme="purple",
            on_click=lambda: UIState.set_active_tab("recipes"),
            style={"cursor": "pointer", "border_radius": "20px", "flex": "1"},
        ),
        rx.button(
            rx.icon("layout-grid", size=14),
            "All",
            size="2",
            variant=rx.cond((UIState.active_tab == "all") | (UIState.active_tab == "dashboard"), "solid", "soft"),
            color_scheme="gray",
            on_click=lambda: UIState.set_active_tab("all"),
            style={"cursor": "pointer", "border_radius": "20px", "flex": "1"},
        ),
        spacing="2",
        width="100%",
        justify="between",
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
                                value=TargetDialogState.target_calories,
                                on_change=TargetDialogState.set_target_calories,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Protein (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_protein,
                                on_change=TargetDialogState.set_target_protein,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Carbs (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_carbs,
                                on_change=TargetDialogState.set_target_carbs,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Target Fat (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_fat,
                                on_change=TargetDialogState.set_target_fat,
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
                        on_click=TargetDialogState.close_modal,
                    ),
                ),
                rx.button(
                    "Save Targets",
                    color_scheme="orange",
                    on_click=TargetDialogState.save_targets,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={"max_width": "460px"},
        ),
        open=TargetDialogState.show_modal,
        on_open_change=TargetDialogState.set_show_modal,
    )
