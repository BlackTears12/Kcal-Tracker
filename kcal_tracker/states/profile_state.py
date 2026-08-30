import reflex as rx
from dataclasses import dataclass
import unidecode

@dataclass 
class Profile:
    email: str = ""
    name: str = ""

class ProfileState(rx.State):
    profile: Profile = Profile()

    def on_login(self, profile: Profile):
        self.profile = profile

    @rx.var
    def name(self) -> str:
        return self.profile.name

    def get_id(self):
        return unidecode.unidecode(self.profile.name, "utf-8").lower()
        