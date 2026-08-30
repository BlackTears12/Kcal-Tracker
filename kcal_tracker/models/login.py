import json
import reflex as rx
from reflex_google_auth import GoogleAuthState
from reflex_google_auth.state import get_token
from kcal_tracker import state_accessor
from kcal_tracker.states.nutrition_state import NutritionState
from kcal_tracker.states.recipes_state import RecipesState
from kcal_tracker.states.profile_state import *
import kcal_tracker.models.agent as agent
import kcal_tracker.models.data_repository as data_repository

# 1. Inherit from GoogleAuthState to track user login status
class Login(GoogleAuthState):
    valid_login: bool = False
    
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

    @rx.var
    def is_valid_login(self) -> bool:
        return self.token_is_valid and self.valid_login

    async def on_login(self):
        """Called upon page load or login to initialize the session state accessor."""
        if not self.token_is_valid:
            return
        profile = self.validate_login(str(self.user_mail))
        self.valid_login = profile is not None
        if not profile:
            return rx.window_alert("This mail is not authorized, if you believe this is a mistake, please contact me :)")
        state_accessor.init(self)
        agent.init_agent()
        profile_state = await self.get_state(ProfileState)
        profile_state.on_login(profile)
        nutrition_state = await self.get_state(NutritionState)
        nutrition_state.on_login(profile_state.get_id())
        recipes_state = await self.get_state(RecipesState)
        recipes_state.on_login(profile_state.get_id())

    def validate_login(self, email: str):
        profiles = data_repository.load_registered_profiles()
        for p in profiles:
            if p.email == email:
                return p
        return None

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