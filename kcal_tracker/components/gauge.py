import reflex as rx
from kcal_tracker.states import NutritionState


def calorie_gauge() -> rx.Component:
    """Circular visual gauge for Calorie target vs eaten."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("flame", color="var(--orange-9)", size=20),
                    rx.heading("Calories", size="4", weight="bold"),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    NutritionState.is_calorie_over,
                    rx.badge("OVER LIMIT", color_scheme="red", variant="solid", radius="full"),
                    rx.badge(
                        f"{NutritionState.remaining_calories} kcal left",
                        color_scheme="orange",
                        variant="soft",
                        radius="full",
                    ),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.flex(
                # Circular Progress Ring
                rx.box(
                    rx.html(
                        f"""
                        <svg viewBox="0 0 160 160" class="w-36 h-36 transform -rotate-90">
                            <circle cx="80" cy="80" r="65" stroke="currentColor" stroke-width="12" fill="transparent" class="text-gray-200 dark:text-gray-800" />
                            <circle cx="80" cy="80" r="65" stroke="currentColor" stroke-width="12" fill="transparent" 
                                    stroke-dasharray="408.4" 
                                    stroke-dashoffset="{408.4 - (NutritionState.calorie_percentage / 100.0) * 408.4}"
                                    stroke-linecap="round"
                                    class="text-orange-500 transition-all duration-700 ease-out" />
                        </svg>
                        """
                    ),
                    rx.vstack(
                        rx.heading(f"{NutritionState.total_calories}", size="7", weight="bold"),
                        rx.text(f"/ {NutritionState.target_calories} kcal", size="2", color_scheme="gray"),
                        rx.badge(
                            f"{NutritionState.calorie_percentage}%",
                            color_scheme="orange",
                            variant="surface",
                            size="1",
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
                    justify_content="center",
                ),
                justify="center",
                align="center",
                width="100%",
                padding_y="3",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Eaten", size="1", color_scheme="gray"),
                    rx.text(f"{NutritionState.total_calories} kcal", size="2", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.divider(orientation="vertical", size="2"),
                rx.vstack(
                    rx.text("Target", size="1", color_scheme="gray"),
                    rx.text(f"{NutritionState.target_calories} kcal", size="2", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.divider(orientation="vertical", size="2"),
                rx.vstack(
                    rx.text("Remaining", size="1", color_scheme="gray"),
                    rx.text(
                        f"{NutritionState.remaining_calories} kcal",
                        size="2",
                        weight="bold",
                        color_scheme="orange",
                    ),
                    align="center",
                    spacing="0",
                ),
                justify="between",
                width="100%",
                padding_top="2",
                border_top="1px solid var(--gray-4)",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        variant="surface",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "box_shadow": "0 4px 20px rgba(0,0,0,0.03)",
        },
        width="100%",
    )


def protein_gauge() -> rx.Component:
    """Circular visual gauge for Protein target vs eaten."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("dumbbell", color="var(--blue-9)", size=20),
                    rx.heading("Protein", size="4", weight="bold"),
                    spacing="2",
                    align="center",
                ),
                rx.badge(
                    f"{NutritionState.remaining_protein}g left",
                    color_scheme="blue",
                    variant="soft",
                    radius="full",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.flex(
                # Circular Progress Ring
                rx.box(
                    rx.html(
                        f"""
                        <svg viewBox="0 0 160 160" class="w-36 h-36 transform -rotate-90">
                            <circle cx="80" cy="80" r="65" stroke="currentColor" stroke-width="12" fill="transparent" class="text-gray-200 dark:text-gray-800" />
                            <circle cx="80" cy="80" r="65" stroke="currentColor" stroke-width="12" fill="transparent" 
                                    stroke-dasharray="408.4" 
                                    stroke-dashoffset="{408.4 - (NutritionState.protein_percentage / 100.0) * 408.4}"
                                    stroke-linecap="round"
                                    class="text-blue-500 transition-all duration-700 ease-out" />
                        </svg>
                        """
                    ),
                    rx.vstack(
                        rx.heading(f"{NutritionState.total_protein}g", size="7", weight="bold"),
                        rx.text(f"/ {NutritionState.target_protein}g target", size="2", color_scheme="gray"),
                        rx.badge(
                            f"{NutritionState.protein_percentage}%",
                            color_scheme="blue",
                            variant="surface",
                            size="1",
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
                    justify_content="center",
                ),
                justify="center",
                align="center",
                width="100%",
                padding_y="3",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Eaten", size="1", color_scheme="gray"),
                    rx.text(f"{NutritionState.total_protein}g", size="2", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.divider(orientation="vertical", size="2"),
                rx.vstack(
                    rx.text("Target", size="1", color_scheme="gray"),
                    rx.text(f"{NutritionState.target_protein}g", size="2", weight="bold"),
                    align="center",
                    spacing="0",
                ),
                rx.divider(orientation="vertical", size="2"),
                rx.vstack(
                    rx.text("Remaining", size="1", color_scheme="gray"),
                    rx.text(
                        f"{NutritionState.remaining_protein}g",
                        size="2",
                        weight="bold",
                        color_scheme="blue",
                    ),
                    align="center",
                    spacing="0",
                ),
                justify="between",
                width="100%",
                padding_top="2",
                border_top="1px solid var(--gray-4)",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        variant="surface",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "box_shadow": "0 4px 20px rgba(0,0,0,0.03)",
        },
        width="100%",
    )


def macro_progress_cards() -> rx.Component:
    """Carbs and Fat linear progress cards."""
    return rx.grid(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.icon("wheat", color="var(--amber-9)", size=16),
                        rx.text("Carbs", size="2", weight="bold"),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        f"{NutritionState.total_carbs} / {NutritionState.target_carbs}g",
                        size="2",
                        weight="bold",
                    ),
                    justify="between",
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
            size="2",
            style={
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "12px",
            },
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.icon("droplet", color="var(--green-9)", size=16),
                        rx.text("Fats", size="2", weight="bold"),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        f"{NutritionState.total_fat} / {NutritionState.target_fat}g",
                        size="2",
                        weight="bold",
                    ),
                    justify="between",
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
            size="2",
            style={
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "12px",
            },
        ),
        columns=rx.breakpoints(initial="1", sm="2"),
        spacing="3",
        width="100%",
    )


def mobile_calorie_gauge() -> rx.Component:
    """Smaller Calorie Mini Gauge Card for mobile screens."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("flame", color="var(--orange-9)", size=14),
                    rx.text("Calories", size="1", weight="bold"),
                    spacing="1",
                    align="center",
                ),
                rx.cond(
                    NutritionState.is_calorie_over,
                    rx.badge("OVER", color_scheme="red", size="1"),
                    rx.badge(f"{NutritionState.remaining_calories} left", color_scheme="orange", variant="soft", size="1"),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.flex(
                rx.box(
                    rx.html(
                        f"""
                        <svg viewBox="0 0 90 90" width="90" height="90" style="transform: rotate(-90deg);">
                            <circle cx="45" cy="45" r="35" stroke="currentColor" stroke-width="8" fill="transparent" class="text-gray-200 dark:text-gray-800" />
                            <circle cx="45" cy="45" r="35" stroke="currentColor" stroke-width="8" fill="transparent" 
                                    stroke-dasharray="219.9" 
                                    stroke-dashoffset="{219.9 - (NutritionState.calorie_percentage / 100.0) * 219.9}"
                                    stroke-linecap="round"
                                    class="text-orange-500 transition-all duration-700 ease-out" />
                        </svg>
                        """
                    ),
                    rx.vstack(
                        rx.heading(f"{NutritionState.total_calories}", size="3", weight="bold"),
                        rx.text(f"/ {NutritionState.target_calories}", size="1", color_scheme="gray"),
                        spacing="0",
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
                padding_y="1",
            ),
            rx.hstack(
                rx.text(f"Eaten: {NutritionState.total_calories}", size="1", color_scheme="gray"),
                rx.text(f"{NutritionState.calorie_percentage}%", size="1", weight="bold", color_scheme="orange"),
                justify="between",
                width="100%",
            ),
            spacing="1",
            align="center",
            width="100%",
        ),
        size="1",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "12px",
            "padding": "8px 10px",
        },
        width="100%",
    )


def mobile_protein_gauge() -> rx.Component:
    """Smaller Protein Mini Gauge Card for mobile screens."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("dumbbell", color="var(--blue-9)", size=14),
                    rx.text("Protein", size="1", weight="bold"),
                    spacing="1",
                    align="center",
                ),
                rx.badge(f"{NutritionState.remaining_protein}g left", color_scheme="blue", variant="soft", size="1"),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.flex(
                rx.box(
                    rx.html(
                        f"""
                        <svg viewBox="0 0 90 90" width="90" height="90" style="transform: rotate(-90deg);">
                            <circle cx="45" cy="45" r="35" stroke="currentColor" stroke-width="8" fill="transparent" class="text-gray-200 dark:text-gray-800" />
                            <circle cx="45" cy="45" r="35" stroke="currentColor" stroke-width="8" fill="transparent" 
                                    stroke-dasharray="219.9" 
                                    stroke-dashoffset="{219.9 - (NutritionState.protein_percentage / 100.0) * 219.9}"
                                    stroke-linecap="round"
                                    class="text-blue-500 transition-all duration-700 ease-out" />
                        </svg>
                        """
                    ),
                    rx.vstack(
                        rx.heading(f"{NutritionState.total_protein}g", size="3", weight="bold"),
                        rx.text(f"/ {NutritionState.target_protein}g", size="1", color_scheme="gray"),
                        spacing="0",
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
                padding_y="1",
            ),
            rx.hstack(
                rx.text(f"Eaten: {NutritionState.total_protein}g", size="1", color_scheme="gray"),
                rx.text(f"{NutritionState.protein_percentage}%", size="1", weight="bold", color_scheme="blue"),
                justify="between",
                width="100%",
            ),
            spacing="1",
            align="center",
            width="100%",
        ),
        size="1",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "12px",
            "padding": "8px 10px",
        },
        width="100%",
    )


def mobile_macro_progress_cards() -> rx.Component:
    """Compact Carbs & Fat linear progress cards for mobile screens."""
    return rx.grid(
        rx.card(
            rx.hstack(
                rx.icon("wheat", color="var(--amber-9)", size=13),
                rx.vstack(
                    rx.hstack(
                        rx.text("Carbs", size="1", weight="bold"),
                        rx.text(f"{NutritionState.total_carbs}/{NutritionState.target_carbs}g", size="1", color_scheme="gray"),
                        justify="between",
                        width="100%",
                    ),
                    rx.progress(value=NutritionState.carbs_percentage, color_scheme="amber", size="1", radius="full"),
                    spacing="1",
                    width="100%",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            size="1",
            style={
                "background": "var(--gray-1)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "10px",
                "padding": "6px 8px",
            },
        ),
        rx.card(
            rx.hstack(
                rx.icon("droplet", color="var(--green-9)", size=13),
                rx.vstack(
                    rx.hstack(
                        rx.text("Fat", size="1", weight="bold"),
                        rx.text(f"{NutritionState.total_fat}/{NutritionState.target_fat}g", size="1", color_scheme="gray"),
                        justify="between",
                        width="100%",
                    ),
                    rx.progress(value=NutritionState.fat_percentage, color_scheme="green", size="1", radius="full"),
                    spacing="1",
                    width="100%",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            size="1",
            style={
                "background": "var(--gray-1)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "10px",
                "padding": "6px 8px",
            },
        ),
        columns="2",
        spacing="2",
        width="100%",
    )
