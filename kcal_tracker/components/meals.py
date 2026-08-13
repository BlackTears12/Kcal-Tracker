import reflex as rx
from kcal_tracker.state import State

def render_meal_item(meal: dict) -> rx.Component:
    """Renders an individual logged meal row/card."""
    category_colors = {
        "Breakfast": "amber",
        "Lunch": "blue",
        "Dinner": "purple",
        "Snack": "green",
    }
    
    return rx.card(
        rx.flex(
            # Left: Category Icon & Details
            rx.hstack(
                rx.box(
                    rx.icon("utensils", size=18, color="var(--gray-11)"),
                    style={
                        "background": "var(--gray-3)",
                        "padding": "10px",
                        "border_radius": "10px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading(meal["name"], size="3", weight="bold"),
                        rx.badge(
                            meal["category"],
                            color_scheme=category_colors.get(meal["category"], "gray"),
                            variant="soft",
                            size="1",
                        ),
                        rx.text(meal["time"], size="1", color_scheme="gray"),
                        align="center",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.badge(f"{meal['calories']} kcal", color_scheme="orange", variant="surface", size="1"),
                        rx.badge(f"{meal['protein']}g P", color_scheme="blue", variant="surface", size="1"),
                        rx.badge(f"{meal['carbs']}g C", color_scheme="amber", variant="surface", size="1"),
                        rx.badge(f"{meal['fat']}g F", color_scheme="green", variant="surface", size="1"),
                        spacing="2",
                        align="center",
                    ),
                    spacing="1",
                ),
                spacing="3",
                align="center",
            ),
            # Right: Edit & Delete buttons
            rx.hstack(
                rx.button(
                    rx.icon("square-pen", size=15),
                    "Edit",
                    size="1",
                    variant="soft",
                    color_scheme="blue",
                    on_click=lambda: State.open_edit_meal(meal),
                    style={"cursor": "pointer"},
                ),
                rx.button(
                    rx.icon("trash-2", size=15),
                    size="1",
                    variant="soft",
                    color_scheme="red",
                    on_click=lambda: State.delete_meal(meal["id"]),
                    style={"cursor": "pointer"},
                ),
                spacing="2",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "12px",
            "transition": "all 0.2s ease",
            "&:hover": {
                "border_color": "var(--gray-6)",
                "box_shadow": "0 2px 12px rgba(0,0,0,0.04)",
            },
        },
        width="100%",
    )


def meals_section() -> rx.Component:
    """Today's logged meals list section."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("list-checks", color="var(--orange-9)", size=20),
                    rx.heading("Today's Logged Meals", size="4", weight="bold"),
                    rx.badge(
                        f"{State.meal_count} meals",
                        color_scheme="gray",
                        variant="soft",
                        radius="full",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Log Meal",
                    size="2",
                    color_scheme="orange",
                    on_click=State.open_add_meal,
                    style={"cursor": "pointer", "border_radius": "8px"},
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(size="4"),
            rx.cond(
                State.meal_count == 0,
                rx.vstack(
                    rx.icon("utensils-crossed", size=36, color="var(--gray-8)"),
                    rx.text("No meals logged yet today.", size="2", weight="bold"),
                    rx.text(
                        "Click '+ Log Meal' or chat with the AI Assistant to log your food!",
                        size="2",
                        color_scheme="gray",
                    ),
                    align="center",
                    padding_y="8",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(State.logged_meals, render_meal_item),
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
            "border_radius": "16px",
        },
        width="100%",
    )


def meal_dialog() -> rx.Component:
    """Dialog modal for creating or editing a meal."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    State.is_editing_meal,
                    "Edit Logged Meal",
                    "Add New Meal",
                ),
            ),
            rx.dialog.description(
                "Enter meal details and macro breakdown.",
                size="2",
                margin_bottom="4",
            ),
            rx.flex(
                rx.vstack(
                    rx.vstack(
                        rx.text("Meal Name", size="2", weight="bold"),
                        rx.input(
                            placeholder="e.g. Grilled Chicken & Rice",
                            value=State.meal_form_name,
                            on_change=State.set_meal_form_name,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Category", size="2", weight="bold"),
                        rx.select(
                            ["Breakfast", "Lunch", "Dinner", "Snack"],
                            value=State.meal_form_category,
                            on_change=State.set_meal_form_category,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Calories (kcal)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.meal_form_calories,
                                on_change=State.set_meal_form_calories,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Protein (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.meal_form_protein,
                                on_change=State.set_meal_form_protein,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Carbs (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.meal_form_carbs,
                                on_change=State.set_meal_form_carbs,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Fat (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.meal_form_fat,
                                on_change=State.set_meal_form_fat,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        columns=rx.breakpoints(initial="2", sm="4"),
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
                        on_click=State.close_meal_modal,
                    ),
                ),
                rx.button(
                    "Save Meal",
                    color_scheme="orange",
                    on_click=State.save_meal,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={"max_width": "500px"},
        ),
        open=State.show_meal_modal,
        on_open_change=State.set_show_meal_modal,
    )
