import reflex as rx
from dataclasses import dataclass

users = {
    "szombati.balint@gmail.com" : "balint",
    "ughybeus@gmail.com" : "bea",
    "bajkolara50@gmail.com": "lily"
}

def is_valid_email(email: str):
    return email in users.keys()

@dataclass 
class Profile:
    email: str = ""
    name: str = ""

class ProfileState(rx.State):
    profile: Profile = Profile()

    def on_login(self, profile: Profile):
        self.profile = profile

    def get_id(self):
        return users[self.profile.email]
        