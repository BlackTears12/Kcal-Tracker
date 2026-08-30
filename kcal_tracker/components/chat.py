import reflex as rx
from kcal_tracker.states import (
    ChatMessage,
    ChatState,
    UIState,
)


def render_chat_message(msg: ChatMessage) -> rx.Component:
    """Renders a chat message bubble in modern mobile chat app styling."""
    return rx.flex(
        rx.cond(
            msg.is_ai,
            # AI Message (Left Aligned)
            rx.hstack(
                rx.box(
                    rx.icon("sparkles", size=14, color="white"),
                    style={
                        "width": "28px",
                        "height": "28px",
                        "min_width": "28px",
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
                                    "font_size": "14px",
                                    "line_height": "1.5",
                                    "color": "var(--gray-12)",
                                    "& p": {"margin_bottom": "6px", "&:last-child": {"margin_bottom": "0px"}},
                                    "& ul": {"padding_left": "18px", "margin_bottom": "6px"},
                                    "& ol": {"padding_left": "18px", "margin_bottom": "6px"},
                                    "& li": {"margin_bottom": "2px"},
                                },
                            ),
                            spacing="1",
                        ),
                        style={
                            "background": "var(--gray-3)",
                            "border": "1px solid var(--gray-5)",
                            "padding": "10px 14px",
                            "border_radius": "18px 18px 18px 4px",
                            "box_shadow": "0 2px 6px rgba(0, 0, 0, 0.15)",
                        },
                    ),
                    rx.text(
                        msg.time_str,
                        size="1",
                        color="var(--gray-9)",
                        style={"font_size": "10px", "padding_left": "4px"},
                    ),
                    spacing="1",
                    align="start",
                    max_width="85%",
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
                            style={"white_space": "pre-wrap", "word_break": "break-word"},
                        ),
                        rx.hstack(
                            rx.text(
                                msg.time_str,
                                size="1",
                                color="rgba(255, 255, 255, 0.75)",
                                style={"font_size": "10px"},
                            ),
                            rx.icon("check-check", size=12, color="rgba(255, 255, 255, 0.85)"),
                            spacing="1",
                            justify="end",
                            align="center",
                            width="100%",
                            margin_top="2px",
                        ),
                        style={
                            "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                            "padding": "10px 14px",
                            "border_radius": "18px 18px 4px 18px",
                            "box_shadow": "0 3px 12px rgba(255, 107, 107, 0.28)",
                        },
                    ),
                    spacing="1",
                    align="end",
                    max_width="82%",
                ),
                justify="end",
                width="100%",
            ),
        ),
        width="100%",
    )


def render_thinking_indicator() -> rx.Component:
    """Renders a sleek typing/thinking indicator bubble on the left."""
    return rx.hstack(
        rx.box(
            rx.icon("sparkles", size=14, color="white"),
            style={
                "width": "28px",
                "height": "28px",
                "min_width": "28px",
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
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both 0.2s",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.2s infinite ease-in-out both 0.4s",
                        }
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.text("AI is typing...", size="1", color="var(--gray-10)", weight="medium"),
                spacing="2",
                align="center",
            ),
            style={
                "background": "var(--gray-3)",
                "border": "1px solid var(--gray-5)",
                "padding": "10px 14px",
                "border_radius": "18px 18px 18px 4px",
            },
        ),
        spacing="2",
        align="start",
        justify="start",
        width="100%",
    )


def chat_app_bar() -> rx.Component:
    """Mobile chat app header bar with back button, avatar, online status, and action buttons."""
    return rx.flex(
        rx.hstack(
            # Back / Close Button (standard mobile chat interaction)
            rx.icon_button(
                rx.icon("chevron-left", size=22),
                variant="ghost",
                color_scheme="gray",
                size="2",
                on_click=UIState.close_chat,
                style={"cursor": "pointer", "border_radius": "50%"},
            ),
            # Contact Profile (Avatar with online dot + Name + Status)
            rx.hstack(
                rx.box(
                    rx.box(
                        rx.icon("bot", size=18, color="white"),
                        style={
                            "width": "36px",
                            "height": "36px",
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
                            "width": "10px",
                            "height": "10px",
                            "border_radius": "50%",
                            "background": rx.cond(ChatState.is_thinking, "var(--purple-9)", "#10B981"),
                            "border": "2px solid var(--gray-2)",
                        }
                    ),
                    position="relative",
                    display="inline-flex",
                ),
                rx.vstack(
                    rx.text("Kcal AI", size="2", weight="bold", color="var(--gray-12)"),
                    rx.cond(
                        ChatState.is_thinking,
                        rx.text("typing...", size="1", color="var(--purple-9)", weight="medium"),
                        rx.text("online", size="1", color="var(--gray-10)"),
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
                rx.icon("trash-2", size=16),
                variant="ghost",
                color_scheme="gray",
                size="2",
                on_click=ChatState.clear_chat,
                title="Clear Chat",
                style={"cursor": "pointer", "border_radius": "50%"},
            ),
            rx.dialog.close(
                rx.icon_button(
                    rx.icon("x", size=18),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                    on_click=UIState.close_chat,
                    style={"cursor": "pointer", "border_radius": "50%"},
                ),
            ),
            spacing="1",
            align="center",
        ),
        justify="between",
        align="center",
        width="100%",
        padding="10px 14px",
        background="var(--gray-2)",
        border_bottom="1px solid var(--gray-4)",
        flex_shrink="0",
    )


def chat_messages_stream() -> rx.Component:
    """Scrollable chat messages feed."""
    return rx.box(
        rx.vstack(
            rx.foreach(ChatState.history, render_chat_message),
            rx.cond(
                ChatState.is_thinking,
                render_thinking_indicator(),
            ),
            spacing="3",
            width="100%",
        ),
        flex="1",
        overflow_y="auto",
        padding="14px",
        background="var(--gray-1)",
        width="100%",
    )


def chat_composer() -> rx.Component:
    """Mobile chat composer input bar pinned at bottom."""
    return rx.box(
        rx.form(
            rx.hstack(
                rx.input(
                    placeholder=rx.cond(
                        ChatState.is_thinking,
                        "AI is responding...",
                        "Message Kcal AI...",
                    ),
                    value=ChatState.chat_input,
                    on_change=ChatState.set_chat_input,
                    disabled=ChatState.is_thinking,
                    size="3",
                    style={
                        "border_radius": "24px",
                        "background": "var(--gray-3)",
                        "border": "1px solid var(--gray-5)",
                        "padding_left": "16px",
                        "padding_right": "16px",
                        "width": "100%",
                        "height": "42px",
                        "font_size": "14px",
                        "color": "var(--gray-12)",
                    },
                ),
                rx.button(
                    rx.cond(
                        ChatState.is_thinking,
                        rx.spinner(size="1", color="white"),
                        rx.icon("arrow-up", size=18, color="white"),
                    ),
                    type="submit",
                    disabled=ChatState.is_thinking,
                    style={
                        "width": "42px",
                        "height": "42px",
                        "min_width": "42px",
                        "border_radius": "50%",
                        "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "cursor": "pointer",
                        "border": "none",
                        "box_shadow": "0 2px 8px rgba(255, 107, 107, 0.35)",
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
        padding="10px 14px",
        background="var(--gray-2)",
        border_top="1px solid var(--gray-4)",
        width="100%",
        flex_shrink="0",
    )


def chat_body() -> rx.Component:
    """Chat container content for mobile chat app interface."""
    return rx.flex(
        chat_messages_stream(),
        chat_composer(),
        direction="column",
        flex="1",
        width="100%",
        overflow="hidden",
    )


def chat_dialog() -> rx.Component:
    """Full mobile-styled chat interface dialog modal."""
    return rx.dialog.root(
        rx.dialog.content(
            chat_app_bar(),
            chat_messages_stream(),
            chat_composer(),
            style={
                "max_width": rx.breakpoints(initial="100vw", sm="480px"),
                "width": rx.breakpoints(initial="100vw", sm="95vw"),
                "height": rx.breakpoints(initial="100dvh", sm="680px"),
                "max_height": rx.breakpoints(initial="100dvh", sm="90vh"),
                "background": "var(--gray-2)",
                "border": rx.breakpoints(initial="none", sm="1px solid var(--gray-4)"),
                "border_radius": rx.breakpoints(initial="0px", sm="24px"),
                "box_shadow": "0 20px 60px rgba(0, 0, 0, 0.6)",
                "padding": "0px",
                "margin": "0px auto",
                "display": "flex",
                "flex_direction": "column",
                "overflow": "hidden",
            },
        ),
        open=UIState.is_chat_open,
        on_open_change=UIState.set_chat_open,
    )


def chat_fab() -> rx.Component:
    """Floating Action Button in the lower-right corner to open AI Agent Chat."""
    return rx.box(
        rx.button(
            rx.hstack(
                rx.icon("bot", size=26, color="white"),
                rx.cond(
                    ChatState.is_thinking,
                    rx.spinner(size="1", color="white"),
                ),
                align="center",
                spacing="2",
            ),
            on_click=UIState.open_chat,
            style={
                "width": "60px",
                "height": "60px",
                "border_radius": "50%",
                "background": "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)",
                "box_shadow": "0 6px 24px rgba(139, 92, 246, 0.45)",
                "cursor": "pointer",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "transition": "all 0.25s ease",
                "border": "none",
                "&:hover": {
                    "transform": "scale(1.08)",
                    "box_shadow": "0 8px 30px rgba(139, 92, 246, 0.6)",
                },
                "&:active": {
                    "transform": "scale(0.95)",
                },
            },
        ),
        style={
            "position": "fixed",
            "bottom": "24px",
            "right": "24px",
            "z_index": "999",
        },
    )


def chat_section() -> rx.Component:
    """Embedded chat section card (compatibility helper)."""
    return rx.card(
        rx.flex(
            chat_app_bar(),
            chat_messages_stream(),
            chat_composer(),
            direction="column",
            height="560px",
            overflow="hidden",
            width="100%",
        ),
        size="1",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "20px",
            "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.25)",
            "padding": "0px",
            "overflow": "hidden",
        },
        width="100%",
    )
