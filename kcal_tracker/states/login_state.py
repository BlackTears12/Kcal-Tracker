import json
import reflex as rx
from reflex_google_auth import GoogleAuthState
from reflex_google_auth.state import get_token
import kcal_tracker.models.services as services
from kcal_tracker.data.profile import Profile


class Login(GoogleAuthState):
    """Google sign-in is only used once, to start a long-lived session kept in the browser."""
    valid_login: bool = False
    # Session token, the database only has its hash
    session_token: str = rx.LocalStorage(name="kcal_session")
    display_name: str = ""
    is_admin: bool = False
    # Admin only: the other users whose log can be switched to
    switchable_profiles: list[Profile] = []
    # Name of the user whose log an admin switched to, empty when working on their own
    acting_name: str = ""
    # Email of the authorized user, backend only so the client can't set it
    _user_id: str = ""
    # Email of the user whose log an admin switched to, backend only
    _acting_as: str = ""

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
        return self.valid_login

    @rx.var
    def is_acting_for_other(self) -> bool:
        return self.acting_name != ""

    async def on_login(self):
        """Called upon page load or login, restores the session and loads the user's data."""
        user_id = services.SessionService().validate(self.session_token)
        if user_id is None:
            self._clear_login()
            # Signed in with Google before sessions existed, or the session just expired
            if self.token_is_valid:
                return Login.start_session
            return
        profile = services.find_profile(user_id)
        self.valid_login = True
        self._user_id = user_id
        self.display_name = profile.name if profile and profile.name else user_id
        self.is_admin = services.is_admin(user_id)
        self.switchable_profiles = [p for p in services.load_profiles() if p.email != user_id] if self.is_admin else []
        # A page load always starts on the user's own log
        self._acting_as = ""
        self.acting_name = ""
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
        return Login.start_session

    async def start_session(self):
        """Exchanges a verified Google token of an allowed user for a session token."""
        if not self.token_is_valid:
            return
        profile = services.find_profile(str(self.user_mail))
        # The Google token is short lived and not needed once the session exists
        self.token_response_json = ""
        self.refresh_token = ""
        if profile is None:
            self._clear_login()
            return rx.window_alert("This mail is not authorized, if you believe this is a mistake, please contact me :)")
        self.session_token = services.SessionService().create(profile.email, self.router.headers.user_agent)
        return Login.on_login

    async def switch_profile(self, email: str):
        """Admin only: work on another user's log, or on their own with an empty email."""
        user_id = await current_user_id(self)
        if user_id is None or not services.is_admin(user_id):
            return
        if not email or email == user_id:
            self._acting_as, self.acting_name = "", ""
        else:
            profile = services.find_profile(email)
            if profile is None:
                return
            self._acting_as, self.acting_name = profile.email, profile.name or profile.email
        # Imported here because these states import this module for current_user_id
        from kcal_tracker.states.nutrition_state import NutritionState
        from kcal_tracker.states.chat_state import ChatState
        # The visible chat belongs to the previous log
        (await self.get_state(ChatState)).reset()
        return NutritionState.reload_view

    async def logout(self):
        services.SessionService().revoke(self.session_token)
        return await self._end_session()

    async def logout_everywhere(self):
        user_id = await current_user_id(self)
        if user_id is not None:
            services.SessionService().revoke_all(user_id)
        return await self._end_session()

    async def _end_session(self):
        self.token_response_json = ""
        self.refresh_token = ""
        self._clear_login()
        # Imported here because these states import this module for current_user_id
        from kcal_tracker.states.nutrition_state import NutritionState
        from kcal_tracker.states.recipes_state import RecipesState
        from kcal_tracker.states.chat_state import ChatState
        # Don't leave this user's data in the tab for whoever signs in next
        for state_cls in (NutritionState, RecipesState, ChatState):
            (await self.get_state(state_cls)).reset()

    def _clear_login(self):
        self.session_token = ""
        self.valid_login = False
        self.display_name = ""
        self._user_id = ""
        self.is_admin = False
        self.switchable_profiles = []
        self.acting_name = ""
        self._acting_as = ""


async def current_user_id(state: rx.State) -> str | None:
    """Returns the authorized user's id for this session, or None if it isn't logged in.

    Every event handler touching user data must check this, hiding the UI is not enough.
    The session is re-validated each time, so logging out elsewhere or removing the user
    from profiles_repo.csv takes effect immediately.
    """
    login = await state.get_state(Login)
    if not (login.valid_login and login._user_id):
        return None
    if services.SessionService().validate(login.session_token) != login._user_id:
        # Revoked or expired: show the login screen again
        login._clear_login()
        return None
    return login._user_id


async def acting_user_id(state: rx.State) -> str | None:
    """Returns whose data this session works on: the logged-in user, or the user an admin switched to.

    Use this for handlers touching meals, workouts and targets, and current_user_id for the
    session itself (e.g. logging out).
    """
    user_id = await current_user_id(state)
    if user_id is None:
        return None
    login = await state.get_state(Login)
    if not login._acting_as:
        return user_id
    if services.is_admin(user_id) and services.find_profile(login._acting_as) is not None:
        return login._acting_as
    # Admin rights or the other user were removed: refuse rather than silently write to the admin's own log
    login._acting_as, login.acting_name = "", ""
    return None
