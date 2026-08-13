import reflex as rx
from kcal_tracker.state import State
from kcal_tracker.components.navbar import navbar
from kcal_tracker.components.dashboard import dashboard_summary, target_dialog
from kcal_tracker.components.meals import meals_section, meal_dialog
from kcal_tracker.components.recipes import recipes_section, recipe_dialog
from kcal_tracker.components.chat import chat_section

def index() -> rx.Component:
    """Main page container for Calorie Tracker fullstack app."""
    return rx.box(
        navbar(),
        rx.container(
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
                            f"{State.total_calories} / {State.target_calories} Kcal",
                            color_scheme="orange",
                            variant="surface",
                            size="2",
                        ),
                        rx.badge(
                            f"{State.total_protein} / {State.target_protein}g Protein",
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
        ),
        min_height="100vh",
        background="var(--gray-1)",
    )


app = rx.App()
app.add_page(index, title="Kcal AI Tracker - Calorie & Macro Tracker")

