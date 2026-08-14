import reflex as rx


class UIState(rx.State):
    """Manages active tab, mobile view layout, and top-level UI states."""
    active_tab: str = "dashboard"  # Options: "dashboard", "chat", "recipes", "all"

    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.var
    def is_dashboard_active(self) -> bool:
        return self.active_tab in ["dashboard", "all"]

    @rx.var
    def is_chat_active(self) -> bool:
        return self.active_tab in ["chat", "all"]

    @rx.var
    def is_recipes_active(self) -> bool:
        return self.active_tab in ["recipes", "all"]
