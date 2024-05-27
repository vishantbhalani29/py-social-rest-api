import re

from django.conf import settings

from utils.django.exceptions import InvalidPasswordException


def is_valid_password(password: str) -> None:
    """
    Check if a password is valid based on a regular expression pattern.

    Parameters:
        password (str): The password to be checked.

    Returns:
        bool: True if the password matches the regular expression pattern, False otherwise.
    """
    if not bool(re.match(settings.PASSWORD_REGEX, password)):
        raise InvalidPasswordException(
            item="invalid-password-exception",
            message="Password should have 8+ characters with at least one uppercase, one lowercase, one digit, and one special character (@$!%*?&).",
        )
