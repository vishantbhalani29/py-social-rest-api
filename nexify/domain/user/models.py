import uuid
from dataclasses import dataclass, field
from typing import Union

from dataclass_type_validator import dataclass_validate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import validate_email
from django.db import models

from utils.data_manipulation.type_conversion import asdict
from utils.django import custom_models


@dataclass(frozen=True)
class UserID:
    """
    A class representing a unique identifier for a user.

    Note:
    - This class is decorated with @dataclass decorators to enable data immutability.
    """

    id: uuid.UUID = field(init=False, default_factory=uuid.uuid4)


@dataclass(frozen=True)
class UserFollowID:
    """
    A class representing the unique identifier for a user follow.

    Attributes:
    - value (uuid.UUID): The UUID value representing the user follow identifier.

    Note:
    - This class is decorated with @dataclass decorator to enable data immutability.
    """

    value: uuid.UUID


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class UserPersonalData:
    """
    UserPersonalData class represents the personal data of a user.

    Attributes:
    - email (str): The email address of the user.
    - username (Union[str, None]): The username of the user. It can be None if not provided.
    - first_name (Union[str, None]): The first name of the user. It can be None if not provided.
    - last_name (Union[str, None]): The last name of the user. It can be None if not provided.

    Methods:
    - __post_init__(): Validates the email address using the validate_email function from django.core.validators.

    Note:
    - This class is decorated with @dataclass_validate and @dataclass decorators to enable data validation and immutability respectively.
    - The email attribute is required and must be a valid email address.
    """

    email: str
    username: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

    def __post_init__(self):
        validate_email(self.email)


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class UserBasePermissions:
    """
    A class representing the base permissions of a user.

    Attributes:
    - is_staff (bool): Indicates whether the user is a staff member.
    - is_active (bool): Indicates whether the user is active.

    Note:
    - This class is decorated with @dataclass_validate and @dataclass decorators
        to enable data validation and immutability respectively.
    """

    is_staff: bool
    is_active: bool


class UserManagerAutoID(UserManager):
    """A custom UserManager class that automatically generates a UUID for each user."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Creates a superuser with the given username, email, and password.

        The is_staff and is_superuser fields are set to True by default.

        Returns:
        - User Instance: The created superuser.

        Raises:
        - ValueError: If the is_staff field is not True or the is_superuser field is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if id not in extra_fields:
            extra_fields = dict(extra_fields, id=UserID().id)

        return self._create_user(username, email, password, **extra_fields)


# --------------------------------------------------
# User Model
# --------------------------------------------------


class User(AbstractUser, custom_models.ActivityTracking):
    """
    A custom User model that extends the AbstractUser class and includes additional fields and functionality.

    This User class also inherits from the ActivityTracking to track the activity state of user instances.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "User".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "Users".
    - db_table (str): The name of the database table for this model, set to "user".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True, blank=False, null=False)

    objects = UserManagerAutoID()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "user"


class UserFactory:
    """
    A factory class for creating User instances.

    The 'build_entity_with_id' method creates a User entity with the provided parameters and returns it.
    """

    @staticmethod
    def build_entity_with_id(
        password: str,
        personal_data: UserPersonalData,
        base_permissions: UserBasePermissions,
    ) -> User:
        personal_data_dict = asdict(personal_data, skip_empty=True)
        base_permissions_dict = asdict(base_permissions, skip_empty=True)
        password = make_password(password=password)
        return User(
            id=UserID().id,
            **personal_data_dict,
            **base_permissions_dict,
            password=password
        )


# --------------------------------------------------
# UserFollow Model
# --------------------------------------------------


class UserFollow(custom_models.ActivityTracking):
    """
    A model class representing the relationship between users for following and being followed.

    Attributes:
    - id (UUIDField): The unique identifier for the UserFollow instance.
    - follower (ForeignKey): The user who is following another user.
    - following (ForeignKey): The user who is being followed by another user.
    - is_accepted (BooleanField): Flag to indicate whether the follow request is accepted or not.
        Defaults to False.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "UserFollow".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "UserFollows".
    - db_table (str): The name of the database table for this model, set to "user_follow".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    is_accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "UserFollow"
        verbose_name_plural = "UserFollows"
        db_table = "user_follow"


class UserFollowFactory:
    """
    A factory class for creating instances of the UserFollow model.

    This class provides methods for building UserFollow entities with or without an ID.

    Methods:
    - build_entity(id: UserFollowID, follower: User, following: User) -> UserFollow:
        Builds a UserFollow entity with the given ID, follower, and following.

    - build_entity_with_id(follower: User, following: User) -> UserFollow:
        Builds a UserFollow entity with a new UUID-based ID, follower, and following.

    """

    @staticmethod
    def build_entity(
        id: UserFollowID,
        follower: User,
        following: User,
    ) -> UserFollow:
        return UserFollow(
            id=id.value,
            follower=follower,
            following=following,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        follower: User,
        following: User,
    ) -> UserFollow:
        entity_id = UserFollowID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            follower=follower,
            following=following,
        )
