import reflex as rx
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    content: str = ""
    time: datetime = field(default_factory=datetime.now)
    is_ai: bool = False
    action: str = ""

    def formatted_time(self) -> str:
        return self.time.strftime("%I:%M %p")


def get_default_messages() -> list[ChatMessage]:
    return [
        ChatMessage(
            content="👋 Welcome to your AI Nutrition Assistant! I can help you log meals, calculate macros, save recipes, and answer nutritional questions.\n\nTry saying: *'Log 2 eggs and toast for breakfast'* or *'Create a recipe for Protein Smoothie'*.",
            time=datetime.now(),
            is_ai=True,
            action="AI Ready",
        )
    ]


class ChatState(rx.State):
    history: list[ChatMessage] = get_default_messages()
    chat_input: str = ""
    is_thinking: bool = False

    # Computed vars
    @rx.var
    def message_count(self) -> int:
        return len(self.history)

    @rx.var
    def has_messages(self) -> bool:
        return len(self.history) > 0

    # Event handlers
    def set_chat_input(self, val: str):
        self.chat_input = val

    def set_thinking(self, val: bool):
        self.is_thinking = val

    def add_user_message(self, content: str):
        if not content.strip():
            return
        user_msg = ChatMessage(
            content=content.strip(),
            time=datetime.now(),
            is_ai=False,
        )
        self.history = self.history + [user_msg]

    def add_ai_message(self, content: str, action: str = ""):
        ai_msg = ChatMessage(
            content=content,
            time=datetime.now(),
            is_ai=True,
            action=action,
        )
        self.history = self.history + [ai_msg]

    def handle_submit(self):
        if not self.chat_input.strip():
            return
        user_text = self.chat_input.strip()
        self.chat_input = ""
        self.add_user_message(user_text)
        self.is_thinking = True
        # AI processing will be hooked up here (e.g. by NutritionAgent)

    def send_quick_prompt(self, prompt_text: str):
        self.chat_input = prompt_text
        self.handle_submit()

    def clear_chat(self):
        self.history = []
        self.chat_input = ""
        self.is_thinking = False
