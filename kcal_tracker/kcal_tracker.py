import reflex as rx
from kcal_tracker.state import State
from kcal_tracker.components.navbar import navbar
from kcal_tracker.components.dashboard import dashboard_summary, target_dialog
from kcal_tracker.components.meals import meals_section, meal_dialog
from kcal_tracker.components.recipes import recipes_section, recipe_dialog
from kcal_tracker.components.chat import chat_section
from reflex_google_auth import google_login, google_oauth_provider, require_google_login
from kcal_tracker.models.google_login import UserState
import kcal_tracker.content as content


def login_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Welcome to Kcal AI Tracker", size="5"),
        rx.text("Please log in with Google to access your dashboard:"),
        # The button triggers UserState.on_success automatically upon login
        google_login(on_success=UserState.on_success),
        align="center",
        justify="center",
        spacing="5",
        padding_y="9",
    )


def index() -> rx.Component:
    return google_oauth_provider(
        rx.box(
            rx.cond(
                UserState.token_is_valid,
                content.main_content(),
                login_content(),
            ),
            min_height="100vh",
            background="var(--gray-1)",
        )
    )


app = rx.App()
app.add_page(index, title="Kcal AI Tracker - Calorie & Macro Tracker")