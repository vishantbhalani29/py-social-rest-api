from datetime import datetime, timedelta

import jwt

from nexify.domain.user.models import User


class UserAccessToken:
    """
    A class representing a user access token.

    Attributes:
        exp (int): The expiration time of the access token in minutes.
        key (str): The key used for encoding the access token.

    Methods:
        generate_token(user: User) -> str: Generates an access token for the given user.

    """

    def __init__(self, exp, key) -> None:
        self.exp = exp
        self.key = key

    def generate_token(self, user: User) -> str:
        """
        Generates an access token for the given user.

        Parameters:
            user (User): The user object for which the access token is generated.

        Returns:
            str: The generated access token.

        Raises:
            Exception: If there is an error during token generation.

        """

        try:
            expiration_time = datetime.utcnow() + timedelta(minutes=self.exp)
            token_data = dict(
                id=str(user.id),
                email=user.email,
                username=user.username,
                exp=expiration_time,
            )
            access_token = jwt.encode(payload=token_data, key=self.key)
            return access_token
        except Exception as e:
            raise e

    def verify_token(self, encoded_token: str) -> dict:
        """
        Verifies the given access token and returns the decoded token data.

        Parameters:
            encoded_token (str): The encoded access token to be verified.

        Returns:
            dict: The decoded token data.

        Raises:
            Exception: If there is an error during token verification.

        """
        try:
            decoded_token_data = jwt.decode(
                jwt=encoded_token, key=self.key, algorithms=["HS256"], verify_exp=True
            )
            return decoded_token_data
        except Exception as e:
            raise e
