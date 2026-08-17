import reflex as rx
from kcal_tracker.states import (
    ChatMessage,
    ChatState,
)


def render_chat_message(msg: ChatMessage) -> rx.Component:
    """Renders a chat message bubble."""
    return rx.flex(
        rx.cond(
            msg.is_ai,
            # AI Message (Left Aligned)
            rx.flex(
                rx.avatar(
                    fallback="AI",
                    size="2",
                    color_scheme="purple",
                    variant="soft",
                    style={"border": "1px solid var(--purple-6)"},
                ),
                rx.vstack(
                    rx.box(
                        rx.vstack(
                            rx.cond(
                                msg.action != "",
                                rx.badge(
                                    msg.action,
                                    color_scheme="purple",
                                    variant="solid",
                                    size="1",
                                    radius="full",
                                ),
                            ),
                            rx.markdown(msg.content),
                            spacing="2",
                        ),
                        style={
                            "background": "var(--gray-3)",
                            "border": "1px solid var(--gray-5)",
                            "padding": "12px 16px",
                            "border_radius": "16px 16px 16px 4px",
                        },
                    ),
                    spacing="1",
                    align="start",
                    max_width="88%",
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
                        rx.text(msg.content, size="2", color="white"),
                        style={
                            "background": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
                            "padding": "10px 14px",
                            "border_radius": "16px 16px 4px 16px",
                            "box_shadow": "0 2px 8px rgba(255, 107, 107, 0.2)",
                        },
                    ),
                    spacing="1",
                    align="end",
                    max_width="85%",
                ),
                rx.avatar(fallback="U", size="2", color_scheme="orange", variant="solid"),
                spacing="2",
                align="start",
                justify="end",
                width="100%",
            ),
        ),
        width="100%",
    )


def render_thinking_indicator() -> rx.Component:
    """Renders an animated AI thinking / typing indicator bubble."""
    return rx.flex(
        rx.avatar(
            fallback="AI",
            size="2",
            color_scheme="purple",
            variant="soft",
            style={"border": "1px solid var(--purple-6)"},
        ),
        rx.box(
            rx.hstack(
                rx.spinner(size="1", color="var(--purple-9)"),
                rx.text("AI is thinking...", size="2", color="var(--gray-11)", weight="medium"),
                rx.hstack(
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.4s infinite ease-in-out both",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.4s infinite ease-in-out both 0.2s",
                        }
                    ),
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": "var(--purple-9)",
                            "animation": "pulse 1.4s infinite ease-in-out both 0.4s",
                        }
                    ),
                    spacing="1",
                    align="center",
                ),
                spacing="2",
                align="center",
            ),
            style={
                "background": "var(--gray-3)",
                "border": "1px solid var(--gray-5)",
                "padding": "10px 16px",
                "border_radius": "16px 16px 16px 4px",
            },
        ),
        spacing="2",
        align="start",
        justify="start",
        width="100%",
    )


def chat_section() -> rx.Component:
    """AI Assistant Chatbot Section."""
    quick_prompts = [
        ("🍳 Log 2 eggs and toast", "Log 2 eggs and whole wheat toast for breakfast (320 kcal, 18g protein)"),
        ("🍗 Log chicken & rice", "Log 200g grilled chicken breast and 150g rice for lunch"),
        ("📖 Create smoothie recipe", "Create a recipe for High-Protein Smoothie with 300ml milk, 1 banana, 40g whey"),
        ("📊 Remaining macros?", "How much protein and calories do I have left today?"),
    ]

    return rx.card(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.icon("bot", color="var(--purple-9)", size=22),
                    rx.vstack(
                        rx.heading("AI Nutrition Assistant", size="4", weight="bold"),
                        rx.hstack(
                            rx.box(
                                style={
                                    "width": "8px",
                                    "height": "8px",
                                    "border_radius": "50%",
                                    "background": rx.cond(ChatState.is_thinking, "var(--purple-9)", "#10B981"),
                                }
                            ),
                            rx.text(
                                rx.cond(ChatState.is_thinking, "Thinking...", "Online & Ready"),
                                size="1",
                                color_scheme=rx.cond(ChatState.is_thinking, "purple", "green"),
                            ),
                            spacing="1",
                            align="center",
                        ),
                        spacing="0",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.badge(
                    rx.cond(ChatState.is_thinking, "Processing...", "Natural Language"),
                    color_scheme="purple",
                    variant="soft",
                    radius="full",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(size="4"),

            # Quick Action Prompt Chips
            rx.flex(
                rx.text("Quick Actions:", size="1", weight="bold", color_scheme="gray"),
                rx.flex(
                    *[
                        rx.badge(
                            label,
                            color_scheme="gray",
                            variant="surface",
                            size="2",
                            on_click=lambda text=prompt: ChatState.send_quick_prompt(text),
                            style={
                                "cursor": "pointer",
                                "transition": "all 0.15s ease",
                                "&:hover": {
                                    "background": "var(--purple-4)",
                                    "color": "var(--purple-11)",
                                },
                            },
                        )
                        for label, prompt in quick_prompts
                    ],
                    wrap="wrap",
                    spacing="2",
                ),
                direction="column",
                spacing="2",
                width="100%",
                padding_y="1",
            ),

            # Chat Messages Scroll Area
            rx.box(
                rx.vstack(
                    rx.foreach(ChatState.history, render_chat_message),
                    rx.cond(
                        ChatState.is_thinking,
                        render_thinking_indicator(),
                    ),
                    spacing="3",
                    width="100%",
                ),
                style={
                    "max_height": "420px",
                    "min_height": "320px",
                    "overflow_y": "auto",
                    "padding": "12px",
                    "background": "var(--gray-1)",
                    "border_radius": "12px",
                    "border": "1px solid var(--gray-4)",
                },
                width="100%",
            ),

            # Chat Input Form
            rx.form(
                rx.hstack(
                    rx.input(
                        placeholder=rx.cond(
                            ChatState.is_thinking,
                            "AI is thinking...",
                            "Talk to AI... e.g. 'Log 150g salmon for dinner' or 'Create protein pancake recipe'",
                        ),
                        value=ChatState.chat_input,
                        on_change=ChatState.set_chat_input,
                        disabled=ChatState.is_thinking,
                        size="3",
                        width="100%",
                        style={"border_radius": "10px"},
                    ),
                    rx.button(
                        rx.icon("send", size=18),
                        "Send",
                        size="3",
                        color_scheme="purple",
                        type="submit",
                        loading=ChatState.is_thinking,
                        disabled=ChatState.is_thinking,
                        style={"cursor": "pointer", "border_radius": "10px"},
                    ),
                    spacing="2",
                    width="100%",
                    align="center",
                ),
                on_submit=ChatState.handle_submit,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        style={
            "background": "var(--gray-2)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
        },
        width="100%",
    )
