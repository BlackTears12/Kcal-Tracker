import reflex as rx
from reflex_google_auth import google_login, google_oauth_provider, require_google_login
from kcal_tracker.models.login import Login
import kcal_tracker.content as content

def login_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Welcome to Kcal AI Tracker", size="5"),
        rx.text("Please log in with Google to access your dashboard:"),
        # The button triggers UserState.on_success automatically upon login
        google_login(on_success=Login.on_success),
        align="center",
        justify="center",
        spacing="5",
        padding_y="9",
    )


def index() -> rx.Component:
    return google_oauth_provider(
        rx.box(
            rx.cond(
                Login.token_is_valid,
                content.main_content(),
                login_content(),
            ),
            min_height="100vh",
            background="var(--gray-1)",
        )
    )


app = rx.App()
app.add_page(
    index,
    title="Kcal AI Tracker - Calorie & Macro Tracker",
    on_load=Login.on_login, # type: ignore
)