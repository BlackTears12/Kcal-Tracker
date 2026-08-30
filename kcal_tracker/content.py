import reflex as rx
from kcal_tracker.states import NutritionState, UIState
from kcal_tracker.components.navbar import navbar
from kcal_tracker.components.dashboard import (
    date_navigator,
    dashboard_summary,
    content_menubar,
    target_dialog,
    desktop_date_navigator,
    mobile_date_navigator,
    mobile_macro_summary,
    mobile_nav_pills,
)
from kcal_tracker.components.meals import meals_section, meal_dialog
from kcal_tracker.components.recipes import recipes_section, recipe_dialog
from kcal_tracker.components.chat import chat_dialog, chat_fab, chat_section


def main_content() -> rx.Component:
    """Material Dark App Layout based on New-ui-design.md specifications."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # 1. Date Navigator (Content: The date (or today) with previous/next day buttons)
                date_navigator(),

                # 2. Dashboard: 1 circular gauge (eaten/total calories) + 3 progress bars (protein, carbs, fat)
                dashboard_summary(),

                # 3. Menubar: choose either logged meal, recipes or all to display
                content_menubar(),

                # 4. Content Display Area (Logged Meals / Recipes / All)
                rx.cond(
                    UIState.is_meals_active,
                    meals_section(),
                ),
                rx.cond(
                    UIState.is_recipes_active,
                    recipes_section(),
                ),

                spacing="5",
                width="100%",
                padding_y="5",
            ),
            size="3",
            max_width="980px",
            padding_x=rx.breakpoints(initial="3", sm="4"),
        ),

        # Dialog Modals
        meal_dialog(),
        recipe_dialog(),
        target_dialog(),
        chat_dialog(),

        # 5. Chat Icon in Lower Right (Floating Action Button opening Agent Chat)
        chat_fab(),

        width="100%",
        min_height="100vh",
        background="var(--gray-1)",
    )


# Compatibility aliases
def desktop_content() -> rx.Component:
    return main_content()


def mobile_content() -> rx.Component:
    return main_content()