import reflex as rx
from kcal_tracker.states import NutritionState, UIState
from kcal_tracker.components.navbar import navbar
from kcal_tracker.components.dashboard import (
    dashboard_summary,
    mobile_macro_summary,
    mobile_nav_pills,
    target_dialog,
)
from kcal_tracker.components.meals import meals_section, meal_dialog
from kcal_tracker.components.recipes import recipes_section, recipe_dialog
from kcal_tracker.components.chat import chat_section


def desktop_content() -> rx.Component:
    """Main page container for Calorie Tracker fullstack app."""
    return rx.container(
        navbar(),
        rx.vstack(
            # App Title & Welcome Subtitle
            rx.flex(
                rx.vstack(
                    rx.heading("Daily Calorie & Macro Dashboard", size="7", weight="bold"),
                    rx.text(
                        "Track your calories and protein targets, manage recipes, or log meals effortlessly with AI.",
                        size="3",
                        color_scheme="gray",
                    ),
                    spacing="1",
                ),
                rx.hstack(
                    rx.badge(
                        f"{NutritionState.total_calories} / {NutritionState.target_calories} Kcal",
                        color_scheme="orange",
                        variant="surface",
                        size="2",
                    ),
                    rx.badge(
                        f"{NutritionState.total_protein} / {NutritionState.target_protein}g Protein",
                        color_scheme="blue",
                        variant="surface",
                        size="2",
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
                padding_y="2",
            ),

            # Main Grid: Left = Gauges & Lists (Meals, Recipes), Right = AI Chatbot
            rx.grid(
                # Left Column: Dashboard Gauges + Logged Meals + Recipes
                rx.vstack(
                    dashboard_summary(),
                    meals_section(),
                    recipes_section(),
                    spacing="6",
                    width="100%",
                ),
                # Right Column: AI Chatbot Interface
                rx.vstack(
                    chat_section(),
                    spacing="6",
                    width="100%",
                    style={"position": "sticky", "top": "80px"},
                ),
                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="6",
                width="100%",
            ),

            # Dialog Modals
            meal_dialog(),
            recipe_dialog(),
            target_dialog(),

            spacing="6",
            width="100%",
            padding_y="6",
        ),
        size="4",
    )


def mobile_content() -> rx.Component:
    """Snappy, Android app-like mobile layout with smaller kcal & protein macros followed by AI chat."""
    return rx.box(
        rx.vstack(
            # Top App Bar Header Card (Android Native Style)
            rx.card(
                rx.flex(
                    rx.hstack(
                        rx.box(
                            rx.icon("flame", color="white", size=18),
                            style={
                                "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                                "padding": "6px",
                                "border_radius": "8px",
                                "display": "flex",
                                "align_items": "center",
                                "justify_content": "center",
                            },
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Kcal AI", size="3", weight="bold"),
                                rx.badge("Mobile App", color_scheme="orange", variant="soft", size="1"),
                                spacing="2",
                                align="center",
                            ),
                            rx.text("Track macros & AI food logging", size="1", color_scheme="gray"),
                            spacing="0",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.badge(
                            f"{NutritionState.total_calories} / {NutritionState.target_calories} kcal",
                            color_scheme="orange",
                            variant="surface",
                            size="1",
                        ),
                        rx.badge(
                            f"{NutritionState.total_protein} / {NutritionState.target_protein}g P",
                            color_scheme="blue",
                            variant="surface",
                            size="1",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                size="1",
                style={
                    "background": "var(--gray-2)",
                    "border": "1px solid var(--gray-4)",
                    "border_radius": "14px",
                    "padding": "10px 12px",
                },
                width="100%",
            ),

            # 1. Smaller Kcal & Protein Macros Summary
            mobile_macro_summary(),

            # Android App Navigation Pills
            mobile_nav_pills(),

            # 2. AI Chatbot Section (Follows smaller macros directly)
            rx.cond(
                (UIState.active_tab == "chat") | (UIState.active_tab == "all") | (UIState.active_tab == "dashboard"),
                chat_section(),
            ),

            # 3. Logged Meals Section
            rx.cond(
                (UIState.active_tab == "meals") | (UIState.active_tab == "all") | (UIState.active_tab == "dashboard"),
                meals_section(),
            ),

            # 4. Saved Recipes Section
            rx.cond(
                (UIState.active_tab == "recipes") | (UIState.active_tab == "all") | (UIState.active_tab == "dashboard"),
                recipes_section(),
            ),

            # Dialog Modals
            meal_dialog(),
            recipe_dialog(),
            target_dialog(),

            spacing="4",
            width="100%",
            padding_x="3",
            padding_y="3",
        ),
        width="100%",
        max_width="540px",
        margin="0 auto",
    )


def main_content() -> rx.Component:
    return rx.box(
        rx.desktop_only(desktop_content()),
        rx.mobile_only(mobile_content()),
    )