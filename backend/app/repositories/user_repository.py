from typing import Optional
from uuid import uuid4


class UserRepository:
    def __init__(self):
        self.users = {}

    def create_user(self, user_data: dict) -> dict:
        email = user_data["email"].lower()

        if email in self.users:
            raise ValueError("Email already registered")

        user = {
            "id": str(uuid4()),
            **user_data,
            "email": email
        }

        self.users[email] = user

        return user

    def get_user_by_email(self, email: str) -> Optional[dict]:
        return self.users.get(email.lower())

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        for user in self.users.values():
            if user["id"] == user_id:
                return user

        return None