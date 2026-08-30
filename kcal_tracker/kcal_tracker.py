import reflex as rx
from reflex_google_auth import google_login, google_oauth_provider, require_google_login
from kcal_tracker.models.login import Login
import kcal_tracker.content as content

def login_content() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.box(
                    rx.icon("flame", color="white", size=32),
                    style={
                        "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                        "padding": "12px",
                        "border_radius": "16px",
                        "box_shadow": "0 4px 16px rgba(255, 107, 107, 0.4)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.vstack(
                    rx.heading("Welcome to Kcal AI Tracker", size="6", weight="bold"),
                    rx.text(
                        "Smart Macro & Meal Tracking powered by AI",
                        size="2",
                        color_scheme="gray",
                    ),
                    align="center",
                    spacing="1",
                ),
                rx.text(
                    "Please log in with Google to access your dashboard:",
                    size="2",
                    color="var(--gray-11)",
                ),
                # The button triggers UserState.on_success automatically upon login
                google_login(on_success=Login.on_success),
                align="center",
                justify="center",
                spacing="5",
                padding_y="4",
                width="100%",
            ),
            size="4",
            style={
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "24px",
                "box_shadow": "0 12px 40px rgba(0, 0, 0, 0.35)",
                "max_width": "420px",
                "width": "90vw",
            },
        ),
        min_height="80vh",
        padding_y="8",
    )


def index() -> rx.Component:
    return google_oauth_provider(
        rx.box(
            rx.cond(
                Login.is_valid_login,
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