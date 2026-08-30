import reflex as rx
from kcal_tracker.states import (
    NutritionState,
    TargetDialogState,
    MealDialogState,
    RecipesState,
    UIState,
)
from kcal_tracker.components.gauge import (
    calorie_gauge,
    macro_progress_bars,
    mobile_calorie_gauge,
    mobile_protein_gauge,
    mobile_macro_progress_cards,
)


def date_navigator() -> rx.Component:
    """Material Dark Date Switcher with previous/next day navigation and Today indicator."""
    return rx.card(
        rx.flex(
            # Previous Day Button
            rx.button(
                rx.icon("chevron-left", size=18),
                rx.text("Previous", display=rx.breakpoints(initial="none", sm="inline")),
                size="2",
                variant="soft",
                color_scheme="gray",
                on_click=NutritionState.view_previous_day,
                style={"cursor": "pointer", "border_radius": "10px"},
            ),
            # Center: Date Display & Today Chip
            rx.hstack(
                rx.box(
                    rx.icon("calendar", size=18, color="var(--orange-9)"),
                    style={
                        "background": "var(--orange-3)",
                        "padding": "6px",
                        "border_radius": "10px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.text(
                    NutritionState.formatted_date,
                    size="3",
                    weight="bold",
                ),
                rx.cond(
                    ~NutritionState.is_today,
                    rx.button(
                        "Today",
                        size="1",
                        variant="surface",
                        color_scheme="orange",
                        on_click=NutritionState.view_today,
                        style={"cursor": "pointer", "border_radius": "8px"},
                    ),
                ),
                spacing="3",
                align="center",
            ),
            # Next Day Button
            rx.button(
                rx.text("Next", display=rx.breakpoints(initial="none", sm="inline")),
                rx.icon("chevron-right", size=18),
                size="2",
                variant="soft",
                color_scheme="gray",
                on_click=NutritionState.view_next_day,
                style={"cursor": "pointer", "border_radius": "10px"},
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "box_shadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
        },
        width="100%",
    )


def dashboard_summary() -> rx.Component:
    """Dashboard summary section containing 1 circular calorie gauge and 3 macro progress bars (Material Dark)."""
    return rx.vstack(
        # Dashboard Grid: Single Circular Calorie Gauge (Left/Top) + 3 Macro Progress Bars (Right/Bottom)
        rx.grid(
            calorie_gauge(),
            macro_progress_bars(),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def content_menubar() -> rx.Component:
    """Material 3 Segmented Menubar for choosing between Logged Meals, Recipes, or All."""
    return rx.box(
        rx.grid(
            # Tab 1: Logged Meals
            rx.button(
                rx.hstack(
                    rx.icon("utensils", size=16),
                    rx.text("Logged Meals", weight="bold"),
                    rx.badge(
                        f"{NutritionState.meal_count}",
                        color_scheme=rx.cond(UIState.active_tab == "meals", "orange", "gray"),
                        variant=rx.cond(UIState.active_tab == "meals", "solid", "surface"),
                        size="1",
                        radius="full",
                    ),
                    spacing="2",
                    align="center",
                    justify="center",
                ),
                size="3",
                variant=rx.cond(UIState.active_tab == "meals", "solid", "ghost"),
                color_scheme=rx.cond(UIState.active_tab == "meals", "orange", "gray"),
                on_click=lambda: UIState.set_active_tab("meals"),
                style={
                    "cursor": "pointer",
                    "border_radius": "12px",
                    "transition": "all 0.2s ease",
                    "width": "100%",
                },
            ),
            # Tab 2: Recipes
            rx.button(
                rx.hstack(
                    rx.icon("chef-hat", size=16),
                    rx.text("Recipes", weight="bold"),
                    rx.badge(
                        f"{RecipesState.recipe_count}",
                        color_scheme=rx.cond(UIState.active_tab == "recipes", "purple", "gray"),
                        variant=rx.cond(UIState.active_tab == "recipes", "solid", "surface"),
                        size="1",
                        radius="full",
                    ),
                    spacing="2",
                    align="center",
                    justify="center",
                ),
                size="3",
                variant=rx.cond(UIState.active_tab == "recipes", "solid", "ghost"),
                color_scheme=rx.cond(UIState.active_tab == "recipes", "purple", "gray"),
                on_click=lambda: UIState.set_active_tab("recipes"),
                style={
                    "cursor": "pointer",
                    "border_radius": "12px",
                    "transition": "all 0.2s ease",
                    "width": "100%",
                },
            ),
            # Tab 3: All
            rx.button(
                rx.hstack(
                    rx.icon("layout-grid", size=16),
                    rx.text("All", weight="bold"),
                    spacing="2",
                    align="center",
                    justify="center",
                ),
                size="3",
                variant=rx.cond(UIState.active_tab == "all", "solid", "ghost"),
                color_scheme=rx.cond(UIState.active_tab == "all", "gray", "gray"),
                on_click=lambda: UIState.set_active_tab("all"),
                style={
                    "cursor": "pointer",
                    "border_radius": "12px",
                    "transition": "all 0.2s ease",
                    "width": "100%",
                },
            ),
            columns="3",
            spacing="2",
            width="100%",
        ),
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "padding": "6px",
            "box_shadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
            "width": "100%",
        },
    )


def target_dialog() -> rx.Component:
    """Material Dark dialog modal for adjusting daily target goals."""
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
                            rx.hstack(
                                rx.icon("flame", size=14, color="var(--orange-9)"),
                                rx.text("Target Calories (kcal)", size="2", weight="bold"),
                                spacing="1",
                                align="center",
                            ),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_calories,
                                on_change=TargetDialogState.set_target_calories,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("dumbbell", size=14, color="#38BDF8"),
                                rx.text("Target Protein (g)", size="2", weight="bold"),
                                spacing="1",
                                align="center",
                            ),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_protein,
                                on_change=TargetDialogState.set_target_protein,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("wheat", size=14, color="#FBBF24"),
                                rx.text("Target Carbs (g)", size="2", weight="bold"),
                                spacing="1",
                                align="center",
                            ),
                            rx.input(
                                type="number",
                                value=TargetDialogState.target_carbs,
                                on_change=TargetDialogState.set_target_carbs,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("droplet", size=14, color="#34D399"),
                                rx.text("Target Fat (g)", size="2", weight="bold"),
                                spacing="1",
                                align="center",
                            ),
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
            style={
                "max_width": "480px",
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "20px",
            },
        ),
        open=TargetDialogState.show_modal,
        on_open_change=TargetDialogState.set_show_modal,
    )


# Backwards compatibility aliases
desktop_date_navigator = date_navigator
mobile_date_navigator = date_navigator
mobile_macro_summary = dashboard_summary
mobile_nav_pills = content_menubar

