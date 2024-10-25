import os

from models import User


def is_admin(user: User) -> bool:
    return user.email.lower() == os.getenv("ADMIN_EMAIL", "kukubaorch@gmail.com").lower()


def is_password_encrypted(password: str | None) -> bool:
    return password is not None and password != ""
