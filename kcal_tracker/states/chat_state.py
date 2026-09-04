import reflex as rx
from dataclasses import dataclass, field
from datetime import datetime
import kcal_tracker.models.agent as agent
import asyncio

import kcal_tracker.state_accessor as state_accessor
from kcal_tracker.states.nutrition_state import Meal, NutritionState

@dataclass
class ChatMessage:
    content: str = ""
    time: datetime = field(default_factory=datetime.now)
    time_str: str = ""
    is_ai: bool = False
    action: str = ""
    image_filename: str = ""

    def __post_init__(self):
        if not self.time_str and self.time:
            self.time_str = self.time.strftime("%I:%M %p").lstrip("0")

    def formatted_time(self) -> str:
        return self.time_str or self.time.strftime("%I:%M %p").lstrip("0")


def get_default_messages() -> list[ChatMessage]:
    return [
        ChatMessage(
            content="Hey there! 👋 I'm your Kcal AI Coach. Tell me what you ate (e.g. *'Log 2 eggs and toast for breakfast'*), upload a food photo, ask for recipe ideas, or check your remaining macros!",
            time=datetime.now(),
            time_str=datetime.now().strftime("%I:%M %p").lstrip("0"),
            is_ai=True,
            action="",
        )
    ]


class ChatState(rx.State):
    history: list[ChatMessage] = get_default_messages()
    chat_input: str = ""
    uploaded_image: str = ""
    uploaded_image_filename: str = ""
    is_uploading: bool = False
    is_thinking: bool = False

    # Computed vars
    @rx.var
    def message_count(self) -> int:
        return len(self.history)

    @rx.var
    def has_messages(self) -> bool:
        return len(self.history) > 0

    @rx.var
    def has_attached_image(self) -> bool:
        return bool(self.uploaded_image_filename)

    # Event handlers
    def set_chat_input(self, val: str):
        self.chat_input = val

    def set_thinking(self, val: bool):
        self.is_thinking = val

    def add_user_message(self, content: str, image_filename: str = ""):
        if not content.strip() and not image_filename:
            return
        now = datetime.now()
        user_msg = ChatMessage(
            content=content.strip(),
            time=now,
            time_str=now.strftime("%I:%M %p").lstrip("0"),
            is_ai=False,
            image_filename=image_filename,
        )
        self.history = self.history + [user_msg]

    def add_ai_message(self, content: str, action: str = ""):
        now = datetime.now()
        ai_msg = ChatMessage(
            content=content,
            time=now,
            time_str=now.strftime("%I:%M %p").lstrip("0"),
            is_ai=True,
            action=action,
        )
        self.history = self.history + [ai_msg]

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if isinstance(files, rx.UploadFile):
            file_list = [files]
        elif isinstance(files, list):
            file_list = files
        else:
            file_list = []

        if not file_list:
            return

        self.is_uploading = True
        yield

        try:
            file = file_list[0]
            upload_data = await file.read()
            clean_filename = str(file.filename).replace(" ", "_")
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{clean_filename}"
            outfile = rx.get_upload_dir() / unique_filename

            # Save the file to the app's upload directory
            with outfile.open("wb") as f:
                f.write(upload_data)

            # Store the filename to preview it in the UI and absolute path for the agent
            self.uploaded_image = str(outfile.absolute())
            self.uploaded_image_filename = unique_filename
        finally:
            self.is_uploading = False

    @rx.event
    def clear_uploaded_image(self):
        self.uploaded_image = ""
        self.uploaded_image_filename = ""

    async def handle_submit(self):
        if not self.chat_input.strip() and not self.uploaded_image:
            return
        user_text = self.chat_input.strip()
        img_path = self.uploaded_image
        img_filename = self.uploaded_image_filename

        self.chat_input = ""
        self.uploaded_image = ""
        self.uploaded_image_filename = ""

        display_text = user_text if user_text else "Attached a picture"
        self.add_user_message(display_text, image_filename=img_filename)
        self.is_thinking = True
        yield
        try:
            prompt_to_send = user_text if user_text else "Please analyze this food / meal picture, describe what you see, estimate its calories and macros, or log it."
            result = await asyncio.wait_for(agent.send_prompt(prompt_to_send, img_path), timeout=60.0)
            async with self:
                response = result
                if response:
                    self.add_ai_message(response)
        except asyncio.TimeoutError:
            async with self:
                response = "Request timed out. No response received within 1 minute."
                print(response)
        except Exception as e:
            async with self:
                response = f"An error occurred: {str(e)}"
                print(response)
        finally:
            # 3. Always reset is_thinking back to False
            async with self:
                self.is_thinking = False

    def send_quick_prompt(self, prompt_text: str):
        self.chat_input = prompt_text
        return ChatState.handle_submit

    def clear_chat(self):
        self.history = []
        self.chat_input = ""
        self.uploaded_image = ""
        self.uploaded_image_filename = ""
        self.is_thinking = False
        self.is_uploading = False
