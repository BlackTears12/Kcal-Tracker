import reflex as rx
from reflex_google_auth import GoogleAuthState
from kcal_tracker import state_accessor


# 1. Inherit from GoogleAuthState to track user login status
class UserState(GoogleAuthState):
    @rx.var
    def user_name(self) -> str:
        """Fetch the user's name if authenticated."""
        if self.token_is_valid:
            # self.tokeninfo contains profile fields: name, email, picture, sub, etc.
            return self.tokeninfo.get("name", "User")
        return ""

    @rx.var
    def user_picture(self) -> str:
        """Fetch user's Google avatar."""
        if self.token_is_valid:
            return self.tokeninfo.get("picture", "")
        return ""

    def on_login(self):
        """Called upon page load or login to initialize the session state accessor."""
        state_accessor.init(self)