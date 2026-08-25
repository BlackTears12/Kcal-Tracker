import json
import reflex as rx
from reflex_google_auth import GoogleAuthState
from reflex_google_auth.state import get_token
from kcal_tracker import state_accessor
from kcal_tracker.states.nutrition_state import NutritionState
from kcal_tracker.states.recipes_state import RecipesState


# 1. Inherit from GoogleAuthState to track user login status
class User(GoogleAuthState):
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

    async def on_login(self):
        """Called upon page load or login to initialize the session state accessor."""
        state_accessor.init(self)
        if not self.token_is_valid: 
            return
        nutrition_state = await self.get_state(NutritionState)
        nutrition_state.on_login(self.get_id())
        recipes_state = await self.get_state(RecipesState)
        recipes_state.on_login(self.get_id())

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
        return User.on_login

    def get_id(self):
        if self.token_is_valid:
            return "bea" if self.tokeninfo.get("email", "") == "ughybeus@gmail.com" else "balint"
        return "shared"