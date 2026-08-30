import reflex as rx


class UIState(rx.State):
    """Manages active content menubar tab, agent chat modal visibility, and top-level UI states."""
    active_tab: str = "meals"  # Options: "meals", "recipes", "all"
    is_chat_open: bool = False

    def set_active_tab(self, tab: str):
        self.active_tab = tab

    def toggle_chat(self):
        self.is_chat_open = not self.is_chat_open

    def open_chat(self):
        self.is_chat_open = True

    def close_chat(self):
        self.is_chat_open = False

    def set_chat_open(self, val: bool):
        self.is_chat_open = val

    @rx.var
    def is_meals_active(self) -> bool:
        return self.active_tab in ["meals", "all"]

    @rx.var
    def is_recipes_active(self) -> bool:
        return self.active_tab in ["recipes", "all"]

    @rx.var
    def is_all_active(self) -> bool:
        return self.active_tab == "all"
