import reflex as rx
from kcal_tracker.data.body import Measurement, MeasurementInput, SiteSummary
from kcal_tracker.states import BodyState, BodyDialogState, NutritionState


def render_history_entry(entry: Measurement, site: str) -> rx.Component:
    """One past measurement of a site in its unfolded history."""
    return rx.hstack(
        rx.text(entry.date_text, size="2", color_scheme="gray", flex="1"),
        rx.text(f"{entry.value_cm} cm", size="2", weight="medium"),
        rx.button(
            rx.icon("trash-2", size=12),
            size="1",
            variant="ghost",
            color_scheme="red",
            on_click=lambda: BodyState.remove_measurement(site, entry.date_iso),
            style={"cursor": "pointer"},
        ),
        align="center",
        spacing="3",
        width="100%",
    )


def render_site_summary(summary: SiteSummary) -> rx.Component:
    """Renders a measured body site: latest value, change since the previous one, and its history on tap."""
    is_expanded = BodyState.expanded_site == summary.site
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.hstack(
                    rx.box(
                        rx.icon("ruler", size=18, color="var(--gray-11)"),
                        style={
                            "background": "var(--gray-3)",
                            "padding": "8px",
                            "border_radius": "10px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                            "min_width": "34px",
                        },
                    ),
                    rx.vstack(
                        rx.heading(summary.site, size="3", weight="bold"),
                        rx.text(
                            rx.cond(summary.change_text != "", summary.change_text, summary.latest_date_text),
                            size="1",
                            color_scheme="gray",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                    min_width="0",
                ),
                rx.hstack(
                    rx.cond(
                        summary.change_cm != 0,
                        rx.badge(
                            rx.cond(summary.change_cm > 0, rx.icon("arrow-up", size=12), rx.icon("arrow-down", size=12)),
                            f"{summary.change_cm} cm",
                            color_scheme="gray",
                            variant="surface",
                            size="1",
                        ),
                    ),
                    rx.heading(f"{summary.latest_cm} cm", size="4", weight="bold"),
                    rx.icon(rx.cond(is_expanded, "chevron-up", "chevron-down"), size=16, color="var(--gray-10)"),
                    spacing="2",
                    align="center",
                    flex_shrink="0",
                ),
                justify="between",
                align="center",
                width="100%",
                gap="2",
                on_click=lambda: BodyState.toggle_site(summary.site),
                style={"cursor": "pointer"},
            ),
            rx.cond(
                is_expanded,
                rx.vstack(
                    rx.foreach(summary.history, lambda entry: render_history_entry(entry, summary.site)),
                    spacing="1",
                    width="100%",
                    padding_top="2",
                    border_top="1px solid var(--gray-4)",
                ),
            ),
            spacing="2",
            width="100%",
        ),
        size="2",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "14px",
            "padding": "12px 14px",
            "transition": "all 0.2s ease",
            "overflow": "hidden",
            "&:hover": {
                "border_color": "var(--gray-6)",
                "box_shadow": "0 2px 12px rgba(0,0,0,0.2)",
            },
        },
        width="100%",
    )


def body_section() -> rx.Component:
    """Body measurements section: latest value per site (Material Dark Style)."""
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.hstack(
                    rx.box(
                        rx.icon("ruler", size=18, color="white"),
                        style={
                            "background": "linear-gradient(135deg, #2DD4BF 0%, #059669 100%)",
                            "padding": "6px",
                            "border_radius": "10px",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                        },
                    ),
                    rx.heading("Body Measurements", size="4", weight="bold"),
                    rx.badge(
                        f"{BodyState.site_count} sites",
                        color_scheme="teal",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                    min_width="0",
                    wrap="wrap",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Log Measurements",
                    size="2",
                    color_scheme="teal",
                    on_click=BodyDialogState.open_modal,
                    style={
                        "cursor": "pointer",
                        "border_radius": "10px",
                        "flex_shrink": "0",
                        "margin_left": "auto",
                    },
                ),
                justify="between",
                align="center",
                width="100%",
                gap="2",
                wrap="wrap",
            ),
            rx.divider(size="4"),
            rx.cond(
                BodyState.site_count == 0,
                rx.vstack(
                    rx.icon("ruler", size=40, color="var(--gray-8)"),
                    rx.text("No measurements logged yet.", size="3", weight="bold"),
                    rx.text(
                        "Click '+ Log Measurements' to record your waist, hips, arms and more, and follow how they change.",
                        size="2",
                        color_scheme="gray",
                        text_align="center",
                    ),
                    align="center",
                    padding_y="8",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(BodyState.summaries, render_site_summary),
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
            "border_radius": "20px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
        },
        width="100%",
    )


def render_measurement_input(row: MeasurementInput, index: int) -> rx.Component:
    """A body site with its value field in the log dialog."""
    return rx.vstack(
        rx.text(row.site, size="2", weight="bold"),
        rx.input(
            type="number",
            placeholder="cm",
            value=row.value,
            on_change=lambda val: BodyDialogState.set_row_value(index, val),
            size="2",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def body_dialog() -> rx.Component:
    """Dialog modal for logging the viewed day's body measurements (Material Dark Style)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(f"Body Measurements · {NutritionState.short_date}"),
            rx.dialog.description(
                "Fill in what you measured, in cm. Clear a field to remove that day's value.",
                size="2",
                margin_bottom="4",
            ),
            rx.vstack(
                rx.grid(
                    rx.foreach(BodyDialogState.rows, render_measurement_input),
                    columns=rx.breakpoints(initial="2", sm="3"),
                    spacing="3",
                    width="100%",
                    style={"max_height": "380px", "overflow_y": "auto", "padding_right": "4px"},
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Other measurement (e.g. Wrist)",
                        value=BodyDialogState.new_site,
                        on_change=BodyDialogState.set_new_site,
                        size="2",
                        flex="1",
                    ),
                    rx.button(
                        rx.icon("plus", size=14),
                        "Add",
                        size="2",
                        variant="soft",
                        color_scheme="teal",
                        on_click=BodyDialogState.add_custom_site,
                        style={"cursor": "pointer"},
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=BodyDialogState.close_modal,
                    ),
                ),
                rx.button(
                    "Save Measurements",
                    color_scheme="teal",
                    on_click=BodyDialogState.save,
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            style={
                "max_width": "560px",
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "20px",
            },
        ),
        open=BodyDialogState.show_modal,
        on_open_change=BodyDialogState.set_show_modal,
    )
