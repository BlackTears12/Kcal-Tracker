import reflex as rx
from kcal_tracker.states import NutritionState


def calorie_gauge() -> rx.Component:
    """Single circular visual gauge for Calorie target vs eaten (Material Dark Style)."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("flame", color="white", size=20),
                        style={
                            "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                            "padding": "6px",
                            "border_radius": "10px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                            "box_shadow": "0 2px 8px rgba(255, 107, 107, 0.35)",
                        },
                    ),
                    rx.vstack(
                        rx.heading("Daily Calories", size="4", weight="bold"),
                        rx.text("Caloric Intake Target", size="1", color_scheme="gray"),
                        spacing="0",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    NutritionState.is_calorie_over,
                    rx.badge("OVER LIMIT", color_scheme="red", variant="solid", radius="full", size="2"),
                    rx.badge(
                        f"{NutritionState.remaining_calories} kcal left",
                        color_scheme="orange",
                        variant="soft",
                        radius="full",
                        size="2",
                    ),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            # Circular Gauge Ring
            rx.flex(
                rx.box(
                    rx.html(
                        f"""
                        <svg viewBox="0 0 180 180" class="w-44 h-44 transform -rotate-90">
                            <!-- Background Track Ring -->
                            <circle cx="90" cy="90" r="74" 
                                    stroke="rgba(255, 255, 255, 0.08)" 
                                    stroke-width="12" 
                                    fill="transparent" />
                            <!-- Active Progress Ring -->
                            <circle cx="90" cy="90" r="74" 
                                    stroke="url(#calorieGradient)" 
                                    stroke-width="12" 
                                    fill="transparent" 
                                    stroke-dasharray="464.95" 
                                    stroke-dashoffset="{464.95 - (NutritionState.calorie_percentage / 100.0) * 464.95}"
                                    stroke-linecap="round"
                                    class="transition-all duration-700 ease-out" />
                            <defs>
                                <linearGradient id="calorieGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#FF6B6B" />
                                    <stop offset="100%" stop-color="#FF8E53" />
                                </linearGradient>
                            </defs>
                        </svg>
                        """
                    ),
                    rx.vstack(
                        rx.heading(
                            f"{NutritionState.total_calories}",
                            size="8",
                            weight="bold",
                            style={"line_height": "1"},
                        ),
                        rx.text(
                            f"/ {NutritionState.target_calories} kcal",
                            size="2",
                            color_scheme="gray",
                            weight="medium",
                        ),
                        rx.badge(
                            f"{NutritionState.calorie_percentage}%",
                            color_scheme="orange",
                            variant="surface",
                            size="1",
                            radius="full",
                        ),
                        spacing="1",
                        align="center",
                        position="absolute",
                        top="50%",
                        left="50%",
                        transform="translate(-50%, -50%)",
                    ),
                    position="relative",
                    display="flex",
                    align_items="center",
                    justify="center",
                ),
                justify="center",
                align="center",
                width="100%",
                padding_y="4",
            ),
            # Bottom Stat Breakdown Row
            rx.grid(
                rx.vstack(
                    rx.text("Eaten", size="1", color_scheme="gray", weight="medium"),
                    rx.text(f"{NutritionState.total_calories} kcal", size="3", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Target", size="1", color_scheme="gray", weight="medium"),
                    rx.text(f"{NutritionState.target_calories} kcal", size="3", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Remaining", size="1", color_scheme="gray", weight="medium"),
                    rx.text(
                        f"{NutritionState.remaining_calories} kcal",
                        size="3",
                        weight="bold",
                        color_scheme="orange",
                    ),
                    align="center",
                    spacing="0",
                ),
                columns="3",
                width="100%",
                padding_top="3",
                border_top="1px solid var(--gray-4)",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "20px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
        },
        width="100%",
    )


def macro_progress_bars() -> rx.Component:
    """3 linear progress bars for Protein, Carbs, and Fat (Material Dark Style)."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("chart-bar", color="var(--orange-9)", size=18),
                    rx.heading("Macronutrients", size="3", weight="bold"),
                    spacing="2",
                    align="center",
                ),
                rx.text("Daily Targets", size="1", color_scheme="gray"),
                justify="between",
                align="center",
                width="100%",
            ),
            # 1. Protein Progress Bar
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("dumbbell", size=14, color="#38BDF8"),
                                style={
                                    "background": "rgba(56, 189, 248, 0.15)",
                                    "padding": "4px",
                                    "border_radius": "6px",
                                    "display": "flex",
                                    "align_items": "center",
                                    "justify_content": "center",
                                },
                            ),
                            rx.text("Protein", size="2", weight="bold"),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.text(
                                f"{NutritionState.total_protein} / {NutritionState.target_protein}g",
                                size="2",
                                weight="bold",
                            ),
                            rx.badge(
                                f"{NutritionState.protein_percentage}%",
                                color_scheme="blue",
                                variant="soft",
                                size="1",
                                radius="full",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    rx.progress(
                        value=NutritionState.protein_percentage,
                        color_scheme="blue",
                        size="2",
                        radius="full",
                    ),
                    spacing="2",
                    width="100%",
                ),
                style={
                    "background": "var(--gray-1)",
                    "border": "1px solid var(--gray-4)",
                    "border_radius": "12px",
                    "padding": "12px 14px",
                    "width": "100%",
                },
            ),
            # 2. Carbs Progress Bar
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("wheat", size=14, color="#FBBF24"),
                                style={
                                    "background": "rgba(251, 191, 36, 0.15)",
                                    "padding": "4px",
                                    "border_radius": "6px",
                                    "display": "flex",
                                    "align_items": "center",
                                    "justify_content": "center",
                                },
                            ),
                            rx.text("Carbs", size="2", weight="bold"),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.text(
                                f"{NutritionState.total_carbs} / {NutritionState.target_carbs}g",
                                size="2",
                                weight="bold",
                            ),
                            rx.badge(
                                f"{NutritionState.carbs_percentage}%",
                                color_scheme="amber",
                                variant="soft",
                                size="1",
                                radius="full",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    rx.progress(
                        value=NutritionState.carbs_percentage,
                        color_scheme="amber",
                        size="2",
                        radius="full",
                    ),
                    spacing="2",
                    width="100%",
                ),
                style={
                    "background": "var(--gray-1)",
                    "border": "1px solid var(--gray-4)",
                    "border_radius": "12px",
                    "padding": "12px 14px",
                    "width": "100%",
                },
            ),
            # 3. Fat Progress Bar
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("droplet", size=14, color="#34D399"),
                                style={
                                    "background": "rgba(52, 211, 153, 0.15)",
                                    "padding": "4px",
                                    "border_radius": "6px",
                                    "display": "flex",
                                    "align_items": "center",
                                    "justify_content": "center",
                                },
                            ),
                            rx.text("Fat", size="2", weight="bold"),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.text(
                                f"{NutritionState.total_fat} / {NutritionState.target_fat}g",
                                size="2",
                                weight="bold",
                            ),
                            rx.badge(
                                f"{NutritionState.fat_percentage}%",
                                color_scheme="green",
                                variant="soft",
                                size="1",
                                radius="full",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    rx.progress(
                        value=NutritionState.fat_percentage,
                        color_scheme="green",
                        size="2",
                        radius="full",
                    ),
                    spacing="2",
                    width="100%",
                ),
                style={
                    "background": "var(--gray-1)",
                    "border": "1px solid var(--gray-4)",
                    "border_radius": "12px",
                    "padding": "12px 14px",
                    "width": "100%",
                },
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "20px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
        },
        width="100%",
    )


# Alias helper names for compatibility
macro_progress_cards = macro_progress_bars
mobile_calorie_gauge = calorie_gauge
mobile_protein_gauge = macro_progress_bars
mobile_macro_progress_cards = macro_progress_bars
