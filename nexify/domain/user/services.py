from typing import Type

from django.db.models.manager import BaseManager

from .models import User, UserFactory, UserFollow, UserFollowFactory


class UserServices:
    """
    A class that provides various services related to the User model.

    Methods:
    - get_user_factory(): Returns the UserFactory class, which is responsible for creating User instances.
    - get_user_repo(): Returns the User.objects manager, which provides access to the User model's database operations.
    - get_user_by_id(id: str) -> User: Retrieves a User instance from the database based on the provided id.
    - get_user_by_email(email: str) -> User: Retrieves a User instance from the database based on the provided email.

    Note:
    - This class assumes that the User model is defined in the 'user.models' module.
    - The UserFactory class is responsible for creating User instances with the provided parameters.
    - The User.objects manager provides access to the database operations for the User model.
    """

    @staticmethod
    def get_user_factory() -> Type[UserFactory]:
        """
        Returns the UserFactory class, which is responsible for creating User instances.

        Returns:
            Type[UserFactory]: The UserFactory class.

        """
        return UserFactory

    @staticmethod
    def get_user_repo() -> BaseManager[User]:
        """
        Returns the User.objects manager, which provides access to the User model's database operations.

        Returns:
            BaseManager[User]: The User.objects manager.

        """
        return User.objects

    def get_user_by_id(self, id: str) -> User:
        """
        Retrieves a User instance from the database based on the provided id.

        Parameters:
        - id (str): The id of the User instance to retrieve.

        Returns:
        - User: The User instance with the provided id.

        """
        return User.objects.get(id=id)

    def get_user_by_email(self, email: str) -> User:
        """
        Retrieves a User instance from the database based on the provided email.

        Parameters:
        - email (str): The email of the User instance to retrieve.

        Returns:
        - User: The User instance with the provided email.

        """
        return User.objects.get(email=email)


class UserFollowServices:
    """
    A class that provides services related to UserFollow entities.

    Attributes:
    - None

    Methods:
    - get_user_follow_factory() -> Type[UserFollowFactory]:
        Returns the UserFollowFactory class.

    - get_user_follow_repo() -> BaseManager[UserFollow]:
        Returns the BaseManager for the UserFollow model.

    - get_user_follow_by_id(id: str) -> UserFollow:
        Retrieves a UserFollow entity by its ID.

    """

    @staticmethod
    def get_user_follow_factory() -> Type[UserFollowFactory]:
        """
        Returns the UserFollowFactory class.

        Returns:
            Type[UserFollowFactory]: The UserFollowFactory class.
        """
        return UserFollowFactory

    @staticmethod
    def get_user_follow_repo() -> BaseManager[UserFollow]:
        """
        Returns the BaseManager for the UserFollow model.

        Returns:
            BaseManager[UserFollow]: The BaseManager for the UserFollow model.
        """
        return UserFollow.objects

    def get_user_follow_by_id(self, id: str) -> UserFollow:
        """
        Retrieves a UserFollow entity by its ID.

        Parameters:
        - id (str): The ID of the UserFollow entity to retrieve.

        Returns:
        - UserFollow: The UserFollow entity with the specified ID.
        """
        return UserFollow.objects.get(id=id)
