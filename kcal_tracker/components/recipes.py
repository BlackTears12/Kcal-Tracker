import reflex as rx
from kcal_tracker.state import State

def render_recipe_item(recipe: dict) -> rx.Component:
    """Renders a saved recipe card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("book-open", size=18, color="var(--purple-9)"),
                        style={
                            "background": "var(--purple-3)",
                            "padding": "8px",
                            "border_radius": "8px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                        },
                    ),
                    rx.vstack(
                        rx.heading(recipe["name"], size="3", weight="bold"),
                        rx.text(f"Servings: {recipe['servings']}", size="1", color_scheme="gray"),
                        spacing="0",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("circle-plus", size=15),
                        "Log Meal",
                        size="1",
                        color_scheme="green",
                        variant="soft",
                        on_click=lambda: State.log_recipe_as_meal(recipe),
                        style={"cursor": "pointer"},
                    ),
                    rx.button(
                        rx.icon("square-pen", size=15),
                        size="1",
                        variant="soft",
                        color_scheme="blue",
                        on_click=lambda: State.open_edit_recipe(recipe),
                        style={"cursor": "pointer"},
                    ),
                    rx.button(
                        rx.icon("trash-2", size=15),
                        size="1",
                        variant="soft",
                        color_scheme="red",
                        on_click=lambda: State.delete_recipe(recipe["id"]),
                        style={"cursor": "pointer"},
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.text(
                f"🛒 Ingredients: {recipe['ingredients']}",
                size="2",
                color_scheme="gray",
                style={"font_style": "italic"},
            ),
            rx.hstack(
                rx.badge(f"{recipe['calories']} kcal", color_scheme="orange", variant="surface", size="1"),
                rx.badge(f"{recipe['protein']}g Protein", color_scheme="blue", variant="surface", size="1"),
                rx.badge(f"{recipe['carbs']}g Carbs", color_scheme="amber", variant="surface", size="1"),
                rx.badge(f"{recipe['fat']}g Fat", color_scheme="green", variant="surface", size="1"),
                spacing="2",
                align="center",
            ),
            spacing="3",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "12px",
            "transition": "all 0.2s ease",
            "&:hover": {
                "border_color": "var(--purple-6)",
                "box_shadow": "0 2px 12px rgba(0,0,0,0.04)",
            },
        },
        width="100%",
    )


def recipes_section() -> rx.Component:
    """Saved recipes collection section."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("chef-hat", color="var(--purple-9)", size=20),
                    rx.heading("Saved Recipes", size="4", weight="bold"),
                    rx.badge(
                        f"{State.recipe_count} recipes",
                        color_scheme="purple",
                        variant="soft",
                        radius="full",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Create Recipe",
                    size="2",
                    color_scheme="purple",
                    on_click=State.open_add_recipe,
                    style={"cursor": "pointer", "border_radius": "8px"},
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(size="4"),
            rx.cond(
                State.recipe_count == 0,
                rx.vstack(
                    rx.icon("book-x", size=36, color="var(--gray-8)"),
                    rx.text("No saved recipes yet.", size="2", weight="bold"),
                    rx.text(
                        "Create a recipe manually or ask the AI Chatbot e.g. 'Create a recipe for Protein Smoothie'!",
                        size="2",
                        color_scheme="gray",
                    ),
                    align="center",
                    padding_y="8",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(State.recipes, render_recipe_item),
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


def recipe_dialog() -> rx.Component:
    """Dialog modal for creating or editing a recipe."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    State.is_editing_recipe,
                    "Edit Recipe",
                    "Create New Recipe",
                ),
            ),
            rx.dialog.description(
                "Enter recipe details and ingredients.",
                size="2",
                margin_bottom="4",
            ),
            rx.flex(
                rx.vstack(
                    rx.vstack(
                        rx.text("Recipe Title", size="2", weight="bold"),
                        rx.input(
                            placeholder="e.g. Protein Oatmeal Bowl",
                            value=State.recipe_form_name,
                            on_change=State.set_recipe_form_name,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Ingredients & Quantity", size="2", weight="bold"),
                        rx.input(
                            placeholder="e.g. 50g Oats, 1 scoop Whey, 200ml Milk",
                            value=State.recipe_form_ingredients,
                            on_change=State.set_recipe_form_ingredients,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Servings", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.recipe_form_servings,
                                on_change=State.set_recipe_form_servings,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Calories (kcal)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.recipe_form_calories,
                                on_change=State.set_recipe_form_calories,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Protein (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.recipe_form_protein,
                                on_change=State.set_recipe_form_protein,
                                size="3",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Carbs (g)", size="2", weight="bold"),
                            rx.input(
                                type="number",
                                value=State.recipe_form_carbs,
                                on_change=State.set_recipe_form_carbs,
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
                        on_click=State.close_recipe_modal,
                    ),
                ),
                rx.button(
                    "Save Recipe",
                    color_scheme="purple",
                    on_click=State.save_recipe,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={"max_width": "500px"},
        ),
        open=State.show_recipe_modal,
        on_open_change=State.set_show_recipe_modal,
    )
