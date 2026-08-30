import json
import reflex as rx
from reflex_google_auth import GoogleAuthState
from reflex_google_auth.state import get_token
from kcal_tracker import state_accessor
from kcal_tracker.states.nutrition_state import NutritionState
from kcal_tracker.states.recipes_state import RecipesState
from kcal_tracker.states.profile_state import *
import kcal_tracker.models.agent as agent

# 1. Inherit from GoogleAuthState to track user login status
class Login(GoogleAuthState):
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
            # self.tokeninfo contains profile fields: name, email, picture, sub, etc.
            return self.tokeninfo.get("email", "user@mail.com")
        return ""

    @rx.var
    def user_picture(self) -> str:
        """Fetch user's Google avatar."""
        if self.token_is_valid:
            return self.tokeninfo.get("picture", "")
        return ""

    async def on_login(self):
        """Called upon page load or login to initialize the session state accessor."""
        if not self.token_is_valid:
            return
        if not is_valid_email(self.user_mail):
            return rx.window_alert("This mail not authorized, if you believe this is a mistake, please contact me:)")
        state_accessor.init(self)
        agent.init_agent()
        profile_state = await self.get_state(ProfileState)
        profile_state.on_login(Profile(email=self.user_mail,name=self.user_name))

        nutrition_state = await self.get_state(NutritionState)
        nutrition_state.on_login(profile_state.get_id())
        recipes_state = await self.get_state(RecipesState)
        recipes_state.on_login(profile_state.get_id())

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