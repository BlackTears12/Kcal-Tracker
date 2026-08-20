import reflex as rx
from kcal_tracker.states import (
    RecipesState,
    RecipeDialogState,
)
from kcal_tracker.data.recipe import Recipe, Ingredient 

def render_recipe_item(recipe: Recipe) -> rx.Component:
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
                        rx.heading(recipe.name, size="3", weight="bold"),
                        rx.text(f"Servings: {recipe.servings}", size="1", color_scheme="gray"),
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
                        on_click=lambda: RecipesState.log_recipe_as_meal(recipe),
                        style={"cursor": "pointer"},
                    ),
                    rx.button(
                        rx.icon("square-pen", size=15),
                        size="1",
                        variant="soft",
                        color_scheme="blue",
                        on_click=lambda: RecipeDialogState.open_edit_recipe(recipe),
                        style={"cursor": "pointer"},
                    ),
                    rx.button(
                        rx.icon("trash-2", size=15),
                        size="1",
                        variant="soft",
                        color_scheme="red",
                        on_click=lambda: RecipesState.remove_recipe(recipe.id),
                        style={"cursor": "pointer"},
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.cond(
                recipe.instructions != "",
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("clipboard-list", size=14, color="var(--purple-9)"),
                            rx.text("Instructions", size="1", weight="bold", color="var(--purple-9)"),
                            spacing="1",
                            align="center",
                        ),
                        rx.text(
                            recipe.instructions,
                            size="2",
                            color="var(--gray-12)",
                            style={
                                "white_space": "pre-wrap",
                                "word_break": "break-word",
                                "line_height": "1.5",
                            },
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    style={
                        "background": "var(--gray-2)",
                        "border": "1px solid var(--gray-4)",
                        "border_radius": "8px",
                        "padding": "10px 12px",
                        "width": "100%",
                        "max_height": "180px",
                        "overflow_y": "auto",
                    },
                ),
            ),
            # Ingredients List
            rx.vstack(
                rx.hstack(
                    rx.icon("shopping-basket", size=14, color="var(--purple-9)"),
                    rx.text("Ingredients:", size="1", weight="bold", color="var(--purple-9)"),
                    spacing="1",
                    align="center",
                ),
                rx.cond(
                    recipe.ingredients,
                    rx.vstack(
                        rx.foreach(
                            recipe.ingredients,
                            lambda ing: rx.hstack(
                                rx.text(f"• {ing.name}", size="2", weight="medium"),
                                rx.badge(f"{ing.weight_g}g", color_scheme="gray", variant="surface", size="1"),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.text(
                        f"🛒 {recipe.ingredients_text}",
                        size="2",
                        color_scheme="gray",
                        style={"font_style": "italic"},
                    ),
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            rx.hstack(
                rx.badge(f"{recipe.calories} kcal / serv", color_scheme="orange", variant="surface", size="1"),
                rx.badge(f"{recipe.protein}g Protein / serv", color_scheme="blue", variant="surface", size="1"),
                rx.badge(f"{recipe.carbs}g Carbs / serv", color_scheme="amber", variant="surface", size="1"),
                rx.badge(f"{recipe.fat}g Fat / serv", color_scheme="green", variant="surface", size="1"),
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


def render_editable_ingredient(ing: Ingredient, index: int) -> rx.Component:
    """Renders an editable ingredient row inside the Recipe Dialog."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.badge(f"#{index + 1}", size="1", color_scheme="purple", variant="soft"),
                    rx.input(
                        placeholder="Ingredient name (e.g. Oats)",
                        value=ing.name,
                        on_change=lambda val: RecipeDialogState.update_ingredient_name(index, val),
                        size="2",
                        flex="1",
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                ),
                rx.hstack(
                    rx.input(
                        type="number",
                        placeholder="Weight",
                        value=ing.weight_g,
                        on_change=lambda val: RecipeDialogState.update_ingredient_weight(index, val),
                        size="2",
                        style={"width": "80px"},
                    ),
                    rx.text("g", size="1", color_scheme="gray"),
                    spacing="1",
                    align="center",
                ),
                rx.button(
                    rx.icon("trash-2", size=14),
                    size="1",
                    color_scheme="red",
                    variant="soft",
                    on_click=lambda: RecipeDialogState.remove_ingredient(index),
                    style={"cursor": "pointer"},
                ),
                justify="between",
                align="center",
                width="100%",
                spacing="2",
            ),
            rx.hstack(
                rx.text("Macros per 100g:", size="1", color_scheme="gray", weight="bold"),
                rx.hstack(
                    rx.input(
                        type="number",
                        placeholder="kcal",
                        value=ing.macros_per_100g.calories,
                        on_change=lambda val: RecipeDialogState.update_ingredient_calories(index, val),
                        size="1",
                        style={"width": "68px"},
                    ),
                    rx.text("kcal", size="1", color_scheme="gray"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.input(
                        type="number",
                        placeholder="protein",
                        value=ing.macros_per_100g.protein,
                        on_change=lambda val: RecipeDialogState.update_ingredient_protein(index, val),
                        size="1",
                        style={"width": "62px"},
                    ),
                    rx.text("p", size="1", color_scheme="gray"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.input(
                        type="number",
                        placeholder="carbs",
                        value=ing.macros_per_100g.carbs,
                        on_change=lambda val: RecipeDialogState.update_ingredient_carbs(index, val),
                        size="1",
                        style={"width": "62px"},
                    ),
                    rx.text("c", size="1", color_scheme="gray"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.input(
                        type="number",
                        placeholder="fat",
                        value=ing.macros_per_100g.fat,
                        on_change=lambda val: RecipeDialogState.update_ingredient_fat(index, val),
                        size="1",
                        style={"width": "62px"},
                    ),
                    rx.text("f", size="1", color_scheme="gray"),
                    spacing="1",
                    align="center",
                ),
                spacing="2",
                align="center",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        size="1",
        style={
            "background": "var(--gray-3)",
            "border": "1px solid var(--gray-5)",
            "border_radius": "8px",
            "padding": "8px 10px",
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
                        f"{RecipesState.recipe_count} recipes",
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
                    on_click=RecipeDialogState.open_add_recipe,
                    style={"cursor": "pointer", "border_radius": "8px"},
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(size="4"),
            rx.cond(
                RecipesState.recipe_count == 0,
                rx.vstack(
                    rx.icon("book-x", size=36, color="var(--gray-8)"),
                    rx.text("No saved recipes yet.", size="2", weight="bold"),
                    rx.text(
                        "Create a recipe manually or ask the AI Assistant e.g. 'Create a recipe for Protein Smoothie'!",
                        size="2",
                        color_scheme="gray",
                    ),
                    align="center",
                    padding_y="8",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(RecipesState.recipes, render_recipe_item),
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
            rx.dialog.title(RecipeDialogState.modal_title),
            rx.dialog.description(
                "Enter recipe details, preparation instructions, and ingredients.",
                size="2",
                margin_bottom="4",
            ),
            rx.flex(
                rx.vstack(
                    rx.vstack(
                        rx.text("Recipe Title", size="2", weight="bold"),
                        rx.input(
                            placeholder="e.g. Protein Oatmeal Bowl",
                            value=RecipeDialogState.name,
                            on_change=RecipeDialogState.set_name,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Instructions (Optional)", size="2", weight="bold"),
                        rx.text_area(
                            placeholder="e.g.\n1. Season salmon with salt and pepper.\n2. Sear in a pan for 4 mins each side.\n3. Serve over cooked rice and steamed broccoli.",
                            value=RecipeDialogState.instructions,
                            on_change=RecipeDialogState.set_instructions,
                            size="3",
                            width="100%",
                            rows="4",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Servings", size="2", weight="bold"),
                        rx.input(
                            type="number",
                            value=RecipeDialogState.servings,
                            on_change=RecipeDialogState.set_servings,
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Ingredients", size="2", weight="bold"),
                            rx.button(
                                rx.icon("plus", size=14),
                                "Add Ingredient",
                                size="1",
                                variant="soft",
                                color_scheme="purple",
                                on_click=RecipeDialogState.add_ingredient,
                                style={"cursor": "pointer"},
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.foreach(RecipeDialogState.ingredients, render_editable_ingredient),
                            spacing="2",
                            width="100%",
                            style={"max_height": "260px", "overflow_y": "auto", "padding_right": "4px"},
                        ),
                        spacing="2",
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
                        on_click=RecipeDialogState.close_modal,
                    ),
                ),
                rx.button(
                    "Save Recipe",
                    color_scheme="purple",
                    on_click=RecipeDialogState.save_recipe,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={"max_width": "580px"},
        ),
        open=RecipeDialogState.show_modal,
        on_open_change=RecipeDialogState.set_show_modal,
    )
