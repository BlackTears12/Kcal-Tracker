import reflex as rx
from kcal_tracker.states import TargetDialogState, NutritionState


def navbar() -> rx.Component:
    """Navigation bar header."""
    return rx.box(
        rx.flex(
            # Left: Brand logo & Title
            rx.hstack(
                rx.box(
                    rx.icon("flame", color="white", size=22),
                    style={
                        "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                        "padding": "8px",
                        "border_radius": "10px",
                        "box_shadow": "0 2px 10px rgba(255, 107, 107, 0.3)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("Kcal", size="5", weight="bold"),
                        rx.badge("AI Tracker", color_scheme="orange", variant="soft", size="1"),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Smart Macro & Meal Tracking",
                        size="1",
                        color_scheme="gray",
                    ),
                    spacing="0",
                ),
                align="center",
                spacing="3",
            ),
            # Right: Action Buttons & Mode Toggle
            rx.hstack(
                rx.button(
                    rx.icon("target", size=16),
                    "Set Goals",
                    variant="outline",
                    color_scheme="gray",
                    size="2",
                    on_click=TargetDialogState.open_modal,
                    style={"cursor": "pointer", "border_radius": "8px"},
                ),
                rx.button(
                    rx.icon("rotate-ccw", size=16),
                    "Reset Day",
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    on_click=NutritionState.clear_all_meals,
                    style={"cursor": "pointer", "border_radius": "8px"},
                ),
                rx.color_mode.button(size="2"),
                spacing="3",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
            max_width="1280px",
            margin="0 auto",
            padding_x="4",
            padding_y="3",
        ),
        style={
            "border_bottom": "1px solid var(--gray-4)",
            "background": "var(--gray-1)",
            "backdrop_filter": "blur(8px)",
            "position": "sticky",
            "top": "0",
            "z_index": "50",
            "width": "100%",
        },
    )
