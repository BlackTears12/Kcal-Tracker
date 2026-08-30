import reflex as rx
from kcal_tracker.states import (
    ChatMessage,
    ChatState,
    UIState,
)


def render_chat_message(msg: ChatMessage) -> rx.Component:
    """Renders a compact chat message bubble in dark styling."""
    return rx.flex(
        rx.cond(
            msg.is_ai,
            # AI Message (Left Aligned)
            rx.hstack(
                rx.box(
                    rx.icon("sparkles", size=13, color="white"),
                    style={
                        "width": "24px",
                        "height": "24px",
                        "min_width": "24px",
                        "border_radius": "50%",
                        "background": "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "margin_top": "2px",
                    },
                ),
                rx.vstack(
                    rx.box(
                        rx.vstack(
                            rx.cond(
                                msg.action != "",
                                rx.badge(
                                    msg.action,
                                    color_scheme="purple",
                                    variant="surface",
                                    size="1",
                                    radius="full",
                                ),
                            ),
                            rx.markdown(
                                msg.content,
                                style={
                                    "font_size": "13px",
                                    "line_height": "1.45",
                                    "color": "var(--gray-12)",
                                    "& p": {"margin_bottom": "4px", "&:last-child": {"margin_bottom": "0px"}},
                                    "& ul": {"padding_left": "16px", "margin_bottom": "4px"},
                                    "& ol": {"padding_left": "16px", "margin_bottom": "4px"},
                                    "& li": {"margin_bottom": "2px"},
                                },
                            ),
                            spacing="1",
                        ),
                        style={
                            "background": "var(--gray-3)",
                            "border": "1px solid var(--gray-5)",
                            "padding": "8px 11px",
                            "border_radius": "14px 14px 14px 4px",
                            "box_shadow": "0 1px 4px rgba(0, 0, 0, 0.12)",
                        },
                    ),
                    rx.text(
                        msg.time_str,
                        size="1",
                        color="var(--gray-9)",
                        style={"font_size": "9px", "padding_left": "4px"},
                    ),
                    spacing="1",
                    align="start",
                    max_width="86%",
                ),
                spacing="2",
                align="start",
                justify="start",
                width="100%",
            ),
            # User Message (Right Aligned)
            rx.flex(
                rx.vstack(
                    rx.box(
                        rx.text(
                            msg.content,
                            size="2",
                            color="white",
                            weight="medium",
                            style={"white_space": "pre-wrap", "word_break": "break-word", "font_size": "13px"},
                        ),
                        rx.hstack(
                            rx.text(
                                msg.time_str,
                                size="1",
                                color="rgba(255, 255, 255, 0.75)",
                                style={"font_size": "9px"},
                            ),
                            rx.icon("check-check", size=11, color="rgba(255, 255, 255, 0.85)"),
                            spacing="1",
                            justify="end",
                            align="center",
                            width="100%",
                            margin_top="1px",
                        ),
                        style={
                            "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                            "padding": "8px 11px",
                            "border_radius": "14px 14px 4px 14px",
                            "box_shadow": "0 2px 8px rgba(255, 107, 107, 0.22)",
                        },
                    ),
                    spacing="1",
                    align="end",
                    max_width="84%",
                ),
                justify="end",
                width="100%",
            ),
        ),
        width="100%",
    )


def render_thinking_indicator() -> rx.Component:
    """Renders a compact typing indicator bubble on the left."""
    return rx.hstack(
        rx.box(
            rx.icon("sparkles", size=13, color="white"),
            style={
                "width": "24px",
                "height": "24px",
                "min_width": "24px",
                "border_radius": "50%",
                "background": "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "margin_top": "2px",
            },
        ),
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        style={
                            "width": "5px",
                            "height": "5px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "5px",
                            "height": "5px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both 0.2s",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "5px",
                            "height": "5px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both 0.4s",
                        }
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.text("AI is typing...", size="1", color="var(--gray-10)", style={"font_size": "11px"}),
                spacing="2",
                align="center",
            ),
            style={
                "background": "var(--gray-3)",
                "border": "1px solid var(--gray-5)",
                "padding": "7px 11px",
                "border_radius": "14px 14px 14px 4px",
            },
        ),
        spacing="2",
        align="start",
        justify="start",
        width="100%",
    )


def chat_app_bar() -> rx.Component:
    """Compact chat header bar with avatar, online status, clear button, and close button."""
    return rx.flex(
        rx.hstack(
            # Contact Profile (Avatar with online dot + Name + Status)
            rx.hstack(
                rx.box(
                    rx.box(
                        rx.icon("bot", size=15, color="white"),
                        style={
                            "width": "28px",
                            "height": "28px",
                            "border_radius": "50%",
                            "background": "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)",
                            "display": "flex",
                            "align_items": "center",
                            "justify_content": "center",
                        },
                    ),
                    rx.box(
                        style={
                            "position": "absolute",
                            "bottom": "0",
                            "right": "0",
                            "width": "8px",
                            "height": "8px",
                            "border_radius": "50%",
                            "background": rx.cond(ChatState.is_thinking, "var(--purple-9)", "#10B981"),
                            "border": "1.5px solid var(--gray-2)",
                        }
                    ),
                    position="relative",
                    display="inline-flex",
                ),
                rx.vstack(
                    rx.text("Kcal AI", size="2", weight="bold", color="var(--gray-12)"),
                    rx.cond(
                        ChatState.is_thinking,
                        rx.text("typing...", size="1", color="var(--purple-9)", weight="medium", style={"font_size": "10px"}),
                        rx.text("online", size="1", color="var(--gray-10)", style={"font_size": "10px"}),
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="2",
                align="center",
            ),
            spacing="2",
            align="center",
        ),
        # Right action icons: Clear chat + Close
        rx.hstack(
            rx.icon_button(
                rx.icon("trash-2", size=14),
                variant="ghost",
                color_scheme="gray",
                size="1",
                on_click=ChatState.clear_chat,
                title="Clear Chat",
                style={"cursor": "pointer", "border_radius": "50%"},
            ),
            rx.icon_button(
                rx.icon("x", size=15),
                variant="ghost",
                color_scheme="gray",
                size="1",
                on_click=UIState.close_chat,
                title="Close",
                style={"cursor": "pointer", "border_radius": "50%"},
            ),
            spacing="1",
            align="center",
        ),
        justify="between",
        align="center",
        width="100%",
        padding="8px 12px",
        background="var(--gray-3)",
        border_bottom="1px solid var(--gray-4)",
        flex_shrink="0",
    )


def chat_messages_stream() -> rx.Component:
    """Compact scrollable chat messages feed."""
    return rx.box(
        rx.vstack(
            rx.foreach(ChatState.history, render_chat_message),
            rx.cond(
                ChatState.is_thinking,
                render_thinking_indicator(),
            ),
            spacing="2",
            width="100%",
        ),
        flex="1",
        overflow_y="auto",
        padding="10px 12px",
        background="var(--gray-1)",
        width="100%",
    )


def chat_composer() -> rx.Component:
    """Compact chat input composer pinned at bottom."""
    return rx.box(
        rx.form(
            rx.hstack(
                rx.input(
                    placeholder=rx.cond(
                        ChatState.is_thinking,
                        "AI is thinking...",
                        "Message Kcal AI...",
                    ),
                    value=ChatState.chat_input,
                    on_change=ChatState.set_chat_input,
                    disabled=ChatState.is_thinking,
                    size="2",
                    style={
                        "border_radius": "18px",
                        "background": "var(--gray-3)",
                        "border": "1px solid var(--gray-5)",
                        "padding_left": "12px",
                        "padding_right": "12px",
                        "width": "100%",
                        "height": "36px",
                        "font_size": "13px",
                        "color": "var(--gray-12)",
                    },
                ),
                rx.button(
                    rx.cond(
                        ChatState.is_thinking,
                        rx.spinner(size="1", color="white"),
                        rx.icon("arrow-up", size=15, color="white"),
                    ),
                    type="submit",
                    disabled=ChatState.is_thinking,
                    style={
                        "width": "34px",
                        "height": "34px",
                        "min_width": "34px",
                        "border_radius": "50%",
                        "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "cursor": "pointer",
                        "border": "none",
                        "box_shadow": "0 2px 6px rgba(255, 107, 107, 0.3)",
                        "transition": "all 0.15s ease",
                        "&:active": {
                            "transform": "scale(0.92)",
                        },
                    },
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            on_submit=ChatState.handle_submit,
            width="100%",
        ),
        padding="8px 10px",
        background="var(--gray-2)",
        border_top="1px solid var(--gray-4)",
        width="100%",
        flex_shrink="0",
    )


def chat_body() -> rx.Component:
    """Chat container content for chat interface."""
    return rx.flex(
        chat_messages_stream(),
        chat_composer(),
        direction="column",
        flex="1",
        width="100%",
        overflow="hidden",
    )


def chat_dialog() -> rx.Component:
    """Compact docked chat window anchored cleanly in the bottom-right corner."""
    return rx.cond(
        UIState.is_chat_open,
        rx.box(
            chat_app_bar(),
            chat_messages_stream(),
            chat_composer(),
            style={
                "position": "fixed",
                "bottom": rx.breakpoints(initial="16px", sm="20px"),
                "right": rx.breakpoints(initial="16px", sm="20px"),
                "z_index": "1000",
                "width": rx.breakpoints(initial="calc(100vw - 32px)", sm="350px", md="360px"),
                "max_width": "360px",
                "height": rx.breakpoints(initial="440px", sm="460px"),
                "max_height": "calc(100vh - 80px)",
                "background": "var(--gray-2)",
                "border": "1px solid var(--gray-5)",
                "border_radius": "18px",
                "box_shadow": "0 12px 36px rgba(0, 0, 0, 0.5), 0 2px 8px rgba(0, 0, 0, 0.25)",
                "display": "flex",
                "flex_direction": "column",
                "overflow": "hidden",
            },
        ),
    )


def chat_fab() -> rx.Component:
    """Floating Action Button in the lower-right corner to open AI Agent Chat."""
    return rx.cond(
        ~UIState.is_chat_open,
        rx.box(
            rx.button(
                rx.hstack(
                    rx.icon("bot", size=22, color="white"),
                    rx.cond(
                        ChatState.is_thinking,
                        rx.spinner(size="1", color="white"),
                    ),
                    align="center",
                    spacing="1",
                ),
                on_click=UIState.open_chat,
                style={
                    "width": "50px",
                    "height": "50px",
                    "border_radius": "50%",
                    "background": "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)",
                    "box_shadow": "0 4px 18px rgba(139, 92, 246, 0.45)",
                    "cursor": "pointer",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "transition": "all 0.2s ease",
                    "border": "none",
                    "&:hover": {
                        "transform": "scale(1.06)",
                        "box_shadow": "0 6px 24px rgba(139, 92, 246, 0.6)",
                    },
                    "&:active": {
                        "transform": "scale(0.95)",
                    },
                },
            ),
            style={
                "position": "fixed",
                "bottom": rx.breakpoints(initial="16px", sm="20px"),
                "right": rx.breakpoints(initial="16px", sm="20px"),
                "z_index": "999",
            },
        ),
    )


def chat_section() -> rx.Component:
    """Embedded chat section card (compatibility helper)."""
    return rx.card(
        rx.flex(
            chat_app_bar(),
            chat_messages_stream(),
            chat_composer(),
            direction="column",
            height="460px",
            overflow="hidden",
            width="100%",
        ),
        size="1",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "18px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
            "padding": "0px",
            "overflow": "hidden",
        },
        width="100%",
    )
