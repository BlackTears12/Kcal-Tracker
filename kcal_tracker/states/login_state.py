import json
import reflex as rx
from reflex_google_auth import GoogleAuthState
from reflex_google_auth.state import get_token
import kcal_tracker.models.services as services


class Login(GoogleAuthState):
    valid_login: bool = False
    # Email of the authorized user, backend only so the client can't set it
    _user_id: str = ""

    @rx.var
    def user_name(self) -> str:
        """Fetch the user's name if authenticated."""
        if self.token_is_valid:
            # self.tokeninfo contains profile fields: name, email, picture, sub, etc.
            return self.tokeninfo.get("name", "User")
        return ""

    @rx.var
    def user_mail(self) -> str:
        """Fetch the user's mail if authenticated."""
        if self.token_is_valid:
            return self.tokeninfo.get("email", "")
        return ""

    @rx.var
    def user_picture(self) -> str:
        """Fetch user's Google avatar."""
        if self.token_is_valid:
            return self.tokeninfo.get("picture", "")
        return ""

    @rx.var
    def is_valid_login(self) -> bool:
        return self.token_is_valid and self.valid_login

    async def on_login(self):
        """Called upon page load or login, authorizes the user and loads their data."""
        if not self.token_is_valid:
            self.valid_login = False
            self._user_id = ""
            return
        profile = services.find_profile(str(self.user_mail))
        self.valid_login = profile is not None
        self._user_id = profile.email if profile else ""
        if not profile:
            return rx.window_alert("This mail is not authorized, if you believe this is a mistake, please contact me :)")
        # Imported here because these states import this module for current_user_id
        from kcal_tracker.states.nutrition_state import NutritionState
        from kcal_tracker.states.recipes_state import RecipesState
        return [NutritionState.view_today, RecipesState.load]

    @rx.event
    async def on_success(self, response: dict):
        """Called by Google Sign-In on successful login."""
        if "credential" in response:
            self.token_response_json = json.dumps({"id_token": response["credential"]})
            self.refresh_token = ""
        elif "code" in response:
            token_response = await get_token(response["code"])
            self.token_response_json = json.dumps(token_response)
            if "refresh_token" in token_response:
                self.refresh_token = token_response["refresh_token"]
        return Login.on_login


async def current_user_id(state: rx.State) -> str | None:
    """Returns the authorized user's id for this session, or None if it isn't logged in.

    Every event handler touching user data must check this, hiding the UI is not enough.
    """
    login = await state.get_state(Login)
    if not (login.valid_login and login._user_id and login.token_is_valid):
        return None
    # The token may have been swapped for another account since on_login ran
    if str(login.user_mail).strip().lower() != login._user_id:
        return None
    return login._user_id
