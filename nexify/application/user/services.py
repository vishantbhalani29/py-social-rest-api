import datetime
from typing import Any, Dict, Tuple, Union

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.db.models.query import QuerySet
from github import Auth, Github
from rest_framework_simplejwt.tokens import RefreshToken

from nexify.domain.user.models import (
    User,
    UserBasePermissions,
    UserFollow,
    UserPersonalData,
)
from nexify.domain.user.services import UserFollowServices, UserServices
from nexify.infrastructure.emailer.services import MailerServices
from utils.data_manipulation.access_token import UserAccessToken
from utils.django.exceptions import (
    CannotFollowSelfException,
    UserAlreadyExistsException,
    UserFollowNotFoundException,
    UserNotFoundException,
)
from utils.global_methods.password_validator import is_valid_password


class UserAppServices:
    """
    The UserAppServices class provides methods for managing user-related operations.

    Methods:
    - list_users(): Retrieves a list of active users, ordered by creation date.
    - create_user_from_dict(data: Dict[str, Any]) -> User: Creates a new user based on the provided data dictionary.
    - get_user_data_with_token(user: User) -> Dict[str, Any]: Retrieves user data along with a JWT token for authentication.
    - update_user_from_dict(user_obj: User, data: Dict[str, Any]) -> User: Updates the user object with the provided data.
    - delete_user(user_obj: User) -> bool: Deletes the specified user.

    Note:
    - This class relies on the UserServices class for user-related operations.
    - The create_user_from_dict method performs validation to ensure that the email address is unique.
    - The get_user_data_with_token method generates a JWT token for authentication purposes.
    - The update_user_from_dict method updates the user object with the provided data, including email, first name, and last name.
    - The delete_user method deletes the specified user from the database.

    """

    def __init__(self) -> None:
        self.user_services = UserServices()
        self.mailer_services = MailerServices()

    def list_users(self) -> QuerySet[User]:
        """
        Retrieves a list of active users, ordered by creation date.

        Returns:
            QuerySet[User]: A queryset of active users, ordered by creation date.

        """
        return (
            self.user_services.get_user_repo()
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def create_user_from_dict(self, data: Dict[str, Any]) -> User:
        """
        Creates a new user based on the provided data dictionary.

        Parameters:
        - data (Dict[str, Any]): A dictionary containing the user data, including email, first name, last name, and password.

        Returns:
        - User: The newly created user object.

        Raises:
        - UserAlreadyExistsException: If a user with the same email address already exists.

        Note:
        - This method performs validation to ensure that the email address is unique.
        - The password is validated using the is_valid_password() method.
        - The user object is created using the UserPersonalData and UserBasePermissions classes.
        - The user object is saved to the database using the user factory method.

        """
        email = data.get("email", None)
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)
        password = data.get("password", None)

        user_exists = self.list_users().filter(email=email).first()
        if user_exists:
            raise UserAlreadyExistsException(
                item="user-already-exists-exception",
                message=f"The email address {user_exists.email} is already in use.",
            )

        is_valid_password(password=password)

        user_personal_data = UserPersonalData(
            email=email, username=email, first_name=first_name, last_name=last_name
        )
        user_base_permissions = UserBasePermissions(is_staff=False, is_active=True)

        try:
            with transaction.atomic():
                user_factory_method = self.user_services.get_user_factory()
                user_obj = user_factory_method.build_entity_with_id(
                    password=password,
                    personal_data=user_personal_data,
                    base_permissions=user_base_permissions,
                )
                user_obj.save()
                return user_obj
        except Exception as e:
            raise e

    def get_user_data_with_token(self, user: User) -> Dict[str, Any]:
        """
        Retrieves user data along with a JWT token for authentication.

        Parameters:
        - user (User): The user object for which to retrieve the data.

        Returns:
        - Dict[str, Any]: A dictionary containing the user data, including id, email, first name, last name, username, is_active, access token, and refresh token.

        Raises:
        - Exception: If an error occurs while retrieving the user data.

        Note:
        - This method generates a JWT token for authentication purposes using the RefreshToken.for_user() method.
        - The user data is retrieved from the user object and stored in a dictionary.
        - The last login timestamp is updated using the update_last_login() function.
        - The user data dictionary is returned.
        """
        try:
            with transaction.atomic():
                token = RefreshToken.for_user(user)
                data = dict(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    is_active=user.is_active,
                    access=str(token.access_token),
                    refresh=str(token),
                )
                update_last_login(None, user)
                return data
        except Exception as e:
            raise e

    def update_user_from_dict(self, user_obj: User, data: Dict[str, Any]) -> User:
        """
        Updates the user object with the provided data.

        Parameters:
        - user_obj (User): The user object to be updated.
        - data (Dict[str, Any]): A dictionary containing the data to update the user object with, including email, first name, and last name.

        Returns:
        - User: The updated user object.

        Raises:
        - UserAlreadyExistsException: If a user with the same email address already exists.

        Note:
        - This method updates the email, first name, and last name of the user object based on the provided data.
        - If the email address is changed, the username is also updated to match the new email address.
        - The user object is saved to the database using the save() method.
        - If a user with the same email address already exists, a UserAlreadyExistsException is raised.

        """
        email = data.get("email", None)
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)

        user_exists = self.list_users().filter(email=email).first()
        if user_exists:
            raise UserAlreadyExistsException(
                item="user-already-exists-exception",
                message=f"The email address {user_exists.email} is already in use.",
            )

        try:
            with transaction.atomic():
                if email:
                    user_obj.email = email
                    user_obj.username = email
                if first_name:
                    user_obj.first_name = first_name
                if last_name:
                    user_obj.last_name = last_name
                user_obj.save()
                return user_obj
        except Exception as e:
            raise e

    def delete_user(self, user_obj: User) -> bool:
        """
        Deletes the specified user from the database.

        Parameters:
        - user_obj (User): The user object to be deleted.

        Returns:
        - bool: True if the user is successfully deleted, False otherwise.

        Raises:
        - Exception: If an error occurs while deleting the user.

        Note:
        - This method uses the delete() method of the user object to delete it from the database.
        - The deletion is performed within a transaction to ensure data consistency.
        - If the deletion is successful, True is returned.
        - If an error occurs during the deletion process, an Exception is raised.
        """
        try:
            with transaction.atomic():
                user_obj.delete()
                return True
        except Exception as e:
            raise e

    def token_url_generator(self, user: User) -> str:
        """
        Generates a URL for the user's forgot password token.

        Parameters:
        - user (User): The user object for which to generate the token URL.

        Returns:
        - str: The URL for the user's forgot password token.

        Note:
        - This method creates a UserAccessToken object with the expiration time and secret key from the settings.
        - The generate_token() method of the UserAccessToken object is called to generate the token for the user.
        - The token is appended to the client host and forgot password route from the settings to create the URL.
        """
        user_access_token = UserAccessToken(
            exp=settings.FORGOT_PASSWORD_EXP_TIME, key=settings.FORGOT_PASSWORD_SECRETE
        )
        token = user_access_token.generate_token(user=user)
        return f"{settings.CLIENT_HOST}/{settings.FORGOT_PASSWORD_ROUTE}/{token}"

    def forgot_password(self, data: Dict[str, Any]):
        """
        Sends a forgot password email to the user with the provided email address.

        Parameters:
        - data (Dict[str, Any]): A dictionary containing the data for the forgot password request, including the user's email address.

        Raises:
        - UserNotFoundException: If no user is found with the provided email address.

        Note:
        - This method retrieves the user object with the provided email address using the list_users() method.
        - If a user is found, a token URL is generated using the token_url_generator() method.
        - The email is sent to the user's email address using the send_mail() method of the mailer_services object.
        - The email contains a reset link with the generated token URL.
        - If no user is found with the provided email address, a UserNotFoundException is raised.
        """
        email = data.get("email")
        try:
            user_exists = self.list_users().filter(email=email).first()
            if user_exists:
                token_url = self.token_url_generator(user=user_exists)
                template_data = dict(
                    subject=settings.FORGOT_PASSWORD_SUBJECT,
                    user_name=user_exists.username,
                    reset_link=token_url,
                    current_year=datetime.datetime.now().year,
                )
                self.mailer_services.send_mail(
                    email=user_exists.email,
                    subject=template_data.get("subject"),
                    template_data=template_data,
                    template_id=settings.FORGOT_PASSWORD_EMAIL_TEMPLATE,
                )
            else:
                raise UserNotFoundException(
                    item="user-not-found-exception",
                    message="No user found with the provided email.",
                )
        except Exception as e:
            raise e

    def reset_password(self, data: Dict[str, Any]) -> bool:
        """
        Resets the password for the user.

        Parameters:
        - data (Dict[str, Any]): A dictionary containing the data for the password reset request, including the token and the new password.

        Returns:
        - bool: True if the password is successfully reset, False otherwise.

        Raises:
        - Exception: If an error occurs while resetting the password.

        Note:
        - This method retrieves the token and the new password from the data dictionary.
        - The token is verified using the UserAccessToken.verify_token() method to get the user ID and email.
        - The user object is retrieved from the database using the user ID and email.
        - If the user object exists, the new password is validated using the is_valid_password() method.
        - The user's password is updated with the new password using the make_password() method.
        - The user object is saved to the database.
        - If the password reset is successful, True is returned.
        - If an error occurs during the password reset process, an Exception is raised.
        """
        token = data.get("token")
        new_password = data.get("new_password")
        try:
            with transaction.atomic():
                user_access_token = UserAccessToken(
                    exp=settings.FORGOT_PASSWORD_EXP_TIME,
                    key=settings.FORGOT_PASSWORD_SECRETE,
                )
                user_data = user_access_token.verify_token(encoded_token=token)
                user_id = user_data.get("id")
                user_email = user_data.get("email")
                user_obj = (
                    self.list_users().filter(id=user_id, email=user_email).first()
                )
                if user_obj:
                    is_valid_password(password=new_password)
                    user_obj.password = make_password(password=new_password)
                    user_obj.save()
                    return True
                else:
                    return False
        except Exception as e:
            raise e

    def create_user_from_github_auth(
        self, access_token: str
    ) -> Tuple[bool, Union[User, None]]:
        """
        Creates a new user based on the provided GitHub access token.

        Parameters:
        - access_token (str): The access token obtained from GitHub.

        Returns:
        - Tuple[bool, Union[User, None]]: A tuple containing a boolean value indicating whether the user was successfully created and either the newly created User object or None.

        Raises:
        - Exception: If an error occurs while creating the user.

        Note:
        - This method authenticates the user using the provided access token.
        - The GitHub API is used to retrieve the user information.
        - If the GitHub user has an email, the method checks if a user with the same email already exists in the database.
        - If a user with the same email exists, the method returns True and the existing user object.
        - If no user with the same email exists, a new User object is created with the email from GitHub and saved to the database.
        - If the GitHub user does not have an email, the method checks if a user with the same username already exists in the database.
        - If a user with the same username exists, the method returns True and the existing user object.
        - If no user with the same username exists, a new User object is created with the username from GitHub and a dummy email address (username@test.com) and saved to the database.
        - If neither an email nor a username is found in the GitHub user, the method returns False and None.
        - The creation of the user and the saving to the database are performed within a transaction to ensure data consistency.
        - If an error occurs during the user creation process, an Exception is raised.
        """

        # Authenticate by a token
        auth = Auth.Token(access_token)
        github_api = Github(auth=auth)

        try:
            github_user = github_api.get_user()

            with transaction.atomic():
                # TODO: Avoid generating random email addresses,
                # reject user creation without email or do mandatory email completion later.

                # Check if GitHub user has an email
                if github_user.email:
                    user_exists = (
                        self.list_users().filter(email=github_user.email).first()
                    )
                    if user_exists:
                        return True, user_exists

                    # Create a new user instance with email from GitHub
                    user_instance = User()
                    user_instance.username = github_user.email.split("@")[0].lower()
                    user_instance.email = github_user.email
                    user_instance.save()
                    return True, user_instance

                # Check if GitHub user has an username
                if github_user.login:
                    user_exists = (
                        self.list_users()
                        .filter(username=github_user.login.lower())
                        .first()
                    )
                    if user_exists:
                        return True, user_exists

                    # Create a new user instance with username from GitHub
                    user_instance = User()
                    user_instance.username = github_user.login.lower()
                    user_instance.email = f"{github_user.login.lower()}@test.com"
                    user_instance.save()
                    return True, user_instance

                # No email or username found in GitHub user
                return False, None
        except Exception as e:
            raise e


class UserFollowAppServices:
    """
    The UserFollowAppServices class provides methods for managing user follow-related operations.

    Methods:
    - follow_or_unfollow_user(user: User, following_user_id: str) -> Tuple[User, str]: Follows or unfollows a user based on the provided user and following user ID.
    - accept_follow_request_of_user(user: User, follower_user_id: str) -> UserFollow: Accepts a follow request from a follower user based on the provided user and follower user ID.
    - delete_follow_request_of_user(user: User, follower_user_id: str) -> bool: Deletes a follow request from a follower user based on the provided user and follower user ID.
    - follow_requests_list(user: User) -> QuerySet[UserFollow]: Retrieves a list of follow requests for the specified user.
    - user_followers(user: User) -> QuerySet[UserFollow]: Retrieves a list of followers for the specified user.
    - user_following(user: User) -> QuerySet[UserFollow]: Retrieves a list of users that the specified user is following.

    Note:
    - This class relies on the UserFollowServices and UserAppServices classes for user follow-related operations.
    - The follow_or_unfollow_user method follows or unfollows a user based on the provided user and following user ID.
    - The accept_follow_request_of_user method accepts a follow request from a follower user based on the provided user and follower user ID.
    - The delete_follow_request_of_user method deletes a follow request from a follower user based on the provided user and follower user ID.
    - The follow_requests_list method retrieves a list of follow requests for the specified user.
    - The user_followers method retrieves a list of followers for the specified user.
    - The user_following method retrieves a list of users that the specified user is following.
    """

    def __init__(self) -> None:
        self.user_follow_services = UserFollowServices()
        self.user_app_services = UserAppServices()

    def follow_or_unfollow_user(
        self, user: User, following_user_id: str
    ) -> Tuple[User, str]:
        """
        Follows or unfollows a user based on the provided user and following user ID.

        Parameters:
        - user (User): The user who wants to follow or unfollow another user.
        - following_user_id (str): The ID of the user that the user wants to follow or unfollow.

        Returns:
        Tuple[User, str]: A tuple containing the following user object and an action message.

        Raises:
        CannotFollowSelfException: If the user tries to follow themselves.
        UserNotFoundException: If the user to be followed or unfollowed is not found.

        Note:
        - If the user is already following the specified user, the method will unfollow them.
        - If the user is not following the specified user, the method will send a follow request.
        - If the follow request is already sent, the method will delete the follow request.
        - The action message will indicate the result of the operation.

        """

        if str(user.id) == following_user_id:
            raise CannotFollowSelfException(
                "cannot-follow-self-exception", "You cannot follow yourself."
            )

        following_user_obj = (
            self.user_app_services.list_users()
            .filter(id=following_user_id, is_active=True)
            .first()
        )

        if not following_user_obj:
            raise UserNotFoundException(
                item="user-not-found-exception", message="User not found."
            )

        exist_user_follow_obj = (
            self.user_follow_services.get_user_follow_repo()
            .filter(follower=str(user.id), following=str(following_user_obj.id))
            .first()
        )

        try:
            with transaction.atomic():
                if exist_user_follow_obj:
                    exist_user_follow_obj.delete()
                    action_message = (
                        "You have unfollowed."
                        if exist_user_follow_obj.is_accepted
                        else "Follow request deleted."
                    )
                else:
                    user_follow_factory_method = (
                        self.user_follow_services.get_user_follow_factory()
                    )
                    user_follow_obj = user_follow_factory_method.build_entity_with_id(
                        follower=user, following=following_user_obj
                    )
                    user_follow_obj.save()
                    action_message = "Follow request sent."

                return following_user_obj, action_message
        except Exception as e:
            raise e

    def accept_follow_request_of_user(
        self, user: User, follower_user_id: str
    ) -> UserFollow:
        """
        Accepts a follow request from a follower user based on the provided user and follower user ID.

        Parameters:
        - user (User): The user who wants to accept the follow request.
        - follower_user_id (str): The ID of the follower user whose follow request is to be accepted.

        Returns:
        UserFollow: The UserFollow object representing the accepted follow request.

        Raises:
        UserNotFoundException: If the follower user is not found.
        UserFollowNotFoundException: If the follow request is not found.

        Note:
        - This method is used to accept a follow request from a follower user.
        - The user parameter is the user who wants to accept the follow request.
        - The follower_user_id parameter is the ID of the follower user whose follow request is to be accepted.
        - If the follower user is not found, a UserNotFoundException is raised.
        - If the follow request is not found, a UserFollowNotFoundException is raised.
        - If the follow request is successfully accepted, the is_accepted attribute of the UserFollow object is set to True.
        - The UserFollow object representing the accepted follow request is returned.
        """
        follower_user_obj = (
            self.user_app_services.list_users()
            .filter(id=follower_user_id, is_active=True)
            .first()
        )
        if not follower_user_obj:
            raise UserNotFoundException(
                item="user-not-found-exception", message="User not found."
            )

        exist_user_follow_obj = (
            self.user_follow_services.get_user_follow_repo()
            .filter(
                follower=str(follower_user_obj.id),
                following=str(user.id),
                is_accepted=False,
            )
            .first()
        )
        if not exist_user_follow_obj:
            raise UserFollowNotFoundException(
                item="user-follow-not-found-exception",
                message="Follow request not found.",
            )

        try:
            with transaction.atomic():
                exist_user_follow_obj.is_accepted = True
                exist_user_follow_obj.save()

                return exist_user_follow_obj
        except Exception as e:
            raise e

    def delete_follow_request_of_user(self, user: User, follower_user_id: str) -> bool:
        """
        Deletes a follow request from a follower user based on the provided user and follower user ID.

        Parameters:
        - user (User): The user who wants to delete the follow request.
        - follower_user_id (str): The ID of the follower user whose follow request is to be deleted.

        Returns:
        bool: True if the follow request is successfully deleted.

        Raises:
        UserNotFoundException: If the follower user is not found.
        UserFollowNotFoundException: If the follow request is not found.

        Note:
        - This method is used to delete a follow request from a follower user.
        - The user parameter is the user who wants to delete the follow request.
        - The follower_user_id parameter is the ID of the follower user whose follow request is to be deleted.
        - If the follower user is not found, a UserNotFoundException is raised.
        - If the follow request is not found, a UserFollowNotFoundException is raised.
        - If the follow request is successfully deleted, True is returned.
        """
        follower_user_obj = (
            self.user_app_services.list_users()
            .filter(id=follower_user_id, is_active=True)
            .first()
        )
        if not follower_user_obj:
            raise UserNotFoundException(
                item="user-not-found-exception", message="User not found."
            )

        exist_user_follow_obj = (
            self.user_follow_services.get_user_follow_repo()
            .filter(
                follower=str(follower_user_obj.id),
                following=str(user.id),
                is_accepted=False,
            )
            .first()
        )
        if not exist_user_follow_obj:
            raise UserFollowNotFoundException(
                item="user-follow-not-found-exception",
                message="Follow request not found.",
            )

        try:
            with transaction.atomic():
                exist_user_follow_obj.delete()
                return True
        except Exception as e:
            raise e

    def follow_requests_list(self, user: User) -> QuerySet[UserFollow]:
        """
        Retrieves a list of follow requests for the specified user.

        Parameters:
        - user (User): The user for whom to retrieve the follow requests.

        Returns:
        QuerySet[UserFollow]: A queryset of follow requests for the specified user.

        Note:
        - This method retrieves a list of follow requests for the specified user.
        - The follow requests are filtered based on the user's ID and the is_accepted attribute.
        - The follow requests are ordered by the created_at attribute in descending order.
        - The returned queryset can be used to perform further operations on the follow requests.
        """
        return (
            self.user_follow_services.get_user_follow_repo()
            .filter(following=str(user.id), is_accepted=False)
            .order_by("-created_at")
        )

    def user_followers(self, user: User) -> QuerySet[UserFollow]:
        """
        Retrieves a list of followers for the specified user.

        Parameters:
        - user (User): The user for whom to retrieve the followers.

        Returns:
        QuerySet[UserFollow]: A queryset of followers for the specified user.

        Note:
        - This method retrieves a list of followers for the specified user.
        - The followers are filtered based on the user's ID and the is_accepted attribute.
        - The followers are ordered by the created_at attribute in descending order.
        - The returned queryset can be used to perform further operations on the followers.
        """
        return (
            self.user_follow_services.get_user_follow_repo()
            .filter(following=str(user.id), is_accepted=True)
            .order_by("-created_at")
        )

    def user_following(self, user: User) -> QuerySet[UserFollow]:
        """
        Retrieves a list of users that the specified user is following.

        Parameters:
        - user (User): The user for whom to retrieve the following users.

        Returns:
        QuerySet[UserFollow]: A queryset of users that the specified user is following.

        Note:
        - This method retrieves a list of users that the specified user is following.
        - The following users are filtered based on the user's ID and the is_accepted attribute.
        - The following users are ordered by the created_at attribute in descending order.
        - The returned queryset can be used to perform further operations on the following users.
        """
        return (
            self.user_follow_services.get_user_follow_repo()
            .filter(follower=str(user.id), is_accepted=True)
            .order_by("-created_at")
        )
